#!/usr/bin/env python3
"""Teste completo do sistema E-Commerce"""

import requests
import json
from colorama import init, Fore, Style

init(autoreset=True)

BASE_URL = "http://localhost:5000"

def test_endpoint(name, method, url, expected_status, data=None, headers=None):
    """Testa um endpoint e reporta o resultado"""
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers)
        else:
            response = requests.request(method, url, json=data, headers=headers)

        if response.status_code == expected_status:
            print(f"{Fore.GREEN}✅ {name}: {response.status_code} OK")
            return True, response
        else:
            print(f"{Fore.RED}❌ {name}: {response.status_code} (expected {expected_status})")
            return False, response
    except Exception as e:
        print(f"{Fore.RED}❌ {name}: Error - {str(e)}")
        return False, None

def main():
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"{Fore.CYAN}E-COMMERCE API - TESTE COMPLETO")
    print(f"{Fore.CYAN}{'='*60}\n")

    results = {"passed": 0, "failed": 0}

    # 1. Página inicial
    success, _ = test_endpoint(
        "Página inicial (porta 5000)",
        "GET",
        f"{BASE_URL}/",
        200
    )
    results["passed" if success else "failed"] += 1

    # 2. Página inicial via Nginx
    success, _ = test_endpoint(
        "Página inicial (porta 80 - Nginx)",
        "GET",
        "http://localhost/",
        200
    )
    results["passed" if success else "failed"] += 1

    # 3. Health check
    success, _ = test_endpoint(
        "Health Check",
        "GET",
        f"{BASE_URL}/health",
        200
    )
    results["passed" if success else "failed"] += 1

    # 4. Swagger Documentation
    success, _ = test_endpoint(
        "Swagger UI",
        "GET",
        f"{BASE_URL}/api/docs",
        200
    )
    results["passed" if success else "failed"] += 1

    # 5. Lista de produtos
    success, _ = test_endpoint(
        "Listar produtos",
        "GET",
        f"{BASE_URL}/api/products/",
        200
    )
    results["passed" if success else "failed"] += 1

    # 6. Login admin
    success, response = test_endpoint(
        "Login Admin",
        "POST",
        f"{BASE_URL}/api/auth/login",
        200,
        data={"username": "admin", "password": "Admin123!"}
    )
    results["passed" if success else "failed"] += 1

    token = None
    if success and response:
        token = response.json().get('access_token')

    # 7. Perfil do usuário (autenticado)
    if token:
        success, _ = test_endpoint(
            "Perfil do usuário (autenticado)",
            "GET",
            f"{BASE_URL}/api/auth/me",
            200,
            headers={'Authorization': f'Bearer {token}'}
        )
        results["passed" if success else "failed"] += 1

    # 8. Carrinho
    if token:
        success, _ = test_endpoint(
            "Ver carrinho",
            "GET",
            f"{BASE_URL}/api/cart/",
            200,
            headers={'Authorization': f'Bearer {token}'}
        )
        results["passed" if success else "failed"] += 1

    # 9. Categorias
    success, _ = test_endpoint(
        "Listar categorias",
        "GET",
        f"{BASE_URL}/api/categories/",
        200
    )
    results["passed" if success else "failed"] += 1

    # 10. API Info via Nginx
    success, _ = test_endpoint(
        "Health via Nginx",
        "GET",
        "http://localhost/health",
        200
    )
    results["passed" if success else "failed"] += 1

    # Resumo
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"{Fore.CYAN}RESUMO DOS TESTES")
    print(f"{Fore.CYAN}{'='*60}\n")

    total = results["passed"] + results["failed"]
    print(f"{Fore.GREEN}✅ Passou: {results['passed']}/{total}")
    print(f"{Fore.RED}❌ Falhou: {results['failed']}/{total}")

    if results["failed"] == 0:
        print(f"\n{Fore.GREEN}{Style.BRIGHT}🎉 TODOS OS TESTES PASSARAM!")
    else:
        print(f"\n{Fore.YELLOW}⚠️  Alguns testes falharam")

    print(f"\n{Fore.CYAN}URLs Disponíveis:")
    print(f"  {Fore.WHITE}• Página inicial: http://localhost:5000/")
    print(f"  {Fore.WHITE}• Via Nginx: http://localhost/")
    print(f"  {Fore.WHITE}• Swagger UI: http://localhost:5000/api/docs")
    print(f"  {Fore.WHITE}• Health Check: http://localhost:5000/health")
    print()

if __name__ == "__main__":
    main()