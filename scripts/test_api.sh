#!/bin/bash

# Script para testar os endpoints da API

BASE_URL="http://localhost:8080"
EMAIL="test@example.com"
PASSWORD="test123"

echo "🧪 Testando API do E-commerce..."
echo ""

# Testar health check
echo "1️⃣  Testando Health Check..."
curl -s "$BASE_URL/health" | jq '.'
echo ""

# Registrar usuário
echo "2️⃣  Registrando novo usuário..."
REGISTER_RESPONSE=$(curl -s -X POST "$BASE_URL/api/auth/register" \
  -H "Content-Type: application/json" \
  -d "{\"email\": \"$EMAIL\", \"password\": \"$PASSWORD\"}")

echo $REGISTER_RESPONSE | jq '.'

# Extrair token
ACCESS_TOKEN=$(echo $REGISTER_RESPONSE | jq -r '.tokens.access_token')

if [ "$ACCESS_TOKEN" == "null" ]; then
    echo "⚠️  Usuário já existe, tentando login..."

    # Fazer login
    echo ""
    echo "3️⃣  Fazendo login..."
    LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/api/auth/login" \
      -H "Content-Type: application/json" \
      -d "{\"email\": \"$EMAIL\", \"password\": \"$PASSWORD\"}")

    echo $LOGIN_RESPONSE | jq '.'
    ACCESS_TOKEN=$(echo $LOGIN_RESPONSE | jq -r '.tokens.access_token')
fi

echo ""
echo "🔑 Access Token: $ACCESS_TOKEN"
echo ""

# Testar endpoint protegido
echo "4️⃣  Testando endpoint protegido (/api/auth/me)..."
curl -s -X GET "$BASE_URL/api/auth/me" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | jq '.'

echo ""
echo "✅ Testes concluídos!"
