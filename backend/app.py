from flask import Flask, request, jsonify
from kazoo.client import KazooClient
import pika
import json
import logging

app = Flask(__name__)

RABBITMQ_HOST = "rabbitmq"
QUEUE_NAME = "email_queue"

def get_config_from_zookeeper():
    
    try:
        
        zk = KazooClient(hosts='zoo:2181', timeout=5)
        zk.start()
        
        if zk.exists("/config/rabbitmq"):
            data, stat = zk.get("/config/rabbitmq")
            config = json.loads(data.decode("utf-8"))
            zk.stop()
            return config.get("host"), config.get("queue")
        
        zk.stop()
    except Exception as e:
        print(f"Erro ao acessar ZooKeeper, usando fallback: {e}")
    
    return RABBITMQ_HOST, QUEUE_NAME

@app.route('/send', methods=['POST'])
def send_email():
    data = request.get_json()
    
    if not data or 'to' not in data or 'subject' not in data or 'body' not in data:
        return jsonify({"error": "Dados incompletos"}), 400

    
    host, queue = get_config_from_zookeeper()

    try:
    
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=host))
        channel = connection.channel()
        
        channel.queue_declare(queue=queue, durable=True)

        channel.basic_publish(
            exchange='',
            routing_key=queue,
            body=json.dumps(data),
            properties=pika.BasicProperties(delivery_mode=2) # Mensagem persistente
        )
        connection.close()
        return jsonify({"status": "Mensagem enviada para a fila!"}), 200

    except Exception as e:
        return jsonify({"error": f"Falha ao conectar ao RabbitMQ: {e}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)