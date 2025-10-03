# 🛒 E-commerce MVP - Microservices Platform

Complete e-commerce platform built with microservices architecture using FastAPI, PostgreSQL, and MongoDB.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                    MICROSERVICES                     │
├─────────────────────────────────────────────────────┤
│                                                      │
│  Auth Service (8001)      → PostgreSQL              │
│  Product Service (8002)   → MongoDB                 │
│  Order Service (8003)     → PostgreSQL              │
│  Payment Service (8004)   → PostgreSQL              │
│  Dashboard Service (8005) → PostgreSQL + MongoDB    │
│                                                      │
└─────────────────────────────────────────────────────┘
```

## 📦 Services

### 1. Auth Service (Port 8001)
- User registration
- User login
- JWT token generation
- User management
- **Database**: PostgreSQL

### 2. Product Service (Port 8002)
- Product CRUD operations
- Category management
- Product search and filtering
- Image handling
- **Database**: MongoDB

### 3. Order Service (Port 8003)
- Shopping cart management
- Order creation
- Order tracking
- Order history
- **Database**: PostgreSQL

### 4. Payment Service (Port 8004)
- Payment processing (fake gateway)
- Payment status tracking
- Refund handling
- **Database**: PostgreSQL

### 5. Dashboard Service (Port 8005)
- Admin dashboard
- User statistics
- Order statistics
- Product statistics
- **Database**: PostgreSQL + MongoDB

## 🚀 Quick Start

### Prerequisites

- Docker Desktop installed
- Docker Compose installed
- 8GB RAM minimum
- Ports 5432, 27017, 6379, 8001-8005 available

### Installation

1. **Clone or navigate to project directory**:
```bash
cd ecommerce-mvp
```

2. **Start all services**:
```bash
docker-compose up --build
```

This single command will:
- Start PostgreSQL database
- Start MongoDB database
- Start Redis cache
- Build and start all 5 microservices
- Initialize databases with sample data

3. **Wait for services to be ready** (approximately 1-2 minutes)

4. **Verify services are running**:
```bash
# Check all services
curl http://localhost:8001/health  # Auth Service
curl http://localhost:8002/health  # Product Service
curl http://localhost:8003/health  # Order Service
curl http://localhost:8004/health  # Payment Service
curl http://localhost:8005/health  # Dashboard Service
```

## 📚 API Documentation

Each service provides interactive Swagger documentation:

- **Auth Service**: http://localhost:8001/docs
- **Product Service**: http://localhost:8002/docs
- **Order Service**: http://localhost:8003/docs
- **Payment Service**: http://localhost:8004/docs
- **Dashboard Service**: http://localhost:8005/docs

## 🧪 Testing the APIs

### 1. Register a User

```bash
curl -X POST http://localhost:8001/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@test.com",
    "username": "testuser",
    "password": "test123",
    "full_name": "Test User"
  }'
```

**Response**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

Save the `access_token` for subsequent requests!

### 2. Login

```bash
curl -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "test123"
  }'
```

### 3. List Products

```bash
curl http://localhost:8002/api/products/
```

### 4. Get Product Details

```bash
curl http://localhost:8002/api/products/{product_id}
```

### 5. Create Order (Authenticated)

```bash
curl -X POST http://localhost:8003/api/orders/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "items": [
      {
        "product_id": "PRODUCT_ID_FROM_STEP_3",
        "quantity": 2
      }
    ],
    "shipping_address": "123 Main St, City, Country"
  }'
```

### 6. Process Payment

```bash
curl -X POST http://localhost:8004/api/payments/process \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "order_id": ORDER_ID_FROM_STEP_5,
    "payment_method": "credit_card",
    "card_number": "4111111111111111",
    "card_holder": "Test User",
    "cvv": "123",
    "expiry": "12/25"
  }'
```

### 7. View Dashboard (Admin Only)

Login as admin first:
```bash
curl -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'
```

Then access dashboard:
```bash
curl http://localhost:8005/api/dashboard/stats \
  -H "Authorization: Bearer ADMIN_TOKEN_HERE"
```

## 🔐 Default Credentials

**Admin User**:
- Username: `admin`
- Password: `admin123`
- Email: `admin@ecommerce.com`

**Test User**:
- Username: `testuser`
- Password: `test123`
- Email: `user@test.com`

## 📊 Database Access

### PostgreSQL

```bash
# Access PostgreSQL
docker exec -it ecommerce_postgres psql -U ecommerce -d ecommerce

# Useful commands:
\dt                    # List tables
SELECT * FROM users;   # View users
SELECT * FROM orders;  # View orders
\q                     # Quit
```

### MongoDB

```bash
# Access MongoDB
docker exec -it ecommerce_mongodb mongosh -u ecommerce -p ecommerce123

