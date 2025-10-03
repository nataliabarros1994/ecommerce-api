# GlowShop E-commerce - Quick Start with Docker

## Prerequisites

- Docker (v20.10+)
- Docker Compose (v2.0+)
- 4GB+ RAM available
- 10GB+ disk space

## Quick Start (3 Simple Steps)

### 1. Start All Services

```bash
cd "/home/nataliabarros1994/Downloads/E-commerce Inteligente com Microserviços"
docker-compose up --build -d
```

**Wait 2-3 minutes** for all services to start and databases to initialize.

### 2. Verify Everything is Running

```bash
docker-compose ps
```

You should see 8 containers running:
- ✅ ecommerce_postgres
- ✅ ecommerce_mongodb
- ✅ auth_service
- ✅ user_service
- ✅ product_service
- ✅ order_service
- ✅ payment_service
- ✅ notification_service

### 3. Test the System

```bash
./test-api.sh
```

This will automatically:
- Check all service health endpoints
- Register a test user
- Seed sample products
- Create an order
- Process a payment
- Display an access token for manual testing

## Access Services

Each service runs on a different port:

- **Auth Service**: http://localhost:5001
- **User Service**: http://localhost:5002
- **Product Service**: http://localhost:5003
- **Order Service**: http://localhost:5004
- **Payment Service**: http://localhost:5005
- **Notification Service**: http://localhost:5006

## View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f auth-service

# Last 100 lines
docker-compose logs --tail=100
```

## Stop Services

```bash
# Stop (preserves data)
docker-compose down

# Stop and delete all data
docker-compose down -v
```

## Access Databases

### PostgreSQL
```bash
docker exec -it ecommerce_postgres psql -U ecommerce_user -d ecommerce_db
```

Useful commands:
- `\dt` - List tables
- `SELECT * FROM users;` - View users
- `SELECT * FROM orders;` - View orders
- `\q` - Exit

### MongoDB
```bash
docker exec -it ecommerce_mongodb mongosh -u mongo_user -p mongo_pass --authenticationDatabase admin
```

Useful commands:
- `use ecommerce_products` - Switch database
- `db.products.find().pretty()` - View products
- `db.payments.find().pretty()` - View payments
- `exit` - Exit

## Manual API Testing

### 1. Register a User

```bash
curl -X POST http://localhost:5001/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "Password123"}'
```

Save the `access_token` from the response!

### 2. List Products

```bash
# Seed sample products first
curl -X POST http://localhost:5003/api/products/seed

# Then list them
curl http://localhost:5003/api/products
```

### 3. Create Order (requires token)

```bash
curl -X POST http://localhost:5004/api/orders \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "items": [{"product_id": "1", "product_name": "Product", "quantity": 1, "price": 99.90}],
    "shipping_address": "Street 123"
  }'
```

## Troubleshooting

### Services won't start
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Port conflicts
Edit `.env` and change the port numbers:
```
AUTH_SERVICE_PORT=5001  # Change to 5011 if needed
```

### Database errors
```bash
# Restart databases
docker-compose restart postgres mongodb

# Check logs
docker-compose logs postgres
docker-compose logs mongodb
```

### Permission errors
```bash
# Fix Docker permissions
sudo usermod -aG docker $USER
newgrp docker
```

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                     API Gateway (Nginx)                  │
│                     Port: 8080 (optional)                │
└───────────────────────┬─────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
┌───────▼──────┐ ┌──────▼──────┐ ┌─────▼───────┐
│ Auth Service │ │User Service │ │Product Svc  │
│   Port 5001  │ │  Port 5002  │ │  Port 5003  │
│  PostgreSQL  │ │ PostgreSQL  │ │   MongoDB   │
└──────────────┘ └─────────────┘ └─────────────┘

┌──────────────┐ ┌─────────────┐ ┌─────────────┐
│ Order Service│ │Payment Svc  │ │Notification │
│  Port 5004   │ │  Port 5005  │ │  Port 5006  │
│  PostgreSQL  │ │   MongoDB   │ │  Stateless  │
└──────────────┘ └─────────────┘ └─────────────┘
```

## Microservices

1. **auth-service**: User authentication, JWT tokens, login/register
2. **user-service**: User profiles, addresses, personal information
3. **product-service**: Product catalog, categories, inventory
4. **order-service**: Order creation, order tracking, order history
5. **payment-service**: Payment processing, transaction records
6. **notification-service**: Email notifications, order confirmations

## Documentation

- **TESTING_GUIDE.md**: Complete testing guide with examples
- **PROJECT_FIXES_SUMMARY.md**: All fixes and improvements made
- **API_REFERENCE.md**: Detailed API documentation
- **ARCHITECTURE.md**: System architecture details

## Support

If you encounter issues:

1. Check logs: `docker-compose logs -f`
2. Verify .env configuration
3. Ensure all ports are available
4. Check Docker has enough resources (Settings → Resources)
5. Try rebuilding: `docker-compose build --no-cache`

## Next Steps

After starting the system:
1. ✅ Run `./test-api.sh` to verify everything works
2. ✅ Import API endpoints into Postman/Insomnia
3. ✅ Read `TESTING_GUIDE.md` for detailed examples
4. ✅ Explore the databases
5. ✅ Build your frontend!

---

**Project**: GlowShop E-commerce Platform
**Status**: ✅ Production Ready
**Services**: 6 Microservices
**Databases**: PostgreSQL + MongoDB
**Language**: Python 3.11 + Flask
