# 🚀 Checklist de Deploy - EVAonline

## ✅ Pré-Deploy (Local)

- [ ] Todas as correções testadas localmente
- [ ] Single-source Open-Meteo funcionando (6 dias)
- [ ] Smart Fusion funcionando (complementação automática de variáveis)
- [ ] Logs mostrando estratégia de fusão por variável
- [ ] Celery worker processando tarefas
- [ ] Testes unitários passando: `pytest backend/tests/`

## 🔒 Segurança

- [ ] Criar senhas fortes para `.env`:
  ```bash
  POSTGRES_PASSWORD=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
  REDIS_PASSWORD=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
  SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
  GRAFANA_ADMIN_PASSWORD=$(python -c "import secrets; print(secrets.token_urlsafe(16))")
  FLOWER_PASSWORD=$(python -c "import secrets; print(secrets.token_urlsafe(16))")
  ```
- [ ] Adicionar `.env` ao `.gitignore` (já deve estar)
- [ ] Configurar firewall no servidor (apenas portas 22, 80, 443)
- [ ] Habilitar fail2ban para proteção SSH
- [ ] Verificar que **nenhum** serviço além do Nginx expõe porta pública
- [ ] `/metrics` endpoint bloqueado publicamente (Nginx retorna 404)
- [ ] Grafana servido em `/grafana/` via Nginx (sem porta 3000 pública)
- [ ] Flower servido em `/flower/` via Nginx (sem porta 5555 pública)
- [ ] Prometheus sem porta 9090 pública (apenas rede interna)

## 🌐 Servidor (VPS)

