# ⚡ Quick Start - 5 Minutos

## 🚀 Início Rápido

### 1. Pré-requisitos
```bash
# Verificar se Docker está instalado
docker --version

# Verificar se Docker Compose está instalado
docker-compose --version
```

### 2. Configurar Ambiente
```bash
# Copiar arquivo de configuração
cp .env.example .env

# Opcional: Editar variáveis (pode usar as padrões para teste)
nano .env
```

### 3. Iniciar Serviços
```bash
# Construir e iniciar todos os serviços
docker-compose up --build

# OU em background
docker-compose up -d --build
```

Aguarde alguns minutos. Você verá logs de todos os serviços sendo iniciados.

### 4. Verificar Status
```bash
# Verificar containers rodando
docker ps

# Testar health check do API Gateway
curl http://localhost:8080/health

# Testar Auth Service
curl http://localhost:5001/health

# Testar Product Service
curl http://localhost:5003/health
```

### 5. Popular Banco de Dados
```bash
# Adicionar produtos de exemplo
curl -X POST http://localhost:8080/api/products/seed
```

### 6. Testar API

#### Registrar Usuário
```bash
curl -X POST http://localhost:8080/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "teste@example.com",
    "password": "senha123"
  }'
```

Guarde o `access_token` da resposta!

#### Listar Produtos
```bash
curl http://localhost:8080/api/products?page=1&per_page=5
```

#### Acessar Endpoint Protegido
```bash
curl -X GET http://localhost:8080/api/auth/me \
  -H "Authorization: Bearer SEU_ACCESS_TOKEN_AQUI"
```

### 7. Acessar Bancos de Dados

#### PostgreSQL
```bash
docker exec -it ecommerce_postgres psql -U ecommerce_user -d ecommerce_db

# Ver usuários
SELECT * FROM users;
```

#### MongoDB
```bash
docker exec -it ecommerce_mongodb mongosh -u mongo_user -p mongo_pass

# Usar database
use ecommerce_products

# Ver produtos
db.products.find().pretty()
```

---

## 🎯 Fluxo Completo de Teste

Execute o script de teste automatizado:

```bash
chmod +x scripts/test_api.sh
./scripts/test_api.sh
```

Ou teste manualmente:

```bash
# 1. Registrar
RESPONSE=$(curl -s -X POST http://localhost:8080/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"pass123"}')

# 2. Extrair token
TOKEN=$(echo $RESPONSE | jq -r '.tokens.access_token')

# 3. Acessar endpoint protegido
curl -X GET http://localhost:8080/api/auth/me \
  -H "Authorization: Bearer $TOKEN"

# 4. Listar produtos
curl http://localhost:8080/api/products

# 5. Ver detalhes de um produto
curl http://localhost:8080/api/products/PRODUCT_ID_AQUI
```

---

## 🛑 Parar Serviços

```bash
# Parar containers
docker-compose down

# Parar e remover volumes (⚠️ apaga dados)
docker-compose down -v
```

---

## 🔧 Troubleshooting Rápido

### Porta já em uso
```bash
# Linux/Mac
lsof -i :8080
kill -9 <PID>

# Alterar porta no docker-compose.yml
ports:
  - "8081:80"  # Usar 8081 ao invés de 8080
```

### Container não inicia
```bash
# Ver logs
docker-compose logs auth-service

# Rebuild
docker-compose up --build --force-recreate auth-service
```

### Banco de dados não conecta
```bash
# Verificar se container está rodando
docker ps | grep postgres

# Testar conexão
docker exec ecommerce_postgres pg_isready

# Reiniciar container
docker-compose restart postgres
```

### Limpar tudo e recomeçar
```bash
# Parar tudo
docker-compose down -v

# Remover imagens
docker rmi $(docker images -q 'ecommerce*')

# Reconstruir
docker-compose up --build
```

---

## 📚 Próximos Passos

Após testar o básico:

1. ✅ Leia o [README.md](README.md) completo
2. ✅ Explore a [ARCHITECTURE.md](ARCHITECTURE.md)
3. ✅ Consulte [API_REFERENCE.md](API_REFERENCE.md)
4. ✅ Desenvolva novos serviços com [DEVELOPMENT.md](DEVELOPMENT.md)
5. ✅ Veja tarefas pendentes em [TODO.md](TODO.md)

---

## 🆘 Precisa de Ajuda?

- **Documentação completa**: [README.md](README.md)
- **Referência da API**: [API_REFERENCE.md](API_REFERENCE.md)
- **Guia de desenvolvimento**: [DEVELOPMENT.md](DEVELOPMENT.md)
- **Arquitetura**: [ARCHITECTURE.md](ARCHITECTURE.md)

---

## ✨ Recursos Implementados

- ✅ Auth Service (JWT completo)
- ✅ Product Service (CRUD + busca)
- ✅ API Gateway (Nginx)
- ✅ PostgreSQL + MongoDB
- ✅ Docker Compose
- ✅ Health checks
- ✅ Documentação completa

## 🚧 Em Desenvolvimento

- ⏳ User Service
- ⏳ Order Service
- ⏳ Payment Service
- ⏳ Notification Service
- ⏳ Frontend React
- ⏳ Testes automatizados

---

**Pronto para começar! 🎉**
