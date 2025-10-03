# 📖 Referência da API

Base URL: `http://localhost:8080`

## 🔐 Autenticação

Todos os endpoints protegidos requerem o header:
```
Authorization: Bearer {access_token}
```

---

## 🔑 Auth Service

### POST /api/auth/register
Registrar novo usuário

**Request:**
```json
{
  "email": "usuario@example.com",
  "password": "senha123"
}
```

**Response:** `201 Created`
```json
{
  "message": "User registered successfully",
  "user": {
    "id": 1,
    "email": "usuario@example.com",
    "is_active": true,
    "is_admin": false,
    "created_at": "2025-01-01T12:00:00",
    "updated_at": "2025-01-01T12:00:00"
  },
  "tokens": {
    "access_token": "eyJ...",
    "refresh_token": "eyJ...",
    "token_type": "Bearer",
    "expires_in": 3600
  }
}
```

**Errors:**
- `400` - Email and password are required
- `409` - Email already registered

---

### POST /api/auth/login
Fazer login

**Request:**
```json
{
  "email": "usuario@example.com",
  "password": "senha123"
}
```

**Response:** `200 OK`
```json
{
  "message": "Login successful",
  "user": { ... },
  "tokens": { ... }
}
```

**Errors:**
- `400` - Email and password are required
- `401` - Invalid credentials
- `403` - Account is inactive

---

### POST /api/auth/refresh
Renovar access token

**Request:**
```json
{
  "refresh_token": "eyJ..."
}
```

**Response:** `200 OK`
```json
{
  "message": "Token refreshed successfully",
  "tokens": {
    "access_token": "eyJ...",
    "refresh_token": "eyJ...",
    "token_type": "Bearer",
    "expires_in": 3600
  }
}
```

**Errors:**
- `400` - Refresh token is required
- `401` - Invalid or expired refresh token

---

### POST /api/auth/verify
Verificar validade do token

**Request:**
```json
{
  "token": "eyJ..."
}
```

**Response:** `200 OK`
```json
{
  "valid": true,
  "user_id": 1,
  "email": "usuario@example.com",
  "is_admin": false
}
```

---

### POST /api/auth/logout
Fazer logout (revoga todos os refresh tokens)

**Headers:** `Authorization: Bearer {access_token}`

**Response:** `200 OK`
```json
{
  "message": "Logged out successfully"
}
```

---

### GET /api/auth/me
Obter informações do usuário atual

**Headers:** `Authorization: Bearer {access_token}`

**Response:** `200 OK`
```json
{
  "id": 1,
  "email": "usuario@example.com",
  "is_active": true,
  "is_admin": false,
  "created_at": "2025-01-01T12:00:00",
  "updated_at": "2025-01-01T12:00:00"
}
```

---

## 📦 Product Service

### GET /api/products
Listar produtos com paginação e filtros

**Query Parameters:**
- `page` (int) - Número da página (default: 1)
- `per_page` (int) - Itens por página (default: 20, max: 100)
- `category` (string) - Filtrar por categoria
- `search` (string) - Buscar em nome e descrição
- `min_price` (float) - Preço mínimo
- `max_price` (float) - Preço máximo
- `sort` (string) - Campo para ordenar (price, name, created_at)
- `order` (string) - Ordem (asc, desc)

**Example:**
```
GET /api/products?page=1&per_page=10&category=electronics&search=notebook&min_price=1000&sort=price&order=asc
```

**Response:** `200 OK`
```json
{
  "products": [
    {
      "id": "507f1f77bcf86cd799439011",
      "name": "Notebook Dell Inspiron",
      "description": "Notebook com processador Intel Core i7...",
      "price": 4599.90,
      "stock": 15,
      "category": "electronics",
      "images": ["notebook-dell-1.jpg"],
      "attributes": {
        "brand": "Dell",
        "color": "Silver",
        "processor": "Intel Core i7"
      },
      "is_active": true,
      "created_at": "2025-01-01T12:00:00",
      "updated_at": "2025-01-01T12:00:00"
    }
  ],
  "pagination": {
    "total": 100,
    "page": 1,
    "per_page": 10,
    "pages": 10
  }
}
```

---

### GET /api/products/:id
Obter detalhes de um produto

**Response:** `200 OK`
```json
{
  "id": "507f1f77bcf86cd799439011",
  "name": "Notebook Dell Inspiron",
  "description": "Notebook com processador Intel Core i7...",
  "price": 4599.90,
  "stock": 15,
  "category": "electronics",
  "images": ["notebook-dell-1.jpg"],
  "attributes": {
    "brand": "Dell",
    "color": "Silver",
    "processor": "Intel Core i7"
  },
  "is_active": true,
  "created_at": "2025-01-01T12:00:00",
  "updated_at": "2025-01-01T12:00:00"
}
```

**Errors:**
- `404` - Product not found

---

### POST /api/products
Criar novo produto (admin only)

**Headers:** `Authorization: Bearer {access_token}` (admin)