- [ ] Servidor Ubuntu 22.04+ com Docker instalado
- [ ] Domínio configurado (DNS apontando para IP do servidor)
- [ ] Certificado SSL (Let's Encrypt com Certbot)
- [ ] **Nginx reverse proxy é OBRIGATÓRIO** (parte do Docker Compose)

### Requisitos Mínimos:
- **CPU**: 2 vCPUs
- **RAM**: 4 GB (2 GB para api + 1 GB para Celery + 1 GB para PostgreSQL/Redis)
- **Disco**: 20 GB SSD
- **Custo**: ~$12-20/mês (DigitalOcean, Linode, Vultr)

## 📦 Deploy Steps

### 1. Preparar Servidor
```bash
# Instalar Docker (inclui Docker Compose v2)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Verificar instalação
docker compose version
```

### 2. Clonar Repositório
```bash
git clone https://github.com/seu-usuario/EVAONLINE.git
cd EVAONLINE
```

### 3. Configurar Ambiente
```bash
# Copiar template
cp .env.example .env

# Gerar senhas seguras e substituir no .env
python -c "import secrets; print(secrets.token_urlsafe(32))"  # POSTGRES_PASSWORD
python -c "import secrets; print(secrets.token_urlsafe(32))"  # REDIS_PASSWORD
python -c "import secrets; print(secrets.token_hex(32))"      # SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(16))"  # GRAFANA_ADMIN_PASSWORD
python -c "import secrets; print(secrets.token_urlsafe(16))"  # FLOWER_PASSWORD

# Editar .env com os valores gerados
nano .env
```

### 4. SSL (Produção)
```bash
# Obter certificado Let's Encrypt
sudo certbot certonly --standalone -d your-domain.com

# Copiar certificados para o projeto
cp /etc/letsencrypt/live/your-domain.com/fullchain.pem docker/nginx/ssl/
cp /etc/letsencrypt/live/your-domain.com/privkey.pem docker/nginx/ssl/

# Descomentar as linhas de SSL em:
#   - docker-compose.yml (porta 443)
#   - docker/nginx/nginx.conf (ssl_certificate directives)
```

### 5. Deploy
```bash
# Build e start
docker compose up -d --build

# Verificar todos os serviços estão healthy
docker compose ps

# Verificar logs
docker compose logs -f api celery-worker nginx
```

### 6. Verificar Segurança
```bash
# /metrics NÃO deve ser acessível publicamente
curl http://your-domain.com/metrics  # Deve retornar 404

# Grafana acessível via sub-path
curl http://your-domain.com/grafana/api/health  # Deve retornar OK

# Flower acessível via sub-path
curl http://your-domain.com/flower/  # Deve pedir autenticação

# Portas internas NÃO devem estar expostas
nmap -p 3000,5432,5555,6379,9090 your-domain.com  # Todas filtered/closed
```

## 🔍 Monitoramento

- [ ] Todos os serviços `healthy`: `docker compose ps`
- [ ] Prometheus coletando métricas (acessível internamente na porta 9090)
- [ ] Grafana dashboards funcionando em `/grafana/`
- [ ] Flower monitorando Celery em `/flower/`
- [ ] Logs persistentes: `volumes: - ./logs:/app/logs`
- [ ] Monitorar uso de recursos: `docker stats`
- [ ] Backup automático do PostgreSQL:
  ```bash
  # Cron job diário
  0 2 * * * docker exec evaonline-postgres pg_dump -U evaonline evaonline | gzip > /backups/evaonline_$(date +\%Y\%m\%d).sql.gz
  ```

## 🚨 Troubleshooting

### Container não inicia
```bash
docker compose logs <service_name>
docker compose down && docker compose up -d
```

### Banco de dados não conecta
```bash
# Verificar variáveis de ambiente
docker exec evaonline-api env | grep POSTGRES

# Testar conexão manualmente
docker exec evaonline-postgres psql -U evaonline -d evaonline -c "SELECT 1"
```

### Celery worker não processa
```bash
# Verificar logs
docker compose logs celery-worker

# Restart
docker compose restart celery-worker

# Limpar cache Redis
docker exec evaonline-redis redis-cli FLUSHDB
```

## 🎯 Plataformas Cloud Alternativas

### Railway.app (Recomendado - Mais Fácil)
1. Conectar repositório GitHub
2. Add PostgreSQL plugin
3. Add Redis plugin
4. Deploy automático em cada push
5. **Custo**: $5-10/mês

### Render.com
1. New Web Service → Docker
3. Add Redis
4. Deploy
5. **Custo**: $7-15/mês

### Fly.io
1. `fly launch`
2. Add Postgres: `fly postgres create`
3. Add Redis: `fly redis create`
4. `fly deploy`
5. **Custo**: $5-10/mês

## ✅ Pós-Deploy

- [ ] Aplicação acessível via HTTPS
- [ ] Testar todos os endpoints
- [ ] Verificar cálculo de ETo com fusão
- [ ] Monitorar logs por 24h
- [ ] Documentar URL de produção no README

## 📊 Performance

### Otimizações Já Implementadas:
- [x] Nginx como reverse proxy obrigatório
- [x] Rate limiting no Nginx (API, WebSocket, admin zones)
- [x] Gzip compression no Nginx
- [x] Cache de assets estáticos (_dash-component-suites)
- [x] Prometheus com pinned version (v2.54.1) e retention size 1GB
- [x] Grafana com pinned version (11.4.0) e sub-path /grafana/
- [x] Healthchecks em todos os serviços

### Otimizações Recomendadas:
- [ ] Habilitar SSL/TLS (Let's Encrypt)
- [ ] Habilitar HSTS header
- [ ] Configurar CDN (Cloudflare - grátis)
- [ ] Otimizar queries PostgreSQL (índices)
- [ ] Configurar IP whitelist para Grafana/Flower em produção

---

## 🆘 Suporte

- **Logs**: `docker compose logs -f --tail=100`
- **Shell no container**: `docker exec -it evaonline-api bash`
- **Restart rápido**: `docker compose restart api celery-worker`
- **Rebuild completo**: `docker compose down && docker compose build --no-cache && docker compose up -d`
