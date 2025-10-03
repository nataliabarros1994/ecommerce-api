# GlowShop E-commerce - Testing Guide

## Prerequisites

Before running the project, ensure you have:
- **Docker** installed (version 20.10 or higher)
- **Docker Compose** installed (version 2.0 or higher)
- At least **4GB of free RAM**
- **10GB of free disk space**

## Project Structure

```
E-commerce Inteligente com Microserviços/
├── services/
│   ├── auth-service/          # Authentication & JWT tokens
│   ├── user-service/          # User profile management
│   ├── product-service/       # Product catalog (MongoDB)
│   ├── order-service/         # Order processing
│   ├── payment-service/       # Payment processing (MongoDB)
│   └── notification-service/  # Email notifications
├── api-gateway/               # Nginx reverse proxy
├── docker-compose.yml         # Docker orchestration
└── .env                       # Environment variables
```

## Step 1: Verify Environment Configuration

Check that your `.env` file exists and has proper configuration:

```bash
cat .env
```

The file should contain all necessary environment variables for:
- PostgreSQL (auth, user, order services)
- MongoDB (product, payment services)
- JWT secret keys
- Service ports

## Step 2: Start the Application

### Option 1: Using docker-compose (recommended)

```bash
cd "/home/nataliabarros1994/Downloads/E-commerce Inteligente com Microserviços"
docker-compose up --build -d
```

### Option 2: Using newer docker compose (without hyphen)

```bash
docker compose up --build -d
```

**Expected output:**
- Building images for all services
- Creating network and volumes
- Starting containers in dependency order

This process may take 5-10 minutes on first run.

## Step 3: Verify All Containers Are Running

```bash
docker-compose ps
```

You should see **8 containers running**:
1. `ecommerce_postgres` - PostgreSQL database
2. `ecommerce_mongodb` - MongoDB database
3. `auth_service` - Authentication service (port 5001)
4. `user_service` - User service (port 5002)
5. `product_service` - Product service (port 5003)
6. `order_service` - Order service (port 5004)
7. `payment_service` - Payment service (port 5005)
8. `notification_service` - Notification service (port 5006)

## Step 4: Check Service Health

Test each service's health endpoint:

```bash
# Auth Service
curl http://localhost:5001/health

# User Service
curl http://localhost:5002/health

# Product Service
curl http://localhost:5003/health

# Order Service
curl http://localhost:5004/health

# Payment Service
curl http://localhost:5005/health

# Notification Service
curl http://localhost:5006/health
```

Each should return:
```json
{"status":"healthy","service":"<service-name>"}
```

## Step 5: View Logs

Check logs for any errors:

```bash
# View all logs
docker-compose logs

# View specific service logs
docker-compose logs auth-service
docker-compose logs product-service

# Follow logs in real-time
docker-compose logs -f
```

## Step 6: Test the API

### 6.1 Register a New User

```bash
curl -X POST http://localhost:5001/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test123456"
  }'
```

**Expected Response:**
```json
{
  "message": "User registered successfully",
  "user": {
    "id": 1,
    "email": "test@example.com",
    "is_active": true,
    "is_admin": false
  },
  "tokens": {
    "access_token": "eyJ...",
    "refresh_token": "eyJ...",
    "token_type": "Bearer",
    "expires_in": 3600
  }
}
```

**Save the `access_token` for subsequent requests!**

### 6.2 Login

```bash
curl -X POST http://localhost:5001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test123456"
  }'
```

### 6.3 Seed Sample Products

```bash
curl -X POST http://localhost:5003/api/products/seed
```

**Expected Response:**
```json
{
  "message": "Database seeded successfully",
  "products_count": 5,
  "categories_count": 3
}
```

### 6.4 List Products

```bash
curl http://localhost:5003/api/products
```

### 6.5 Create User Profile

Replace `YOUR_TOKEN` with the access token from registration:

```bash
curl -X POST http://localhost:5002/api/users/profile \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "phone": "+5511999999999",
    "address": "Rua Exemplo, 123",
    "city": "São Paulo",
    "state": "SP",
    "country": "Brazil",
    "postal_code": "01234-567"
  }'
```

