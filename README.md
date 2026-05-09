# 📬 poc_email — Los Bros
Este repositório contém uma prova de conceito de envio de e-mails assíncrono, desenvolvida como estudo prático de sistemas distribuídos. A aplicação demonstra o fluxo completo de disparo de e-mails de forma desacoplada, utilizando **RabbitMQ** como broker de mensagens e **ZooKeeper** para gerenciamento dinâmico de configuração.

---

## 👥 Membros
- **Guilherme Xavier Zanetti**
- **Nuno Kasuo Tronco Yokoji**

---

## :bulb: Características Principais

Fluxo assíncrono de ponta a ponta — do formulário web até a entrega do e-mail:

- **Frontend desacoplado**: interface leve com HTMX, sem frameworks pesados, que se comunica com o backend via requisições assíncronas
- **Mensageria com RabbitMQ**: o backend publica as mensagens em uma fila durável, garantindo que nenhum e-mail seja perdido mesmo em caso de falha temporária do consumer
- **Configuração dinâmica com ZooKeeper**: o backend consulta o ZooKeeper para obter host e nome da fila em tempo de execução, com fallback automático para valores padrão
- **Consumer resiliente**: o serviço consumidor reconecta automaticamente ao RabbitMQ em caso de falha de conexão
- **Ambiente de testes com MailHog**: todos os e-mails são capturados localmente, sem risco de envio real durante o desenvolvimento

## 🛠️ Tecnologias Utilizadas

- **Python 3.9 / Flask**: backend da API REST e servidor do frontend
- **RabbitMQ 3**: broker de mensagens com painel de gerenciamento integrado
- **Apache ZooKeeper**: serviço de coordenação e configuração distribuída
- **HTMX**: interações assíncronas no frontend sem JavaScript pesado
- **MailHog**: servidor SMTP fake para captura de e-mails em desenvolvimento
- **Docker / Docker Compose**: containerização e orquestração de todos os serviços

## :gear: Arquitetura de Software

```
Frontend (HTMX) → Backend API (Flask) → RabbitMQ → Consumer → MailHog
                          ↕
                      ZooKeeper
                  (config dinâmica)
```

| Serviço    | Tecnologia               | Responsabilidade                          |
|------------|--------------------------|-------------------------------------------|
| `frontend` | Flask + HTMX             | Interface web para composição do e-mail   |
| `backend`  | Flask + Pika + Kazoo     | API REST que publica mensagens na fila    |
| `consumer` | Python + Pika            | Consome a fila e realiza o envio SMTP     |
| `rabbitmq` | RabbitMQ 3 (management)  | Broker de mensagens com fila durável      |
| `zoo`      | Apache ZooKeeper         | Fornece configuração dinâmica ao backend  |
| `mailhog`  | MailHog                  | Servidor SMTP fake para testes locais     |

## 📁 Estrutura do Projeto

```
poc_email/
├── backend/
│   ├── app.py              # API Flask: recebe requests e publica no RabbitMQ
│   ├── requirements.txt
│   └── Dockerfile
├── consumer/
│   ├── main.py             # Consome a fila e envia e-mails via SMTP
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── app.py              # Serve o formulário HTML
│   ├── templates/
│   │   ├── index.html      # UI com HTMX
│   │   ├── style.css
│   │   └── script.js
│   ├── requirements.txt
│   └── Dockerfile
└── docker-compose.yml
```

## 🚀 Como Utilizar

1. **Clone o repositório:**
    ```bash
    git clone https://github.com/seu-usuario/poc_email.git
    cd poc_email
    ```

2. **Suba todos os serviços:**
    ```bash
    docker compose up --build
    ```

3. **Acesse as interfaces:**

    | Interface                  | URL                       |
    |----------------------------|---------------------------|
    | Frontend (app)             | http://localhost:8080     |
    | RabbitMQ Dashboard         | http://localhost:15672    |
    | MailHog (caixa de entrada) | http://localhost:8025     |

    > Credenciais padrão do RabbitMQ: `guest` / `guest`

4. **Envie um e-mail:**
    - Preencha o destinatário e o corpo da mensagem no formulário
    - Clique em **Enviar Email**
    - Acompanhe o e-mail chegando na caixa do MailHog em `http://localhost:8025`

