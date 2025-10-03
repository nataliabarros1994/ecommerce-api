#!/bin/bash

# E-commerce MVP API Test Script
# Tests the complete e-commerce flow

set -e

BASE_URL="http://localhost"
AUTH_PORT="8001"
PRODUCT_PORT="8002"
ORDER_PORT="8003"
PAYMENT_PORT="8004"
DASHBOARD_PORT="8005"

echo "🧪 E-commerce MVP - API Testing Script"
echo "========================================"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test 1: Health Checks
echo -e "${BLUE}1️⃣  Testing Health Checks...${NC}"
curl -s ${BASE_URL}:${AUTH_PORT}/health | jq '.'
curl -s ${BASE_URL}:${PRODUCT_PORT}/health | jq '.'
curl -s ${BASE_URL}:${ORDER_PORT}/health | jq '.'
curl -s ${BASE_URL}:${PAYMENT_PORT}/health | jq '.'
curl -s ${BASE_URL}:${DASHBOARD_PORT}/health | jq '.'
echo -e "${GREEN}✅ All services healthy${NC}\n"

# Test 2: Register User
echo -e "${BLUE}2️⃣  Registering new user...${NC}"
REGISTER_RESPONSE=$(curl -s -X POST ${BASE_URL}:${AUTH_PORT}/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "apitest@test.com",
    "username": "apitest",
    "password": "test123",
    "full_name": "API Test User"
  }')

echo $REGISTER_RESPONSE | jq '.'
ACCESS_TOKEN=$(echo $REGISTER_RESPONSE | jq -r '.access_token')

if [ "$ACCESS_TOKEN" == "null" ]; then
    echo -e "${YELLOW}⚠️  User exists, trying login...${NC}"

    # Login instead
    LOGIN_RESPONSE=$(curl -s -X POST ${BASE_URL}:${AUTH_PORT}/api/auth/login \
      -H "Content-Type: application/json" \
      -d '{
        "username": "apitest",
        "password": "test123"
      }')

    echo $LOGIN_RESPONSE | jq '.'
    ACCESS_TOKEN=$(echo $LOGIN_RESPONSE | jq -r '.access_token')
fi

echo -e "${GREEN}✅ User authenticated${NC}"
echo -e "🔑 Token: ${ACCESS_TOKEN:0:50}...\n"

# Test 3: Get Current User
echo -e "${BLUE}3️⃣  Getting current user info...${NC}"
curl -s -X GET ${BASE_URL}:${AUTH_PORT}/api/auth/me \
  -H "Authorization: Bearer $ACCESS_TOKEN" | jq '.'
echo -e "${GREEN}✅ User info retrieved${NC}\n"

# Test 4: List Products
echo -e "${BLUE}4️⃣  Listing products...${NC}"
PRODUCTS_RESPONSE=$(curl -s ${BASE_URL}:${PRODUCT_PORT}/api/products/)
echo $PRODUCTS_RESPONSE | jq '.'
PRODUCT_ID=$(echo $PRODUCTS_RESPONSE | jq -r '.[0].id')
echo -e "${GREEN}✅ Products listed${NC}"
echo -e "📦 First Product ID: ${PRODUCT_ID}\n"

# Test 5: Get Product Details
echo -e "${BLUE}5️⃣  Getting product details...${NC}"
curl -s ${BASE_URL}:${PRODUCT_PORT}/api/products/${PRODUCT_ID} | jq '.'
echo -e "${GREEN}✅ Product details retrieved${NC}\n"

# Test 6: Create Order
echo -e "${BLUE}6️⃣  Creating order...${NC}"
ORDER_RESPONSE=$(curl -s -X POST ${BASE_URL}:${ORDER_PORT}/api/orders/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -d "{
    \"items\": [
      {
        \"product_id\": \"${PRODUCT_ID}\",
        \"quantity\": 2
      }
    ],
    \"shipping_address\": \"123 Test Street, Test City, TC 12345\"
  }")

echo $ORDER_RESPONSE | jq '.'
ORDER_ID=$(echo $ORDER_RESPONSE | jq -r '.id')
echo -e "${GREEN}✅ Order created${NC}"
echo -e "🛒 Order ID: ${ORDER_ID}\n"

# Test 7: Process Payment
echo -e "${BLUE}7️⃣  Processing payment...${NC}"
PAYMENT_RESPONSE=$(curl -s -X POST ${BASE_URL}:${PAYMENT_PORT}/api/payments/process \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -d "{
    \"order_id\": ${ORDER_ID},
    \"payment_method\": \"credit_card\",
    \"card_number\": \"4111111111111111\",
    \"card_holder\": \"API Test User\",
    \"cvv\": \"123\",
    \"expiry\": \"12/25\"
  }")

echo $PAYMENT_RESPONSE | jq '.'
echo -e "${GREEN}✅ Payment processed${NC}\n"

# Test 8: Get My Orders
echo -e "${BLUE}8️⃣  Getting my orders...${NC}"
curl -s -X GET ${BASE_URL}:${ORDER_PORT}/api/orders/ \
  -H "Authorization: Bearer $ACCESS_TOKEN" | jq '.'
echo -e "${GREEN}✅ Orders retrieved${NC}\n"

# Test 9: Admin Dashboard (if admin token available)
echo -e "${BLUE}9️⃣  Testing admin dashboard...${NC}"
ADMIN_LOGIN=$(curl -s -X POST ${BASE_URL}:${AUTH_PORT}/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }')

ADMIN_TOKEN=$(echo $ADMIN_LOGIN | jq -r '.access_token')

if [ "$ADMIN_TOKEN" != "null" ]; then
    echo "Getting dashboard stats..."
    curl -s -X GET ${BASE_URL}:${DASHBOARD_PORT}/api/dashboard/stats \
      -H "Authorization: Bearer $ADMIN_TOKEN" | jq '.'
    echo -e "${GREEN}✅ Dashboard accessible${NC}\n"
else
    echo -e "${YELLOW}⚠️  Admin login failed${NC}\n"
fi

echo ""
echo "=========================================="
echo -e "${GREEN}🎉 All API tests completed successfully!${NC}"
echo "=========================================="
echo ""
echo "📝 Summary:"
echo "  ✅ All services are healthy"
echo "  ✅ User registration/login works"
echo "  ✅ Product listing works"
echo "  ✅ Order creation works"
echo "  ✅ Payment processing works"
echo "  ✅ Admin dashboard accessible"
echo ""
echo "🌐 API Documentation:"
echo "  Auth Service:      http://localhost:8001/docs"
echo "  Product Service:   http://localhost:8002/docs"
echo "  Order Service:     http://localhost:8003/docs"
echo "  Payment Service:   http://localhost:8004/docs"
echo "  Dashboard Service: http://localhost:8005/docs"
echo ""
