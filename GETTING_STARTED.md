# 🚀 Guia de Início Rápido

## Pré-requisitos

Certifique-se de ter instalado:

- [Docker](https://docs.docker.com/get-docker/) (versão 20.10+)
- [Docker Compose](https://docs.docker.com/compose/install/) (versão 2.0+)
- [Git](https://git-scm.com/downloads)
- [Python 3.11+](https://www.python.org/downloads/) (para desenvolvimento local)
- [VS Code](https://code.visualstudio.com/) (recomendado)

## Configuração Inicial

### 1. Clone o repositório

```bash
git clone <seu-repositorio>
cd ecommerce-microservices
```

### 2. Configure as variáveis de ambiente

```bash
cp .env.example .env
```

Edite o arquivo `.env` com suas configurações:

```env
# Exemplo de configurações mínimas
POSTGRES_USER=ecommerce_user
POSTGRES_PASSWORD=sua_senha_segura
JWT_SECRET_KEY=sua_chave_secreta_jwt

# Para integração com Stripe (opcional)
STRIPE_SECRET_KEY=sk_test_...
```

### 3. Inicie os serviços

```bash
docker-compose up --build
```

Aguarde alguns minutos enquanto os containers são construídos e iniciados.

### 4. Verifique se está funcionando

Abra seu navegador e acesse:

- API Gateway: http://localhost:8080/health
- Auth Service: http://localhost:5001/health

Você deverá ver:
```json
{
  "status": "healthy",
  "service": "auth-service"
}
```

## Testando a API

### Usando cURL

#### 1. Registrar um usuário

```bash
curl -X POST http://localhost:8080/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "usuario@example.com",
    "password": "senha123"
  }'
```

**Resposta esperada:**
```json
{
  "message": "User registered successfully",
  "user": {
    "id": 1,
    "email": "usuario@example.com",
    "is_active": true,
    "is_admin": false
  },
  "tokens": {
    "access_token": "eyJ...",
    "refresh_token": "eyJ...",
    "token_type": "Bearer",
    "expires_in": 3600
  }
}
```

#### 2. Fazer login

```bash
curl -X POST http://localhost:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "usuario@example.com",
    "password": "senha123"
  }'
```

#### 3. Acessar endpoint protegido

```bash
curl -X GET http://localhost:8080/api/auth/me \
  -H "Authorization: Bearer SEU_ACCESS_TOKEN_AQUI"
```

### Usando Postman

1. Importe a collection (em breve)
2. Configure a variável `base_url` para `http://localhost:8080`
3. Execute as requisições na ordem

## Estrutura de Desenvolvimento

### Adicionar novo endpoint

1. Edite o arquivo de rotas do serviço:
```python
# services/auth-service/app/routes.py

@auth_bp.route('/novo-endpoint', methods=['GET'])
@token_required
def novo_endpoint(current_user):
    return jsonify({'message': 'Funcionou!'}), 200
```

2. Os arquivos são sincronizados automaticamente via volumes Docker
3. O servidor Flask reinicia automaticamente

### Acessar banco de dados

#### PostgreSQL

```bash
docker exec -it ecommerce_postgres psql -U ecommerce_user -d ecommerce_db
```

Comandos úteis:
```sql
-- Listar tabelas
\dt

-- Ver estrutura da tabela
\d users

-- Consultar usuários
SELECT * FROM users;
```

#### MongoDB

```bash
docker exec -it ecommerce_mongodb mongosh -u mongo_user -p mongo_pass
```

Comandos úteis:
```javascript
// Usar database
use ecommerce_products

// Listar collections
show collections

// Consultar produtos
db.products.find()
```

## Desenvolvimento Local (sem Docker)

Se preferir rodar os serviços localmente:

### 1. Crie um ambiente virtual

```bash
cd services/auth-service
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

### 2. Instale as dependências

```bash
pip install -r requirements.txt
```

### 3. Configure variáveis de ambiente

```bash
export POSTGRES_HOST=localhost
export JWT_SECRET_KEY=sua-chave-secreta
# ... outras variáveis
```

### 4. Execute o serviço

```bash
python run.py
```

## Comandos Úteis

### Docker Compose

```bash
# Iniciar serviços
docker-compose up

# Iniciar em background
docker-compose up -d

# Ver logs
docker-compose logs -f auth-service

# Parar serviços
docker-compose down

# Remover volumes (⚠️ apaga dados)
docker-compose down -v

# Rebuild de um serviço específico
docker-compose up --build auth-service
```

### Logs e Debug

```bash
# Ver logs de um serviço
docker-compose logs -f auth-service

# Acessar shell de um container
docker exec -it auth_service /bin/sh

# Ver todos os containers rodando
docker ps
```

### Limpeza

```bash
# Remover containers parados
docker container prune

# Remover imagens não utilizadas
docker image prune

# Limpar tudo (⚠️ cuidado)
docker system prune -a
```

## Troubleshooting

### Porta já em uso

```bash
# Linux/Mac
lsof -i :8080
kill -9 <PID>

# Windows
netstat -ano | findstr :8080
taskkill /PID <PID> /F
```

### Container não inicia

```bash
# Ver logs detalhados
docker-compose logs auth-service

# Verificar health check
docker inspect auth_service | grep Health -A 10
```

### Banco de dados não conecta

1. Verifique se o container do banco está rodando:
```bash
docker ps | grep postgres
```

2. Teste conexão manualmente:
```bash
docker exec -it ecommerce_postgres pg_isready
```

3. Verifique as variáveis de ambiente no `.env`

### Erro de permissão

```bash
# Linux: dar permissão aos scripts
chmod +x scripts/*

# Executar Docker sem sudo (Linux)
sudo usermod -aG docker $USER
# Fazer logout e login novamente
```

## Próximos Passos

Agora que o auth-service está funcionando, você pode:

1. ✅ Testar todos os endpoints de autenticação
2. ⏳ Implementar os demais microserviços (user, product, order)
3. ⏳ Adicionar testes automatizados
4. ⏳ Criar frontend em React
5. ⏳ Configurar CI/CD

## Recursos Adicionais

- [Documentação Flask](https://flask.palletsprojects.com/)
- [Docker Compose Reference](https://docs.docker.com/compose/compose-file/)
- [PostgreSQL Tutorial](https://www.postgresql.org/docs/)
- [MongoDB Manual](https://docs.mongodb.com/manual/)
- [JWT Introduction](https://jwt.io/introduction)

## Suporte

Encontrou algum problema? Abra uma issue no GitHub!

---

**Happy Coding! 🚀**