# Useful commands:
use ecommerce_products
db.products.find().pretty()
db.products.countDocuments()
exit
```

## 🛠️ Development

### Project Structure

```
ecommerce-mvp/
├── auth-service/
│   ├── app/
│   │   ├── api/
│   │   │   └── auth.py          # Auth endpoints
│   │   ├── core/
│   │   │   ├── database.py      # DB config
│   │   │   └── security.py      # JWT & password
│   │   ├── models/
│   │   │   └── user.py          # User model
│   │   ├── schemas/
│   │   │   └── user.py          # Pydantic schemas
│   │   └── main.py              # FastAPI app
│   ├── Dockerfile
│   └── requirements.txt
│
├── product-service/
│   └── [Similar structure with MongoDB]
│
├── order-service/
│   └── [Similar structure]
│
├── payment-service/
│   └── [Similar structure]
│
├── dashboard-service/
│   └── [Similar structure]
│
├── shared/
│   └── auth.py                  # Shared auth utilities
│
├── scripts/
│   └── init-db.sql              # Database initialization
│
├── docker-compose.yml
└── README.md
```

### Running Services Individually

```bash
# Auth Service only
docker-compose up postgres redis auth-service

# Product Service only
docker-compose up mongodb product-service
```

### Viewing Logs

```bash
# View all logs
docker-compose logs -f

# View specific service
docker-compose logs -f auth-service

# View last 100 lines
docker-compose logs --tail=100 product-service
```

### Stopping Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (⚠️ deletes all data)
docker-compose down -v

# Restart specific service
docker-compose restart auth-service
```

## 🧪 Testing

### Manual Testing with Swagger UI

Visit each service's `/docs` endpoint for interactive API testing:

- http://localhost:8001/docs (Auth)
- http://localhost:8002/docs (Products)
- http://localhost:8003/docs (Orders)
- http://localhost:8004/docs (Payments)
- http://localhost:8005/docs (Dashboard)

### Complete E2E Flow

1. **Register** → Get token
2. **Login** → Verify authentication
3. **Browse Products** → See catalog
4. **Create Order** → Add items to cart
5. **Process Payment** → Complete purchase
6. **View Dashboard** → Check stats (admin)

## 📝 API Endpoints Summary

### Auth Service (8001)
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `GET /api/auth/me` - Get current user
- `GET /api/auth/users` - List users (admin)

### Product Service (8002)
- `GET /api/products/` - List products
- `GET /api/products/{id}` - Get product
- `POST /api/products/` - Create product (admin)
- `PUT /api/products/{id}` - Update product (admin)
- `DELETE /api/products/{id}` - Delete product (admin)
- `GET /api/products/categories/list` - List categories

### Order Service (8003)
- `POST /api/orders/` - Create order
- `GET /api/orders/` - List user orders
- `GET /api/orders/{id}` - Get order details
- `PUT /api/orders/{id}/status` - Update status (admin)

### Payment Service (8004)
- `POST /api/payments/process` - Process payment
- `GET /api/payments/{id}` - Get payment status
- `POST /api/payments/refund` - Refund payment (admin)

### Dashboard Service (8005)
- `GET /api/dashboard/stats` - Get statistics (admin)
- `GET /api/dashboard/users` - User list (admin)
- `GET /api/dashboard/orders` - Order list (admin)
- `GET /api/dashboard/products` - Product list (admin)

## 🔧 Configuration

### Environment Variables

Edit `docker-compose.yml` to change:

- `SECRET_KEY` - JWT secret (MUST change in production!)
- `DATABASE_URL` - PostgreSQL connection
- `MONGODB_URL` - MongoDB connection
- Service ports

### Database Credentials

**PostgreSQL**:
- User: `ecommerce`
- Password: `ecommerce123`
- Database: `ecommerce`

**MongoDB**:
- User: `ecommerce`
- Password: `ecommerce123`
- Database: `ecommerce_products`

## 🚨 Troubleshooting

### Port Already in Use

```bash
# Check what's using the port
lsof -i :8001

# Stop the process
kill -9 <PID>

# Or change port in docker-compose.yml
```

### Database Connection Errors

```bash
# Restart databases
docker-compose restart postgres mongodb

# Check database logs
docker-compose logs postgres
docker-compose logs mongodb
```

### Service Won't Start

```bash
# Rebuild service
docker-compose up --build auth-service

# View detailed logs
docker-compose logs -f auth-service

# Check container status
docker ps -a
```

### Clean Restart

```bash
# Remove everything and start fresh
docker-compose down -v
docker-compose up --build
```

## 📈 Features Implemented

✅ User authentication (JWT)
✅ Product catalog (CRUD)
✅ Shopping cart
✅ Order management
✅ Payment processing (fake gateway)
✅ Admin dashboard
✅ Database migrations
✅ API documentation (Swagger)
✅ Error handling
✅ Logging
✅ Data validation
✅ Docker containerization

## 🎯 Next Steps

To extend this MVP:

1. **Add Frontend**: React/Vue.js application
2. **Real Payment Gateway**: Stripe/PayPal integration
3. **Email Notifications**: Order confirmations
4. **Image Upload**: Product image handling
5. **Search**: Elasticsearch integration
6. **Caching**: Redis caching layer
7. **Tests**: Unit and integration tests
8. **CI/CD**: GitHub Actions pipeline
9. **Monitoring**: Prometheus + Grafana
10. **Deploy**: Kubernetes deployment

## 📞 Support

For issues or questions:

1. Check the logs: `docker-compose logs -f`
2. Verify all services are running: `docker ps`
3. Check database connectivity
4. Review API documentation at `/docs` endpoints

## 📄 License

MIT License - Free for personal and commercial use

---

**Built with ❤️ using FastAPI, PostgreSQL, and MongoDB**

**Ready for production deployment with minimal configuration changes!**
