#!/bin/bash

# Script para inicialização do ambiente de desenvolvimento

echo "🚀 Inicializando ambiente de desenvolvimento..."

# Verificar se Docker está instalado
if ! command -v docker &> /dev/null; then
    echo "❌ Docker não está instalado. Instale: https://docs.docker.com/get-docker/"
    exit 1
fi

# Verificar se Docker Compose está instalado
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose não está instalado. Instale: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker e Docker Compose encontrados"

# Criar arquivo .env se não existir
if [ ! -f .env ]; then
    echo "📝 Criando arquivo .env..."
    cp .env.example .env
    echo "⚠️  IMPORTANTE: Edite o arquivo .env com suas configurações antes de iniciar!"
else
    echo "✅ Arquivo .env já existe"
fi

# Criar rede Docker se não existir
echo "🌐 Criando rede Docker..."
docker network create ecommerce_network 2>/dev/null || echo "✅ Rede já existe"

# Build dos serviços
echo "🔨 Construindo imagens Docker..."
docker-compose build

echo ""
echo "✅ Ambiente configurado com sucesso!"
echo ""
echo "Próximos passos:"
echo "1. Edite o arquivo .env com suas configurações"
echo "2. Execute: docker-compose up"
echo "3. Acesse: http://localhost:8080/health"
echo ""
