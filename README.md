# 📬 poc_email — Los Bros
Este repositório contém uma prova de conceito de envio de e-mails assíncrono, desenvolvida como estudo prático de sistemas distribuídos. A aplicação demonstra o fluxo completo de disparo de e-mails de forma desacoplada, utilizando **RabbitMQ** como broker de mensagens e **ZooKeeper** para gerenciamento dinâmico de configuração.

---

## 👥 Membros
- **Guilherme Xavier Zanetti**
- **Nuno Kasuo Tronco Yokoji**

---

## 🛠️ Tecnologias Utilizadas

- **Python 3.9 / Flask**: backend da API REST e servidor do frontend
- **RabbitMQ 3**: broker de mensagens com painel de gerenciamento integrado
- **Apache ZooKeeper**: serviço de coordenação e configuração distribuída
- **HTMX**: interações assíncronas no frontend sem JavaScript pesado
- **MailHog**: servidor SMTP fake para captura de e-mails em desenvolvimento
- **Docker / Docker Compose**: containerização e orquestração de todos os serviços
- **NGINX**: load balancer para distribuição de requisições entre múltiplas instâncias

---

## 📋 Índice

- [Parte 1 — Sistema Base](#-parte-1--sistema-base)
- [Parte 2 — Múltiplos Consumers](#-parte-2--múltiplos-consumers)
- [Parte 3 — Load Balancer com NGINX](#-parte-3--load-balancer-com-nginx)
- [Como Utilizar](#-como-utilizar)

---

## 🟢 Parte 1 — Sistema Base

### Características Principais

Fluxo assíncrono de ponta a ponta — do formulário web até a entrega do e-mail:

- **Frontend desacoplado**: interface leve com HTMX, sem frameworks pesados, que se comunica com o backend via requisições assíncronas
- **Mensageria com RabbitMQ**: o backend publica as mensagens em uma fila durável, garantindo que nenhum e-mail seja perdido mesmo em caso de falha temporária do consumer
- **Configuração dinâmica com ZooKeeper**: o backend consulta o ZooKeeper para obter host e nome da fila em tempo de execução, com fallback automático para valores padrão
- **Consumer resiliente**: o serviço consumidor reconecta automaticamente ao RabbitMQ em caso de falha de conexão
- **Ambiente de testes com MailHog**: todos os e-mails são capturados localmente, sem risco de envio real durante o desenvolvimento

### ⚙️ Arquitetura

```
Frontend (Flask) → Backend API (Flask) → RabbitMQ → Consumer → MailHog
                          ↕
                      ZooKeeper
                  (config dinâmica)
```

| Serviço    | Tecnologia               | Porta        | Responsabilidade                          |
|------------|--------------------------|--------------|-------------------------------------------|
| `frontend` | Flask + HTMX             | 8080         | Interface web para composição do e-mail   |
| `backend`  | Flask + Pika + Kazoo     | 5000         | API REST que publica mensagens na fila    |
| `consumer` | Python + Pika + smtplib  | —            | Consome a fila e realiza o envio SMTP     |
| `rabbitmq` | RabbitMQ 3 (management)  | 5672 / 15672 | Broker de mensagens com fila durável      |
| `zoo`      | Apache ZooKeeper         | 2181         | Fornece configuração dinâmica ao backend  |
| `mailhog`  | MailHog                  | 1025 / 8025  | Servidor SMTP fake para testes locais     |

### 📁 Estrutura do Projeto

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
│   │   └── index.html
│   ├── static/
│   │   ├── style.css
│   │   └── script.js
│   ├── requirements.txt
│   └── Dockerfile
└── docker-compose.yml
```

---

## 🔵 Parte 2 — Múltiplos Consumers

### O que mudou

Adicionado suporte a múltiplas instâncias do serviço `consumer` rodando em paralelo, permitindo o processamento concorrente de mensagens da fila do RabbitMQ.

O `docker-compose.yml` foi atualizado para usar `deploy.replicas: 3` no serviço `consumer`, subindo 3 instâncias automaticamente. O `container_name` foi removido pois nomes fixos impedem múltiplas instâncias. O `depends_on` foi convertido para o formato de mapping (objeto), obrigatório ao usar `replicas`.

### Por que funciona sem alterar o código do consumer

O consumer já estava implementado corretamente para escalonamento horizontal:
- `basic_qos(prefetch_count=1)` — cada consumer processa uma mensagem por vez
- `basic_ack` manual — garante que mensagens não processadas voltam para a fila em caso de falha
- Reconexão automática ao RabbitMQ em caso de queda

### ⚙️ Arquitetura

```
Frontend (Flask) → Backend API (Flask) → RabbitMQ → Consumer 1 ─┐
                          ↕                        → Consumer 2 ─┼→ MailHog
                      ZooKeeper                    → Consumer 3 ─┘
```

---

## 🔴 Parte 3 — Load Balancer com NGINX

### O que mudou

Adicionado um load balancer **NGINX** na frente do frontend e do backend, com 3 instâncias de cada serviço rodando simultaneamente e sendo acessadas pelo mesmo endereço.

O `docker-compose.yml` foi atualizado para usar `deploy.replicas: 3` no `frontend` e no `backend`, com `container_name` removido em ambos. Um novo serviço `nginx` foi adicionado, expondo as portas `8080` (frontend) e `5000` (backend) e carregando a configuração via volume.

Foi criada a pasta `nginx/` com o arquivo `nginx.conf`, que define dois upstream pools — um para o frontend e outro para o backend — e distribui as requisições entre as instâncias usando round-robin.

O `frontend/app.py` teve sua `BACKEND_URL` atualizada para apontar ao NGINX internamente, que então balanceia para as instâncias do backend.

### ⚙️ Arquitetura

```
                      ┌─ Frontend 1 ─┐
Usuário → NGINX:8080 ─┼─ Frontend 2 ─┼→ NGINX:5000 ─┬─ Backend 1 ─┐
                      └─ Frontend 3 ─┘               ├─ Backend 2 ─┼→ RabbitMQ → Consumers → MailHog
                                                      └─ Backend 3 ─┘
                                    ↕
                                ZooKeeper
```

### 📁 Estrutura do Projeto

```
poc_email/
├── backend/
│   ├── app.py
│   ├── requirements.txt
│   └── Dockerfile
├── consumer/
│   ├── main.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── app.py
│   ├── templates/
│   │   └── index.html
│   ├── static/
│   │   ├── style.css
│   │   └── script.js
│   ├── requirements.txt
│   └── Dockerfile
├── nginx/
│   └── nginx.conf          # Configuração do load balancer
└── docker-compose.yml
```

---

## 🚀 Como Utilizar

### Pré-requisitos
- Docker Desktop instalado e em execução
- Docker Compose v2+

### Subindo o projeto

1. **Clone o repositório:**
    ```bash
    git clone https://github.com/NunoYokoji/poc_email.git
    cd poc_email
    ```

2. **Suba todos os serviços:**
    ```bash
    docker compose up --build
    ```

3. **Verifique as instâncias rodando:**
    ```bash
    docker compose ps
    ```
    Você verá `frontend-1/2/3`, `backend-1/2/3` e `consumer-1/2/3` todos com status `running`.

### Acessando as interfaces

| Interface                  | URL                       |
|----------------------------|---------------------------|
| Frontend (via NGINX)       | http://localhost:8080     |
| RabbitMQ Dashboard         | http://localhost:15672    |
| MailHog (caixa de entrada) | http://localhost:8025     |

> Credenciais padrão do RabbitMQ: `guest` / `guest`

### Enviando um e-mail

- Acesse `http://localhost:8080`
- Preencha o destinatário, assunto e corpo da mensagem
- Clique em **Enviar Email**
- Acompanhe o e-mail chegando na caixa do MailHog em `http://localhost:8025`

### Verificando o balanceamento e os consumers

No RabbitMQ Dashboard (`http://localhost:15672`) → **Queues** → `email_queue` → aba **Consumers**: os 3 consumers aparecerão listados processando as mensagens distribuídas pelo RabbitMQ.

Para acompanhar os logs em tempo real:
```bash
docker compose logs -f consumer
```
