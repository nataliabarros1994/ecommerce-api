# 🔧 Comandos Rápidos de Referência

## 🚀 Docker Compose

### Iniciar Serviços
```bash
# Iniciar todos os serviços
docker-compose up

# Iniciar em background
docker-compose up -d

# Rebuild completo
docker-compose up --build

# Rebuild de um serviço específico
docker-compose up --build auth-service
```

### Parar Serviços
```bash
# Parar serviços
docker-compose down

# Parar e remover volumes (⚠️ apaga dados)
docker-compose down -v

# Parar serviço específico
docker-compose stop auth-service
```

### Logs
```bash
# Ver logs de todos os serviços
docker-compose logs

# Seguir logs em tempo real
docker-compose logs -f

# Logs de um serviço específico
docker-compose logs -f auth-service

# Últimas 100 linhas
docker-compose logs --tail=100 auth-service
```

### Status
```bash
# Ver containers rodando
docker-compose ps

# Ver status detalhado
docker ps

# Ver recursos utilizados
docker stats
```

### Restart
```bash
# Reiniciar todos os serviços
docker-compose restart

# Reiniciar serviço específico
docker-compose restart auth-service
```

---

## 🗄️ Banco de Dados

### PostgreSQL
```bash
# Acessar PostgreSQL
docker exec -it ecommerce_postgres psql -U ecommerce_user -d ecommerce_db

# Comandos dentro do psql:
\dt                    # Listar tabelas
\d users              # Estrutura da tabela users
\l                    # Listar databases
\c database_name      # Conectar a outro database
\q                    # Sair

# Queries úteis
SELECT * FROM users;
SELECT * FROM refresh_tokens;
SELECT COUNT(*) FROM users;
```

### MongoDB
```bash
# Acessar MongoDB
docker exec -it ecommerce_mongodb mongosh -u mongo_user -p mongo_pass

# Comandos dentro do mongosh:
show dbs                          # Listar databases
use ecommerce_products           # Usar database
show collections                 # Listar collections
db.products.find().pretty()      # Ver produtos
db.products.countDocuments()     # Contar produtos
db.categories.find()             # Ver categorias
exit                             # Sair

# Queries úteis
db.products.find({category: "electronics"})
db.products.find({price: {$gt: 100}})
db.products.find({name: /notebook/i})
```

---

## 🧪 Testar API

### Health Checks
```bash
# API Gateway
curl http://localhost:8080/health

# Auth Service
curl http://localhost:5001/health

# Product Service
curl http://localhost:5003/health
```

### Autenticação
```bash
# Registrar
curl -X POST http://localhost:8080/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'

# Login
curl -X POST http://localhost:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'

# Obter informações do usuário (requer token)
curl -X GET http://localhost:8080/api/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"

# Logout
curl -X POST http://localhost:8080/api/auth/logout \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Produtos
```bash
# Popular banco de dados
curl -X POST http://localhost:8080/api/products/seed

# Listar produtos
curl http://localhost:8080/api/products

# Listar com paginação
curl "http://localhost:8080/api/products?page=1&per_page=5"

# Buscar produtos
curl "http://localhost:8080/api/products?search=notebook"

# Filtrar por categoria
curl "http://localhost:8080/api/products?category=electronics"

# Filtrar por preço
curl "http://localhost:8080/api/products?min_price=100&max_price=500"

# Ordenar
curl "http://localhost:8080/api/products?sort=price&order=asc"

# Obter detalhes de um produto
curl http://localhost:8080/api/products/PRODUCT_ID

# Listar categorias
curl http://localhost:8080/api/products/categories
```

### Criar Produto (Admin)
```bash
# Criar produto (requer token de admin)
curl -X POST http://localhost:8080/api/products \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -d '{
    "name": "Novo Produto",
    "description": "Descrição do produto",
    "price": 99.90,
    "stock": 100,
    "category": "electronics"
  }'

# Atualizar produto
curl -X PUT http://localhost:8080/api/products/PRODUCT_ID \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -d '{"price": 89.90}'

# Deletar produto (soft delete)
curl -X DELETE http://localhost:8080/api/products/PRODUCT_ID \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

---

## 🔍 Debug

### Acessar Container
```bash
# Shell no container
docker exec -it auth_service /bin/sh
docker exec -it product_service /bin/sh
docker exec -it ecommerce_postgres /bin/bash
docker exec -it ecommerce_mongodb /bin/bash

# Executar comando no container
docker exec auth_service ls -la
docker exec auth_service cat config.py
```

### Verificar Logs de Erro
```bash
# Ver erros recentes
docker-compose logs --tail=50 auth-service | grep -i error

# Seguir apenas erros
docker-compose logs -f auth-service 2>&1 | grep -i error
```

### Testar Conectividade
```bash
# Testar se PostgreSQL está respondendo
docker exec ecommerce_postgres pg_isready -U ecommerce_user

# Testar MongoDB
docker exec ecommerce_mongodb mongosh --eval "db.adminCommand('ping')"

# Testar rede entre containers
docker exec auth_service ping -c 3 postgres
docker exec product_service ping -c 3 mongodb
```

