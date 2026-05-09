from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__, static_folder='static')

BACKEND_URL = "http://backend_api:5000"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/send-email', methods=['POST'])
def send_email():
    data = request.form
    recipient = data.get('recipient')
    subject = data.get('subject')
    body = data.get('body')

    if not recipient or not subject or not body:
        return jsonify({"error": "Dados incompletos"}), 400

    try:
        response = requests.post(
            f"{BACKEND_URL}/send",
            json={"to": recipient, "subject": subject, "body": body},
            timeout=10
        )
        return response.text, response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Falha ao conectar ao servidor: {e}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
