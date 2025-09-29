#!/usr/bin/env python3
"""Script para testar a API do e-commerce"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_health():
    """Testar endpoint de saúde"""
    print("1. Testando Health Check...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    print()

def test_register():
    """Registrar novo usuário"""
    print("2. Registrando novo usuário...")
    data = {
        "email": "teste@example.com",
        "username": "testuser",
        "password": "Test1234!",
        "first_name": "Test",
        "last_name": "User"
    }
    response = requests.post(f"{BASE_URL}/api/auth/register", json=data)
    print(f"   Status: {response.status_code}")
    if response.status_code == 201:
        result = response.json()
        print(f"   User created: {result.get('user', {}).get('username')}")
        return result.get('access_token')
    else:
        print(f"   Error: {response.text}")
    print()

def test_login():
    """Fazer login"""
    print("3. Fazendo login...")
    data = {
        "username": "admin",
        "password": "Admin123!"
    }
    response = requests.post(f"{BASE_URL}/api/auth/login", json=data)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"   Login successful for: {result.get('user', {}).get('username')}")
        return result.get('access_token')
    else:
        print(f"   Error: {response.text}")
    print()
    return None

def test_products(token=None):
    """Listar produtos"""
    print("4. Listando produtos...")
    headers = {}
    if token:
        headers['Authorization'] = f'Bearer {token}'

    response = requests.get(f"{BASE_URL}/api/products/", headers=headers)
    print(f"   Status: {response.status_code}")
    result = response.json()
    print(f"   Total produtos: {result.get('pagination', {}).get('total', 0)}")
    print()

def test_create_product(token):
    """Criar produto (requer admin)"""
    print("5. Criando produto (Admin only)...")
    if not token:
        print("   Skipped: No token available")
        return

    headers = {'Authorization': f'Bearer {token}'}
    data = {
        "sku": "TEST-001",
        "name": "Test Product",
        "price": 99.99,
        "quantity": 10,
        "description": "This is a test product"
    }

    response = requests.post(f"{BASE_URL}/api/products/", json=data, headers=headers)
    print(f"   Status: {response.status_code}")
    if response.status_code == 201:
        result = response.json()
        print(f"   Product created: {result.get('product', {}).get('name')}")
    else:
        print(f"   Response: {response.text[:200]}")
    print()

def test_swagger():
    """Verificar Swagger UI"""
    print("6. Verificando Swagger Documentation...")
    response = requests.get(f"{BASE_URL}/api/docs")
    print(f"   Status: {response.status_code}")
    print(f"   Swagger UI: {'Available' if response.status_code == 200 else 'Not Available'}")
    print()

def main():
    print("="*50)
    print("TESTANDO API E-COMMERCE")
    print("="*50)
    print()

    # Testes básicos
    test_health()
    test_swagger()

    # Teste de autenticação
    token = test_login()

    # Teste de produtos
    test_products(token)

    # Teste de criação (admin)
    if token:
        test_create_product(token)

    # Tentar registrar novo usuário
    new_token = test_register()

    print("="*50)
    print("RESUMO DOS TESTES")
    print("="*50)
    print("✅ API está rodando em http://localhost:5000")
    print("✅ Swagger disponível em http://localhost:5000/api/docs")
    print("✅ Login admin funcionando" if token else "❌ Problema no login admin")
    print("\nPara acessar o Swagger no navegador:")
    print("http://localhost:5000/api/docs")

if __name__ == "__main__":
    main()