---

## 🧹 Limpeza

### Remover Containers
```bash
# Remover containers parados
docker container prune

# Remover container específico
docker rm -f auth_service
```

### Remover Imagens
```bash
# Remover imagens não utilizadas
docker image prune

# Remover imagens do projeto
docker rmi $(docker images -q 'ecommerce*')

# Remover todas as imagens não utilizadas
docker image prune -a
```

### Remover Volumes
```bash
# ⚠️ CUIDADO: Remove dados do banco
docker volume prune

# Remover volumes do projeto
docker volume rm ecommerce_postgres_data
docker volume rm ecommerce_mongodb_data
```

### Limpeza Completa
```bash
# ⚠️ CUIDADO: Remove tudo
docker system prune -a --volumes

# Recomeçar do zero
docker-compose down -v
docker rmi $(docker images -q 'ecommerce*')
docker-compose up --build
```

---

## 🔧 Desenvolvimento Local

### Criar Virtual Environment
```bash
# Criar venv
python -m venv venv

# Ativar (Linux/Mac)
source venv/bin/activate

# Ativar (Windows)
venv\Scripts\activate

# Desativar
deactivate
```

### Instalar Dependências
```bash
# Instalar requirements de um serviço
cd services/auth-service
pip install -r requirements.txt

# Instalar em modo desenvolvimento
pip install -e .
```

### Executar Localmente
```bash
# Exportar variáveis de ambiente
export POSTGRES_HOST=localhost
export JWT_SECRET_KEY=dev-key

# Executar
python run.py

# Ou com Flask
flask run --port=5001
```

---

## 📊 Monitoramento

### Ver Uso de Recursos
```bash
# CPU e memória de cada container
docker stats

# Uso de disco
docker system df

# Informações detalhadas
docker inspect auth_service
```

### Ver Redes
```bash
# Listar redes
docker network ls

# Inspecionar rede
docker network inspect ecommerce_network
```

---

## 🔐 Segurança

### Criar Usuário Admin
```bash
# Acessar PostgreSQL
docker exec -it ecommerce_postgres psql -U ecommerce_user -d ecommerce_db

# Tornar usuário admin
UPDATE users SET is_admin = true WHERE email = 'seu-email@example.com';

# Verificar
SELECT email, is_admin FROM users;
```

### Gerar Novo JWT Secret
```bash
# Gerar chave aleatória
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Atualizar no .env
JWT_SECRET_KEY=nova_chave_gerada
```

---

## 🚀 Scripts Úteis

### Backup de Banco
```bash
# Backup PostgreSQL
docker exec ecommerce_postgres pg_dump -U ecommerce_user ecommerce_db > backup.sql

# Restore PostgreSQL
docker exec -i ecommerce_postgres psql -U ecommerce_user ecommerce_db < backup.sql

# Backup MongoDB
docker exec ecommerce_mongodb mongodump --out /backup

# Restore MongoDB
docker exec ecommerce_mongodb mongorestore /backup
```

### Resetar Banco de Dados
```bash
# PostgreSQL
docker exec ecommerce_postgres psql -U ecommerce_user -d ecommerce_db -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"

# MongoDB
docker exec ecommerce_mongodb mongosh -u mongo_user -p mongo_pass --eval "db.dropDatabase()"

# Reiniciar serviços
docker-compose restart auth-service product-service
```

---

## 📝 Variáveis Úteis (Bash)

```bash
# Salvar token em variável
TOKEN=$(curl -s -X POST http://localhost:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}' | jq -r '.tokens.access_token')

# Usar token
curl -H "Authorization: Bearer $TOKEN" http://localhost:8080/api/auth/me

# Salvar resposta em arquivo
curl http://localhost:8080/api/products > products.json
```

---

## 🆘 Troubleshooting

### Porta já em uso
```bash
# Linux/Mac - Ver processo usando porta
lsof -i :8080
lsof -i :5432
lsof -i :27017

# Matar processo
kill -9 <PID>

# Windows - Ver processo
netstat -ano | findstr :8080

# Matar processo (Windows)
taskkill /PID <PID> /F
```

### Permissões (Linux)
```bash
# Adicionar usuário ao grupo docker
sudo usermod -aG docker $USER

# Logout e login novamente

# Dar permissão aos scripts
chmod +x scripts/*.sh
```

### Container crashando
```bash
# Ver logs completos
docker logs auth_service

# Inspecionar container
docker inspect auth_service

# Ver últimos eventos
docker events --filter 'container=auth_service'
```

---

## 📚 Referências Rápidas

- **README**: Documentação principal
- **QUICKSTART**: Início rápido em 5 minutos
- **API_REFERENCE**: Todos os endpoints
- **DEVELOPMENT**: Guia de desenvolvimento
- **ARCHITECTURE**: Detalhes da arquitetura

---

**Salve este arquivo para referência rápida! 📌**