### 6.6 Create an Order

```bash
curl -X POST http://localhost:5004/api/orders \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "items": [
      {
        "product_id": "1",
        "product_name": "Notebook Dell Inspiron",
        "quantity": 1,
        "price": 4599.90
      }
    ],
    "shipping_address": "Rua Exemplo, 123, São Paulo - SP"
  }'
```

### 6.7 Process Payment

```bash
curl -X POST http://localhost:5005/api/payments \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "order_id": "1",
    "amount": 4599.90,
    "payment_method": "card"
  }'
```

## Step 7: Database Access

### PostgreSQL

```bash
docker exec -it ecommerce_postgres psql -U ecommerce_user -d ecommerce_db
```

Useful commands:
```sql
-- List all tables
\dt

-- View users
SELECT * FROM users;

-- View orders
SELECT * FROM orders;

-- Exit
\q
```

### MongoDB

```bash
docker exec -it ecommerce_mongodb mongosh -u mongo_user -p mongo_pass --authenticationDatabase admin
```

Useful commands:
```javascript
// Show databases
show dbs

// Use database
use ecommerce_products

// Show collections
show collections

// View products
db.products.find().pretty()

// View payments
db.payments.find().pretty()

// Exit
exit
```

## Step 8: Stop the Application

```bash
# Stop containers
docker-compose down

# Stop and remove volumes (WARNING: deletes all data)
docker-compose down -v
```

## Troubleshooting

### Problem: Containers won't start

**Solution:**
```bash
# Check logs
docker-compose logs

# Rebuild images
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Problem: Port already in use

**Solution:**
```bash
# Find process using port
sudo lsof -i :5001

# Kill the process or change port in .env file
```

### Problem: Database connection errors

**Solution:**
```bash
# Wait for databases to be healthy
docker-compose ps

# Check database logs
docker-compose logs postgres
docker-compose logs mongodb

# Restart services
docker-compose restart auth-service
```

### Problem: Permission denied for Docker

**Solution:**
```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Log out and log back in, or run:
newgrp docker
```

### Problem: Out of memory

**Solution:**
```bash
# Prune unused Docker resources
docker system prune -a

# Increase Docker memory limit in Docker Desktop settings
```

## API Testing with Postman/Insomnia

Import the following endpoints:

### Base URLs
- Auth Service: `http://localhost:5001`
- User Service: `http://localhost:5002`
- Product Service: `http://localhost:5003`
- Order Service: `http://localhost:5004`
- Payment Service: `http://localhost:5005`
- Notification Service: `http://localhost:5006`

### Authentication Flow
1. POST `/api/auth/register` - Create account
2. POST `/api/auth/login` - Get tokens
3. Use `Bearer {access_token}` in Authorization header
4. POST `/api/auth/refresh` - Refresh expired token

### Product Flow
1. POST `/api/products/seed` - Seed sample data
2. GET `/api/products` - List products
3. GET `/api/products/{id}` - Get product details

### Order Flow
1. POST `/api/orders` - Create order
2. GET `/api/orders` - List user orders
3. GET `/api/orders/{id}` - Get order details
4. PUT `/api/orders/{id}/status` - Update status
5. DELETE `/api/orders/{id}` - Cancel order

### Payment Flow
1. POST `/api/payments` - Process payment
2. GET `/api/payments/{id}` - Get payment details
3. GET `/api/payments/order/{order_id}` - Get payment by order

## Performance Monitoring

```bash
# Monitor resource usage
docker stats

# View specific container stats
docker stats auth_service product_service
```

## Next Steps

- Set up API Gateway (Nginx) for unified endpoint
- Configure CI/CD pipeline
- Add monitoring (Prometheus + Grafana)
- Implement message queue (RabbitMQ)
- Add caching layer (Redis)
- Set up automated testing

## Support

If you encounter issues:
1. Check the logs: `docker-compose logs -f`
2. Verify environment variables in `.env`
3. Ensure all ports are available
4. Check Docker has enough resources

---

**Project:** GlowShop E-commerce Platform
**Architecture:** Microservices with Docker
**Databases:** PostgreSQL + MongoDB
**Language:** Python 3.11 with Flask
