# 🚀 START HERE - GlowShop E-commerce Platform

## ✅ Project Status: READY TO RUN

All microservices have been reviewed, fixed, and verified. Everything is ready to run with Docker!

---

## 📋 Quick Verification Checklist

Before starting, verify you have:

- [x] **All 6 microservices** complete with entry points
  - ✅ auth-service (run.py, Dockerfile, requirements.txt, config.py)
  - ✅ user-service (run.py, Dockerfile, requirements.txt, config.py)
  - ✅ product-service (run.py, Dockerfile, requirements.txt, config.py)
  - ✅ order-service (run.py, Dockerfile, requirements.txt, config.py)
  - ✅ payment-service (run.py, Dockerfile, requirements.txt, config.py)
  - ✅ notification-service (run.py, Dockerfile, requirements.txt, config.py)
- [x] **Docker and Docker Compose** installed
- [x] **.env file** with all configurations
- [x] **docker-compose.yml** configured

---

## 🎯 3-Step Quick Start

### Step 1️⃣: Navigate to Project Directory

```bash
cd "/home/nataliabarros1994/Downloads/E-commerce Inteligente com Microserviços"
```

### Step 2️⃣: Start All Services

```bash
docker-compose up --build -d
```

**What happens:**
- ✅ Builds Docker images for all 6 microservices
- ✅ Creates PostgreSQL and MongoDB databases
- ✅ Starts all containers in the background
- ⏱️ Takes 3-5 minutes on first run

### Step 3️⃣: Verify Everything is Running

```bash
docker-compose ps
```

**Expected output - 8 containers running:**
```
NAME                    STATUS
ecommerce_postgres      Up (healthy)
ecommerce_mongodb       Up (healthy)
auth_service           Up
user_service           Up
product_service        Up
order_service          Up
payment_service        Up
notification_service   Up
```

---

## 🧪 Test the System

### Automated Testing (Recommended)

```bash
./test-api.sh
```

This script will automatically:
1. ✅ Check health of all 6 services
2. ✅ Register a test user and get JWT token
3. ✅ Seed sample products into the database
4. ✅ Create a test order
5. ✅ Process a test payment
6. ✅ Display results and access token

### Manual Health Check

Test each service individually:

```bash
# Test all health endpoints
curl http://localhost:5001/health  # Auth Service
curl http://localhost:5002/health  # User Service
curl http://localhost:5003/health  # Product Service
curl http://localhost:5004/health  # Order Service
curl http://localhost:5005/health  # Payment Service
curl http://localhost:5006/health  # Notification Service
```

**Expected response from each:**
```json
{"status": "healthy", "service": "service-name"}
```

---

## 📊 View Logs

```bash
# View all logs
docker-compose logs -f

# View specific service
docker-compose logs -f auth-service

# View last 50 lines
docker-compose logs --tail=50
```

---

## 🔍 Access Databases

### PostgreSQL (auth, user, order services)

```bash
docker exec -it ecommerce_postgres psql -U ecommerce_user -d ecommerce_db
```

**Useful commands:**
```sql
-- List all tables
\dt

-- View users
SELECT * FROM users;

-- View user profiles
SELECT * FROM user_profiles;

-- View orders
SELECT * FROM orders;

-- View order items
SELECT * FROM order_items;

-- Exit
\q
```

### MongoDB (product, payment services)

```bash
docker exec -it ecommerce_mongodb mongosh -u mongo_user -p mongo_pass --authenticationDatabase admin
```

**Useful commands:**
```javascript
// Use database
use ecommerce_products

// List all products
db.products.find().pretty()

// List all categories
db.categories.find().pretty()

// List all payments
db.payments.find().pretty()

// Count products
db.products.countDocuments()

// Exit
exit
```

---

## 🧑‍💻 API Testing Examples

### 1. Register a New User

```bash
curl -X POST http://localhost:5001/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "SecurePass123"
  }'
```

**Save the `access_token` from the response!**

### 2. Login

```bash
curl -X POST http://localhost:5001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "SecurePass123"
  }'
```

### 3. Seed Sample Products

```bash
curl -X POST http://localhost:5003/api/products/seed
```

**Response:**
```json
{
  "message": "Database seeded successfully",
  "products_count": 5,
  "categories_count": 3
}
```

### 4. List Products

```bash
curl http://localhost:5003/api/products
```

### 5. Create User Profile (requires token)

Replace `YOUR_TOKEN` with your actual access token:

```bash
curl -X POST http://localhost:5002/api/users/profile \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "phone": "+5511999999999",
    "address": "123 Main Street",
    "city": "São Paulo",
    "state": "SP",
    "country": "Brazil",
    "postal_code": "01234-567"
  }'
```

### 6. Create an Order

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
    "shipping_address": "123 Main Street, São Paulo - SP"
  }'
```

### 7. Process Payment

```bash
curl -X POST http://localhost:5005/api/payments \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "order_id": "1",
    "amount": 4599.90,
    "payment_method": "card",
    "currency": "BRL"
  }'
