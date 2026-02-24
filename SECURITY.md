# 🔒 Guia de Segurança - EVAonline

## ⚠️ IMPORTANTE: Leia Antes do Deploy

Este documento contém informações críticas de segurança que **DEVEM** ser seguidas antes de fazer deploy em produção.

---

## 🚨 Checklist de Segurança Pré-Deploy

### 1. ✅ Variáveis de Ambiente

**NUNCA use os valores do `.env.example` em produção!**

#### Criar arquivo `.env` de produção:

```bash
# Copiar template
cp .env.example .env

# Editar com senhas fortes
nano .env  # ou notepad .env no Windows
```

#### Gerar Senhas Fortes:

**SECRET_KEY (obrigatório):**
```bash
# Linux/Mac
python -c 'import secrets; print(secrets.token_urlsafe(32))'

# Windows PowerShell
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**Senhas de Banco e Redis:**
```bash
# Linux/Mac
openssl rand -base64 32

# Windows PowerShell (alternativa)
python -c "import secrets; print(secrets.token_hex(16))"
```

#### Exemplo de `.env` Seguro:

```bash
# PRODUÇÃO - Valores seguros
POSTGRES_PASSWORD=x9K2mP8nQ5vL3wR7yT4jH6fD1sA0gZ9c
REDIS_PASSWORD=k4L7mN2pQ8vW5xY1zR6tJ3hF9dS0aG5b
SECRET_KEY=Np8Qr4Kt7Lw2Mx5Vy1Zz3Hj6Fd9Gs0Ba2Cd4Ef7Gh1Jk3Lm6Np9Qr
```

---

## 🔐 Configurações Obrigatórias

### SECRET_KEY

❌ **NUNCA faça isso:**
```python
SECRET_KEY = "minha-senha-secreta"  # Hard-coded
```

✅ **SEMPRE faça isso:**
```python
import os
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY must be set!")
```

### Senhas de Banco de Dados

**Requisitos mínimos:**
- ✅ Mínimo 16 caracteres
- ✅ Letras maiúsculas e minúsculas
- ✅ Números e caracteres especiais
- ✅ Gerada aleatoriamente
- ❌ Não usar palavras do dicionário
- ❌ Não usar padrões conhecidos (123456, password, etc.)

---

## 🐳 Segurança Docker

### 1. Não Expor Portas Desnecessárias

**Em produção, remover:**
```yaml
# ❌ NÃO expor em produção
ports:
  - "5432:5432"  # PostgreSQL
  - "6379:6379"  # Redis
```

**Manter apenas:**
```yaml
# ✅ OK expor em produção
ports:
  - "8000:8000"  # API
  - "9090:9090"  # Prometheus (opcional)
  - "3000:3000"  # Grafana (opcional)
```

### 2. Docker Secrets (Recomendado)

Para produção com Docker Swarm:

```yaml
secrets:
  postgres_password:
    external: true
  redis_password:
    external: true
  secret_key:
    external: true

services:
  postgres:
    secrets:
      - postgres_password
    environment:
      POSTGRES_PASSWORD_FILE: /run/secrets/postgres_password
```

---

## 🌐 CORS e APIs

### Desenvolvimento (OK):
```python
BACKEND_CORS_ORIGINS = ["*"]  # Aceita qualquer origem
```

### Produção (OBRIGATÓRIO):
```python
BACKEND_CORS_ORIGINS = [
    "https://seu-dominio.com",
    "https://www.seu-dominio.com"
]
```

---

## 📊 Monitoramento

### Grafana

**Senha padrão:** admin/admin

⚠️ **TROCAR IMEDIATAMENTE em produção:**

```bash
docker exec -it evaonline-grafana grafana-cli admin reset-admin-password 'NovaSenhaForte123!'
```

### Flower (Celery)

⚠️ **Sem autenticação por padrão!**

**Adicionar autenticação:**
```yaml
celery-flower:
  environment:
    - FLOWER_BASIC_AUTH=user:password
```

---

## 🔍 Auditoria de Segurança

### Antes do Deploy:

1. **Verificar segredos no código:**
```bash
# Buscar por senhas hard-coded
grep -r "password\|secret\|key" backend/ --exclude-dir=.venv
```

2. **Verificar vulnerabilidades:**
```bash
# Instalar ferramentas
pip install safety bandit

# Escanear dependências
safety check -r requirements.txt

# Escanear código
bandit -r backend/ -ll
```

3. **Validar configuração Docker:**
```bash
docker compose config
```

---

## 📝 .gitignore Crítico

**Verificar que estes arquivos NUNCA sejam commitados:**

```gitignore
# ✅ OBRIGATÓRIO no .gitignore
.env
.env.*
!.env.example
secrets/
keys/
*.key
*.pem
*.crt
```

**Verificar status:**
```bash
git status --ignored
```

---

## 🚀 Deploy Seguro

### Passo 1: Preparar Ambiente

```bash
# 1. Criar .env de produção
cp .env.example .env

# 2. Gerar senhas fortes
python -c 'import secrets; print("SECRET_KEY=" + secrets.token_urlsafe(32))'
python -c 'import secrets; print("POSTGRES_PASSWORD=" + secrets.token_hex(16))'
python -c 'import secrets; print("REDIS_PASSWORD=" + secrets.token_hex(16))'

# 3. Editar .env com as senhas geradas
nano .env
```

### Passo 2: Validar Segurança

```bash
# Verificar que .env não está no git
git status --ignored | grep .env

# Escanear vulnerabilidades
safety check -r requirements.txt
bandit -r backend/ -ll

# Validar Docker
docker compose config
```

### Passo 3: Build e Deploy

```bash
# Build
docker compose build

# Subir serviços
docker compose up -d postgres redis
sleep 30
docker compose up -d api celery-worker celery-beat

# Verificar health
docker ps
docker compose logs -f api
```

---

## 🆘 Incidentes de Segurança

### Se Credenciais Foram Expostas:

1. **Imediatamente:**
   - ❌ Trocar TODAS as senhas
   - ❌ Revogar todos os tokens
   - ❌ Reiniciar todos os serviços

2. **Investigar:**
   - 🔍 Verificar logs de acesso
   - 🔍 Verificar histórico do Git
   - 🔍 Verificar backups

3. **Limpar Histórico Git (se necessário):**
```bash
# ⚠️ CUIDADO: Reescreve histórico
git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch .env' \
  --prune-empty --tag-name-filter cat -- --all
```

---

## 📚 Referências

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Docker Security Best Practices](https://docs.docker.com/engine/security/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [PostgreSQL Security](https://www.postgresql.org/docs/current/security.html)

---

## ✅ Checklist Final

Antes de fazer deploy, confirme:

- [ ] `.env` criado com senhas fortes
- [ ] `SECRET_KEY` gerado e configurado
- [ ] `.env` está no `.gitignore`
- [ ] Nenhum segredo hard-coded no código
- [ ] CORS configurado para domínio específico
- [ ] Portas desnecessárias removidas
- [ ] Senhas do Grafana e Flower alteradas
- [ ] Vulnerabilidades escaneadas (safety, bandit)
- [ ] Logs configurados corretamente
- [ ] Health checks funcionando
- [ ] Backup configurado
- [ ] Monitoramento ativo

---

**Última atualização:** 23/02/2026  
**Responsável:** Equipe EVAonline  
**Contato Segurança:** angelassilviane@gmail.com
