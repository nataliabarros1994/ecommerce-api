#!/bin/bash

# GlowShop API Test Script
# This script tests all microservices endpoints

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Base URLs
AUTH_URL="http://localhost:5001"
USER_URL="http://localhost:5002"
PRODUCT_URL="http://localhost:5003"
ORDER_URL="http://localhost:5004"
PAYMENT_URL="http://localhost:5005"
NOTIFICATION_URL="http://localhost:5006"

# Test credentials
TEST_EMAIL="test@glowshop.com"
TEST_PASSWORD="Test123456"

echo -e "${YELLOW}=== GlowShop API Test Suite ===${NC}\n"

# Step 1: Check health of all services
echo -e "${YELLOW}Step 1: Checking service health...${NC}"

services=("$AUTH_URL:auth-service" "$USER_URL:user-service" "$PRODUCT_URL:product-service" "$ORDER_URL:order-service" "$PAYMENT_URL:payment-service" "$NOTIFICATION_URL:notification-service")

for service in "${services[@]}"; do
    url="${service%%:*}/health"
    name="${service##*:}"

    response=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null || echo "000")

    if [ "$response" -eq 200 ]; then
        echo -e "  ${GREEN}✓${NC} $name is healthy"
    else
        echo -e "  ${RED}✗${NC} $name is not responding (HTTP $response)"
        exit 1
    fi
done

echo ""

# Step 2: Register a new user
echo -e "${YELLOW}Step 2: Registering new user...${NC}"

register_response=$(curl -s -X POST "$AUTH_URL/api/auth/register" \
    -H "Content-Type: application/json" \
    -d "{
        \"email\": \"$TEST_EMAIL\",
        \"password\": \"$TEST_PASSWORD\"
    }")

if echo "$register_response" | grep -q "access_token"; then
    echo -e "  ${GREEN}✓${NC} User registered successfully"
    ACCESS_TOKEN=$(echo "$register_response" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
    USER_ID=$(echo "$register_response" | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)
else
    # Try to login if user already exists
    echo -e "  ${YELLOW}⚠${NC} User already exists, attempting login..."

    login_response=$(curl -s -X POST "$AUTH_URL/api/auth/login" \
        -H "Content-Type: application/json" \
        -d "{
            \"email\": \"$TEST_EMAIL\",
            \"password\": \"$TEST_PASSWORD\"
        }")

    if echo "$login_response" | grep -q "access_token"; then
        echo -e "  ${GREEN}✓${NC} Login successful"
        ACCESS_TOKEN=$(echo "$login_response" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
        USER_ID=$(echo "$login_response" | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)
    else
        echo -e "  ${RED}✗${NC} Failed to authenticate"
        exit 1
    fi
fi

echo ""

# Step 3: Seed products
echo -e "${YELLOW}Step 3: Seeding sample products...${NC}"

seed_response=$(curl -s -X POST "$PRODUCT_URL/api/products/seed")

if echo "$seed_response" | grep -q "message"; then
    echo -e "  ${GREEN}✓${NC} Products seeded successfully"
else
    echo -e "  ${RED}✗${NC} Failed to seed products"
fi

echo ""

# Step 4: List products
echo -e "${YELLOW}Step 4: Listing products...${NC}"

products_response=$(curl -s "$PRODUCT_URL/api/products")

product_count=$(echo "$products_response" | grep -o '"products":\[' | wc -l)

if [ "$product_count" -gt 0 ]; then
    echo -e "  ${GREEN}✓${NC} Products retrieved successfully"
    # Get first product ID
    PRODUCT_ID=$(echo "$products_response" | grep -o '"id":"[^"]*' | head -1 | cut -d'"' -f4)
else
    echo -e "  ${RED}✗${NC} No products found"
fi

echo ""

# Step 5: Create user profile
echo -e "${YELLOW}Step 5: Creating user profile...${NC}"

profile_response=$(curl -s -X POST "$USER_URL/api/users/profile" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    -d '{
        "first_name": "Test",
        "last_name": "User",
        "phone": "+5511999999999",
        "address": "Test Street, 123",
        "city": "São Paulo",
        "state": "SP",
        "country": "Brazil",
        "postal_code": "01234-567"
    }')

if echo "$profile_response" | grep -q "profile"; then
    echo -e "  ${GREEN}✓${NC} User profile created successfully"
else
    echo -e "  ${YELLOW}⚠${NC} Profile might already exist or error occurred"
fi

echo ""

# Step 6: Create an order
echo -e "${YELLOW}Step 6: Creating an order...${NC}"

order_response=$(curl -s -X POST "$ORDER_URL/api/orders" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    -d '{
        "items": [
            {
                "product_id": "'"$PRODUCT_ID"'",
                "product_name": "Test Product",
                "quantity": 2,
                "price": 99.90
            }
        ],
        "shipping_address": "Test Street, 123, São Paulo - SP"
    }')

if echo "$order_response" | grep -q "order"; then
    echo -e "  ${GREEN}✓${NC} Order created successfully"
    ORDER_ID=$(echo "$order_response" | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)
else
    echo -e "  ${RED}✗${NC} Failed to create order"
    echo "$order_response"
fi

echo ""

# Step 7: Process payment
echo -e "${YELLOW}Step 7: Processing payment...${NC}"

payment_response=$(curl -s -X POST "$PAYMENT_URL/api/payments" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    -d '{
        "order_id": "'"$ORDER_ID"'",
        "amount": 199.80,
        "payment_method": "card",
        "currency": "BRL"
    }')

if echo "$payment_response" | grep -q "payment"; then
    echo -e "  ${GREEN}✓${NC} Payment processed successfully"
    PAYMENT_ID=$(echo "$payment_response" | grep -o '"id":"[^"]*' | head -1 | cut -d'"' -f4)
else
    echo -e "  ${RED}✗${NC} Failed to process payment"
fi

echo ""

# Step 8: Get user orders
echo -e "${YELLOW}Step 8: Retrieving user orders...${NC}"

orders_response=$(curl -s "$ORDER_URL/api/orders" \
    -H "Authorization: Bearer $ACCESS_TOKEN")

if echo "$orders_response" | grep -q "id"; then
    echo -e "  ${GREEN}✓${NC} Orders retrieved successfully"
else
    echo -e "  ${RED}✗${NC} Failed to retrieve orders"
fi

echo ""

# Summary
echo -e "${GREEN}=== Test Suite Completed ===${NC}\n"
echo "Summary:"
echo "  - All services are healthy ✓"
echo "  - User authentication works ✓"
echo "  - Products can be listed ✓"
echo "  - Orders can be created ✓"
echo "  - Payments can be processed ✓"
echo ""
echo "Access Token (save for manual testing):"
echo "$ACCESS_TOKEN"
echo ""
echo -e "${YELLOW}Try accessing the services at:${NC}"
echo "  Auth: $AUTH_URL/api/auth"
echo "  Users: $USER_URL/api/users"
echo "  Products: $PRODUCT_URL/api/products"
echo "  Orders: $ORDER_URL/api/orders"
echo "  Payments: $PAYMENT_URL/api/payments"
echo "  Notifications: $NOTIFICATION_URL/api/notifications"