**Request:**
```json
{
  "name": "Produto Novo",
  "description": "Descrição do produto",
  "price": 99.90,
  "stock": 100,
  "category": "electronics",
  "images": ["image1.jpg", "image2.jpg"],
  "attributes": {
    "brand": "Marca",
    "color": "Black"
  }
}
```

**Response:** `201 Created`
```json
{
  "message": "Product created successfully",
  "product": { ... }
}
```

**Errors:**
- `400` - Validation errors
- `403` - Admin privileges required

---

### PUT /api/products/:id
Atualizar produto (admin only)

**Headers:** `Authorization: Bearer {access_token}` (admin)

**Request:**
```json
{
  "price": 89.90,
  "stock": 150
}
```

**Response:** `200 OK`
```json
{
  "message": "Product updated successfully",
  "product": { ... }
}
```

**Errors:**
- `400` - Validation errors
- `403` - Admin privileges required
- `404` - Product not found

---

### DELETE /api/products/:id
Deletar produto (soft delete, admin only)

**Headers:** `Authorization: Bearer {access_token}` (admin)

**Response:** `200 OK`
```json
{
  "message": "Product deleted successfully"
}
```

**Errors:**
- `403` - Admin privileges required
- `404` - Product not found

---

### GET /api/products/categories
Listar todas as categorias

**Response:** `200 OK`
```json
{
  "categories": [
    {
      "id": "507f1f77bcf86cd799439011",
      "name": "Electronics",
      "slug": "electronics",
      "description": "Electronic devices and gadgets",
      "parent_id": null,
      "is_active": true,
      "created_at": "2025-01-01T12:00:00"
    }
  ]
}
```

---

### POST /api/products/categories
Criar nova categoria (admin only)

**Headers:** `Authorization: Bearer {access_token}` (admin)

**Request:**
```json
{
  "name": "Nova Categoria",
  "slug": "nova-categoria",
  "description": "Descrição da categoria",
  "parent_id": null
}
```

**Response:** `201 Created`
```json
{
  "message": "Category created successfully",
  "category": { ... }
}
```

---

### POST /api/products/seed
Popular banco de dados com produtos de exemplo

**Response:** `201 Created`
```json
{
  "message": "Database seeded successfully",
  "products_count": 5,
  "categories_count": 3
}
```

---

## 👤 User Service (A Implementar)

### GET /api/users/:id
Obter perfil do usuário

### PUT /api/users/:id
Atualizar perfil

### POST /api/users/:id/addresses
Adicionar endereço

### GET /api/users/:id/addresses
Listar endereços

### DELETE /api/users/:id/addresses/:address_id
Remover endereço

---

## 🛒 Order Service (A Implementar)

### POST /api/orders
Criar novo pedido

### GET /api/orders
Listar pedidos do usuário

### GET /api/orders/:id
Detalhes do pedido

### PUT /api/orders/:id/status
Atualizar status (admin)

### GET /api/orders/:id/tracking
Rastreamento do pedido

---

## 💳 Payment Service (A Implementar)

### POST /api/payments/process
Processar pagamento

### GET /api/payments/:id
Status do pagamento

### POST /api/payments/webhook
Webhook do gateway de pagamento

---

## 📧 Notification Service (A Implementar)

### POST /api/notifications/email
Enviar e-mail

### GET /api/notifications/:user_id
Histórico de notificações

---

## 🔧 Health Checks

Cada serviço possui um endpoint de health check:

- `GET /health` - Status do serviço

**Response:** `200 OK`
```json
{
  "status": "healthy",
  "service": "service-name",
  "database": "connected"
}
```

---

## 📊 Códigos de Status HTTP

- `200 OK` - Requisição bem-sucedida
- `201 Created` - Recurso criado com sucesso
- `400 Bad Request` - Erro de validação ou parâmetros inválidos
- `401 Unauthorized` - Token ausente ou inválido
- `403 Forbidden` - Sem permissão para acessar o recurso
- `404 Not Found` - Recurso não encontrado
- `409 Conflict` - Conflito (ex: email já registrado)
- `500 Internal Server Error` - Erro interno do servidor

---

## 🧪 Exemplos com cURL

### Registrar e fazer login
```bash
# Registrar
curl -X POST http://localhost:8080/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"senha123"}'

# Login
curl -X POST http://localhost:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"senha123"}'
```

### Listar produtos
```bash
curl -X GET "http://localhost:8080/api/products?page=1&per_page=10"
```

### Criar produto (admin)
```bash
curl -X POST http://localhost:8080/api/products \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -d '{
    "name": "Novo Produto",
    "price": 99.90,
    "stock": 50,
    "category": "electronics"
  }'
```

### Popular banco de dados
```bash
curl -X POST http://localhost:8080/api/products/seed
```

---

## 📝 Notas

1. **Tokens JWT**: Access tokens expiram em 1 hora. Use o refresh token para obter um novo.
2. **Rate Limiting**: 10 requisições por segundo por IP no API Gateway.
3. **Paginação**: Máximo de 100 itens por página.
4. **Admin**: Para testar endpoints admin, crie um usuário e modifique manualmente o campo `is_admin` no banco.

---

**Para mais informações, consulte a documentação completa no README.md**
