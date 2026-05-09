import pika
import json
import smtplib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(data):
    smtp_server = "mailhog"
    smtp_port = 1025  

    # Criação da mensagem em formato HTML
    message = MIMEMultipart("alternative")
    message["Subject"] = data.get("subject")
    message["From"] = "sistema@empresa.com"
    message["To"] = data.get("to")

    html_content = f"<html><body>{data.get('body')}</body></html>"
    part = MIMEText(html_content, "html")
    message.attach(part)

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.sendmail(message["From"], message["To"], message.as_string())
            print(f" [x] E-mail enviado para {data.get('to')}")
    except Exception as e:
        print(f" [!] Erro ao enviar e-mail: {e}")

def callback(ch, method, properties, body):
    print(f" [x] Recebido: {body}")
    data = json.loads(body)
    send_email(data)
    ch.basic_ack(delivery_tag=method.delivery_tag)

def start_consumer():
    while True:
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
            channel = connection.channel()

            channel.queue_declare(queue='email_queue', durable=True)
            
            channel.basic_qos(prefetch_count=1)
            channel.basic_consume(queue='email_queue', on_message_callback=callback)

            print(' [*] Aguardando mensagens. Para sair pressione CTRL+C')
            channel.start_consuming()
        except pika.exceptions.AMQPConnectionError:
            print(" [!] RabbitMQ não disponível, tentando novamente em 5 segundos...")
            time.sleep(5)
        except Exception as e:
            print(f" [!] Erro inesperado: {e}")
            break

if __name__ == '__main__':
    start_consumer()