```

---

## 🛑 Stop the System

```bash
# Stop containers (keeps data)
docker-compose down

# Stop and remove all data
docker-compose down -v
```

---

## 🐛 Troubleshooting

### Problem: Containers won't start

**Solution:**
```bash
# Check what's wrong
docker-compose logs

# Rebuild everything
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Problem: Port already in use

**Solution:**
```bash
# Find what's using the port
sudo lsof -i :5001

# Kill the process or change port in .env
```

### Problem: Database connection failed

**Solution:**
```bash
# Wait for databases to be ready
docker-compose ps

# Check database logs
docker-compose logs postgres
docker-compose logs mongodb

# Restart services
docker-compose restart auth-service user-service
```

### Problem: Permission denied (Docker)

**Solution:**
```bash
# Add your user to docker group
sudo usermod -aG docker $USER

# Restart terminal or run
newgrp docker
```

### Problem: Out of memory

**Solution:**
```bash
# Clean up Docker
docker system prune -a

# Increase Docker memory in Docker Desktop settings
# Recommended: 4GB minimum
```

---

## 📁 Project Structure

```
E-commerce Inteligente com Microserviços/
├── services/
│   ├── auth-service/          ✅ Complete
│   ├── user-service/          ✅ Complete
│   ├── product-service/       ✅ Complete
│   ├── order-service/         ✅ Complete
│   ├── payment-service/       ✅ Complete
│   └── notification-service/  ✅ Complete
├── api-gateway/               ✅ Configured
├── docker-compose.yml         ✅ Ready
├── .env                       ✅ Configured
├── test-api.sh               ✅ Automated tests
├── START_HERE.md             ← You are here
├── QUICKSTART_DOCKER.md      📖 Quick start guide
├── TESTING_GUIDE.md          📖 Detailed testing
└── PROJECT_FIXES_SUMMARY.md  📖 All fixes made
```

---

## 🎨 Service Endpoints

| Service | Port | Endpoint | Database |
|---------|------|----------|----------|
| **Auth** | 5001 | http://localhost:5001/api/auth | PostgreSQL |
| **User** | 5002 | http://localhost:5002/api/users | PostgreSQL |
| **Product** | 5003 | http://localhost:5003/api/products | MongoDB |
| **Order** | 5004 | http://localhost:5004/api/orders | PostgreSQL |
| **Payment** | 5005 | http://localhost:5005/api/payments | MongoDB |
| **Notification** | 5006 | http://localhost:5006/api/notifications | None |

---

## 📚 Additional Documentation

- **QUICKSTART_DOCKER.md** - Fast setup guide
- **TESTING_GUIDE.md** - Complete testing guide with all API examples
- **PROJECT_FIXES_SUMMARY.md** - All fixes and improvements made
- **API_REFERENCE.md** - Detailed API documentation
- **ARCHITECTURE.md** - System architecture overview

---

## 🎯 What's Fixed and Ready

✅ **All microservices complete** with entry points
✅ **All dependencies installed** and correct versions
✅ **All Dockerfiles configured** properly
✅ **Database schemas defined** (PostgreSQL + MongoDB)
✅ **JWT authentication** implemented across all services
✅ **Health checks** on all services
✅ **Error handling** and validation
✅ **Docker Compose** orchestration ready
✅ **Automated testing script** included
✅ **Comprehensive documentation** provided

---

## 🚀 Next Steps After Starting

1. ✅ **Run automated tests**: `./test-api.sh`
2. ✅ **Check all services are healthy**
3. ✅ **Test the API endpoints** with the examples above
4. ✅ **Explore the databases** using the commands provided
5. ✅ **Read TESTING_GUIDE.md** for more examples
6. ✅ **Import endpoints** into Postman/Insomnia
7. ✅ **Build your frontend** - All APIs are ready!

---

## ⚡ Performance Tips

```bash
# Monitor resource usage
docker stats

# View specific containers
docker stats auth_service product_service

# Check disk usage
docker system df
```

---

## 🆘 Need Help?

1. **Check logs first**: `docker-compose logs -f`
2. **Verify .env file** has correct values
3. **Ensure ports are free**: 5001-5006, 5432, 27017
4. **Check Docker has resources**: At least 4GB RAM
5. **Read troubleshooting** section above
6. **Review documentation** in the guides

---

## ✨ Summary

Your **GlowShop E-commerce Platform** is:

- ✅ **100% Complete** - All 6 microservices implemented
- ✅ **Tested & Verified** - All entry points and dependencies checked
- ✅ **Production-Ready** - Proper error handling and security
- ✅ **Well-Documented** - Comprehensive guides provided
- ✅ **Easy to Run** - Just `docker-compose up --build -d`

**You're ready to go! Start with Step 1 above. 🎉**

---

**Made with ❤️ using Python, Flask, Docker, PostgreSQL & MongoDB**
