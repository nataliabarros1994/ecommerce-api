# ⚡ Quick Start Guide

## 🚀 Get Running in 3 Commands

```bash
# 1. Navigate to project
cd ecommerce-mvp

# 2. Start all services
docker-compose up --build

# 3. Test the APIs (in another terminal)
./test_api.sh
```

That's it! Your e-commerce platform is running! 🎉

## 📍 Service URLs

Once running, access:

- **Auth Service**: http://localhost:8001/docs
- **Product Service**: http://localhost:8002/docs
- **Order Service**: http://localhost:8003/docs
- **Payment Service**: http://localhost:8004/docs
- **Dashboard Service**: http://localhost:8005/docs

## 🧪 Quick Test

```bash
# Register a user
curl -X POST http://localhost:8001/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","username":"testuser","password":"test123"}'

# List products
curl http://localhost:8002/api/products/

# View dashboard (admin: admin/admin123)
curl -X POST http://localhost:8001/api/auth/login \
  -d '{"username":"admin","password":"admin123"}' | jq '.access_token'
```

## 📊 Default Data

The system comes with:
- **Admin user**: admin / admin123
- **Test user**: testuser / test123
- **5 sample products** in the catalog

## 🛑 Stop Services

```bash
docker-compose down

# Remove all data
docker-compose down -v
```

## 📖 Full Documentation

See [README.md](README.md) for complete documentation.

## 🔥 Common Issues

**Port already in use?**
```bash
# Change ports in docker-compose.yml
# Or stop the conflicting service
lsof -i :8001
```

**Database error?**
```bash
# Restart databases
docker-compose restart postgres mongodb
```

**Service won't start?**
```bash
# Check logs
docker-compose logs -f auth-service
```

## ✅ Verify Everything Works

```bash
# All services should return "healthy"
curl http://localhost:8001/health
curl http://localhost:8002/health
curl http://localhost:8003/health
curl http://localhost:8004/health
curl http://localhost:8005/health
```

---

**🎓 Next**: Read the full [README.md](README.md) for API details and advanced usage!
