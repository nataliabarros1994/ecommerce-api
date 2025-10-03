# 🏗️ Arquitetura do Sistema

## Visão Geral

Sistema de e-commerce baseado em **arquitetura de microserviços**, onde cada serviço é independente, escalável e possui sua própria responsabilidade.

## Padrões Arquiteturais

### 1. **Microserviços**
Cada serviço é independente e pode ser desenvolvido, deployado e escalado separadamente.

### 2. **API Gateway Pattern**
Nginx como ponto único de entrada, gerenciando:
- Roteamento de requisições
- Rate limiting
- Load balancing
- Headers de segurança

### 3. **Database per Service**
Cada microserviço possui seu próprio banco de dados:
- **PostgreSQL**: Dados relacionais (auth, user, order)
- **MongoDB**: Dados não relacionais (product, payment)

### 4. **JWT Authentication**
Token-based authentication com:
- Access tokens (curta duração - 1h)
- Refresh tokens (longa duração - 30 dias)
- Token revocation

## Fluxo de Comunicação

```
Cliente → API Gateway → Microserviço → Database
```

### Exemplo: Criar Pedido

```
1. Cliente faz login
   POST /api/auth/login → auth-service

2. Cliente lista produtos
   GET /api/products → product-service

3. Cliente cria pedido
   POST /api/orders → order-service
   ↓
   order-service → product-service (verifica estoque)
   ↓
   order-service → payment-service (processa pagamento)
   ↓
   payment-service → notification-service (envia confirmação)
```

## Detalhamento dos Microserviços

### 🔐 Auth Service (Porta 5001)

**Responsabilidade**: Autenticação e autorização

**Endpoints**:
- `POST /api/auth/register` - Registrar novo usuário
- `POST /api/auth/login` - Login
- `POST /api/auth/refresh` - Renovar token
- `POST /api/auth/verify` - Verificar token
- `POST /api/auth/logout` - Logout
- `GET /api/auth/me` - Informações do usuário

**Database**: PostgreSQL
**Tabelas**:
- `users` - Informações de autenticação
- `refresh_tokens` - Tokens de refresh

**Tecnologias**:
- Flask
- SQLAlchemy
- PyJWT
- bcrypt

---

### 👤 User Service (Porta 5002)

**Responsabilidade**: Gerenciamento de perfis de usuário

**Endpoints**:
- `GET /api/users/:id` - Obter perfil
- `PUT /api/users/:id` - Atualizar perfil
- `POST /api/users/:id/addresses` - Adicionar endereço
- `GET /api/users/:id/addresses` - Listar endereços
- `DELETE /api/users/:id/addresses/:address_id` - Remover endereço

**Database**: PostgreSQL
**Tabelas**:
- `user_profiles` - Perfis completos
- `addresses` - Endereços de entrega

---

### 📦 Product Service (Porta 5003)

**Responsabilidade**: Catálogo de produtos

**Endpoints**:
- `GET /api/products` - Listar produtos (paginado)
- `GET /api/products/:id` - Detalhes do produto
- `POST /api/products` - Criar produto (admin)
- `PUT /api/products/:id` - Atualizar produto (admin)
- `DELETE /api/products/:id` - Deletar produto (admin)
- `GET /api/products/categories` - Listar categorias
- `GET /api/products/search?q=termo` - Buscar produtos

**Database**: MongoDB
**Collections**:
- `products` - Catálogo de produtos
- `categories` - Categorias

**Por que MongoDB?**
- Esquema flexível (produtos podem ter atributos diferentes)
- Performance em leituras massivas
- Fácil indexação para busca

---

### 🛒 Order Service (Porta 5004)

**Responsabilidade**: Gerenciamento de pedidos

**Endpoints**:
- `POST /api/orders` - Criar pedido
- `GET /api/orders` - Listar pedidos do usuário
- `GET /api/orders/:id` - Detalhes do pedido
- `PUT /api/orders/:id/status` - Atualizar status (admin)
- `GET /api/orders/:id/tracking` - Rastreamento

**Database**: PostgreSQL
**Tabelas**:
- `orders` - Pedidos
- `order_items` - Itens do pedido
- `order_status_history` - Histórico de status

**Comunicação com outros serviços**:
- `product-service`: Verificar estoque
- `payment-service`: Processar pagamento
- `notification-service`: Enviar confirmação

---

### 💳 Payment Service (Porta 5005)

**Responsabilidade**: Processamento de pagamentos

**Endpoints**:
- `POST /api/payments/process` - Processar pagamento
- `GET /api/payments/:id` - Status do pagamento
- `POST /api/payments/webhook` - Webhook do gateway

**Database**: MongoDB
**Collections**:
- `payments` - Transações
- `payment_logs` - Logs de auditoria

**Integrações**:
- Stripe
- PayPal (opcional)

**Por que MongoDB?**
- Logs de transações podem ter estruturas variadas
- Auditoria completa com documentos aninhados

---

### 📧 Notification Service (Porta 5006)

**Responsabilidade**: Envio de notificações

**Endpoints**:
- `POST /api/notifications/email` - Enviar e-mail
- `GET /api/notifications/:user_id` - Histórico de notificações

**Tipos de notificações**:
- Confirmação de cadastro
- Confirmação de pedido
- Atualização de status
- Recuperação de senha

**Integrações**:
- SMTP (Gmail, SendGrid)
- Templates de e-mail

---

## Segurança

### Autenticação
- JWT com tokens de acesso e refresh
- Tokens armazenados no banco (refresh)
- Revogação de tokens no logout

### Autorização
- Middleware `@token_required`
- Middleware `@admin_required`
- Verificação de permissões por endpoint

### Proteções
- Rate limiting no API Gateway
- CORS configurado
- Headers de segurança (X-Frame-Options, etc.)
- Senhas com bcrypt (salt rounds)
- SQL Injection prevention (SQLAlchemy ORM)
- Input validation (marshmallow)

## Escalabilidade

### Horizontal Scaling
Cada microserviço pode ser escalado independentemente:
```bash
docker-compose up --scale product-service=3
```

### Database Scaling
- PostgreSQL: Read replicas
- MongoDB: Sharding e replica sets

### Caching (Futuro)
- Redis para:
  - Cache de produtos
  - Sessões de usuário
  - Rate limiting

## Monitoramento (Futuro)

### Métricas
- Prometheus para coleta
- Grafana para visualização

### Logs
- Centralização com ELK Stack
- Log levels: INFO, WARNING, ERROR

### Health Checks
Cada serviço possui endpoint `/health`:
```json
{
  "status": "healthy",
  "service": "product-service",
  "database": "connected"
}
```

## Testes

### Tipos de Testes

1. **Testes Unitários**
   - Funções individuais
   - Modelos de dados
   - Utilitários

2. **Testes de Integração**
   - Endpoints da API
   - Comunicação entre serviços
   - Database operations

3. **Testes End-to-End**
   - Fluxos completos (registro → compra)

### Executar Testes
```bash
# Todos os serviços
docker-compose run --rm auth-service pytest

# Serviço específico
cd services/auth-service
pytest tests/ -v --cov=app
```

## Deploy

### Desenvolvimento
```bash
docker-compose up --build
```

### Produção
- Kubernetes para orquestração
- CI/CD com GitHub Actions
- Variáveis de ambiente em secrets

## Próximos Passos

1. ✅ Estrutura base criada
2. ⏳ Implementar demais microserviços
3. ⏳ Adicionar testes
4. ⏳ Implementar frontend React
5. ⏳ Deploy em cloud
6. ⏳ Blockchain para auditoria (opcional)

---

**Desenvolvido por Natália Barros**
