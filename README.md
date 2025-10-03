# 🛒 E-commerce Inteligente com Microserviços

Sistema de e-commerce escalável desenvolvido com arquitetura de microserviços, utilizando Python, Flask, PostgreSQL, MongoDB e Docker.

## 🎯 Objetivos

Demonstrar habilidades em:
- Arquitetura de microserviços
- APIs RESTful
- Bancos de dados relacionais e NoSQL
- Containerização com Docker
- Integração com APIs externas
- Boas práticas de desenvolvimento

## 🏗️ Arquitetura

```
┌─────────────┐
│  API Gateway │
└──────┬──────┘
       │
   ────┼────────────────────────────
   │   │   │    │      │       │
   ▼   ▼   ▼    ▼      ▼       ▼
 Auth User Product Order Payment Notification
Service Service Service Service Service Service
   │   │   │    │      │       │
   ▼   ▼   ▼    ▼      ▼       ▼
 PostgreSQL MongoDB PostgreSQL MongoDB
```

## 📦 Microserviços

### 1. **auth-service** (Porta 5001)
- Autenticação JWT
- Geração e validação de tokens
- Refresh tokens

### 2. **user-service** (Porta 5002)
- CRUD de usuários
- Perfis e endereços
- PostgreSQL

### 3. **product-service** (Porta 5003)
- Catálogo de produtos
- Categorias e estoque
- MongoDB (flexibilidade para atributos dinâmicos)

### 4. **order-service** (Porta 5004)
- Criação e gerenciamento de pedidos
- Status de entrega
- PostgreSQL

### 5. **payment-service** (Porta 5005)
- Integração com Stripe/PayPal
- Processamento de pagamentos
- MongoDB (logs de transações)

### 6. **notification-service** (Porta 5006)
- Envio de e-mails (confirmação, recuperação de senha)
- Webhooks
- Fila de mensagens (RabbitMQ/Celery)

## 🚀 Tecnologias

- **Backend**: Python 3.11, Flask, SQLAlchemy, PyMongo
- **Bancos de Dados**: PostgreSQL, MongoDB
- **Autenticação**: JWT (PyJWT)
- **Containerização**: Docker, Docker Compose
- **API Gateway**: Nginx
- **Mensageria**: RabbitMQ (opcional)
- **Testes**: pytest, unittest
- **Documentação**: Swagger/OpenAPI

## 📁 Estrutura do Projeto

```
ecommerce-microservices/
├── services/
│   ├── auth-service/
│   ├── user-service/
│   ├── product-service/
│   ├── order-service/
│   ├── payment-service/
│   └── notification-service/
├── api-gateway/
├── shared/
│   ├── middleware/
│   └── utils/
├── docker-compose.yml
├── .env.example
└── README.md
```

## 🛠️ Instalação e Execução

### Pré-requisitos
- Docker e Docker Compose instalados
- Python 3.11+
- Git

### 1. Clone o repositório
```bash
git clone https://github.com/seu-usuario/ecommerce-microservices.git
cd ecommerce-microservices
```

### 2. Configure as variáveis de ambiente
```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

### 3. Inicie os serviços
```bash
docker-compose up --build
```

### 4. Acesse a aplicação
- API Gateway: http://localhost:8080
- Swagger Docs: http://localhost:8080/docs

## 🧪 Testes

```bash
# Executar todos os testes
docker-compose run --rm auth-service pytest

# Testes de um serviço específico
cd services/auth-service
pytest tests/
```

## 📚 Documentação da API

Cada microserviço possui documentação Swagger disponível em:
- Auth: http://localhost:5001/docs
- User: http://localhost:5002/docs
- Product: http://localhost:5003/docs
- Order: http://localhost:5004/docs
- Payment: http://localhost:5005/docs

## 🔐 Segurança

- Autenticação JWT com refresh tokens
- Senhas criptografadas com bcrypt
- Validação de entrada com marshmallow
- Rate limiting no API Gateway
- CORS configurado
- Variáveis sensíveis em .env

## 🔄 Fluxo de Pedido

1. Cliente faz login (auth-service)
2. Navega no catálogo (product-service)
3. Adiciona produtos ao carrinho (order-service)
4. Realiza checkout (order-service + payment-service)
5. Pagamento processado (payment-service)
6. Notificação enviada (notification-service)

## 🌐 Integrações Externas

- **Stripe/PayPal**: Processamento de pagamentos
- **SendGrid/SMTP**: Envio de e-mails
- **ViaCEP**: Consulta de endereços (Brasil)

## 📈 Melhorias Futuras

- [ ] Implementar cache com Redis
- [ ] Adicionar mensageria com RabbitMQ
- [ ] Circuit breaker para resiliência
- [ ] Monitoramento com Prometheus/Grafana
- [ ] Blockchain para auditoria de transações
- [ ] Frontend em React
- [ ] Deploy em Kubernetes
- [ ] CI/CD com GitHub Actions

## 👨‍💻 Autor

**Natália Barros**
- GitHub: [@nataliabarros1994](https://github.com/nataliabarros1994)
- LinkedIn: [Seu LinkedIn](https://linkedin.com/in/seu-perfil)

## 📄 Licença

MIT License - veja [LICENSE](LICENSE) para mais detalhes.

---

⭐ Se este projeto foi útil, considere dar uma estrela!
