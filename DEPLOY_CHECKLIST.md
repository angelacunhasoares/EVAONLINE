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
  POSTGRES_PASSWORD=$(openssl rand -base64 32)
  REDIS_PASSWORD=$(openssl rand -base64 32)
  SECRET_KEY=$(openssl rand -base64 32)
  ```
- [ ] Adicionar `.env` ao `.gitignore` (já deve estar)
- [ ] Configurar firewall no servidor (apenas portas 22, 80, 443)
- [ ] Habilitar fail2ban para proteção SSH

## 🌐 Servidor (VPS)

- [ ] Servidor Ubuntu 22.04+ com Docker instalado
- [ ] Domínio configurado (DNS apontando para IP do servidor)
- [ ] Certificado SSL (Let's Encrypt com Certbot)
- [ ] Nginx como reverse proxy (opcional mas recomendado)

### Requisitos Mínimos:
- **CPU**: 2 vCPUs
- **RAM**: 4 GB (2 GB para api + 1 GB para Celery + 1 GB para PostgreSQL/Redis)
- **Disco**: 20 GB SSD
- **Custo**: ~$12-20/mês (DigitalOcean, Linode, Vultr)

## 📦 Deploy Steps

### 1. Preparar Servidor
```bash
# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Instalar docker-compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 2. Clonar Repositório
```bash
git clone https://github.com/seu-usuario/EVAONLINE.git
cd EVAONLINE
```

### 3. Configurar Ambiente
```bash
# Criar .env
cp .env.example .env  # Se existir
# OU criar manualmente:
cat > .env << 'EOF'
POSTGRES_PASSWORD=<senha_forte_aqui>
POSTGRES_USER=evaonline
POSTGRES_DB=evaonline
REDIS_PASSWORD=<senha_forte_aqui>
DOMAIN=seu-dominio.com
EOF
```

### 4. Deploy
```bash
# Build e start
docker-compose up -d

# Verificar logs
docker-compose logs -f api celery-worker

# Verificar saúde dos serviços
docker-compose ps
```

### 5. Configurar Nginx (Opcional)
```bash
# Instalar Certbot para SSL
sudo apt install certbot python3-certbot-nginx

# Obter certificado
sudo certbot --nginx -d seu-dominio.com

# Nginx configurado automaticamente com HTTPS
```

## 🔍 Monitoramento

- [ ] Configurar logs persistentes: `volumes: - ./logs:/app/logs`
- [ ] Monitorar uso de recursos: `docker stats`
- [ ] Configurar alertas (opcional): Prometheus + Grafana
- [ ] Backup automático do PostgreSQL:
  ```bash
  # Cron job diário
  0 2 * * * docker exec evaonline-postgres pg_dump -U evaonline evaonline | gzip > /backups/evaonline_$(date +\%Y\%m\%d).sql.gz
  ```

## 🚨 Troubleshooting

### Container não inicia
```bash
docker-compose logs <service_name>
docker-compose down && docker-compose up -d
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
docker-compose logs celery-worker

# Restart
docker-compose restart celery-worker

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
2. Add PostgreSQL database
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

### Otimizações Recomendadas:
- [ ] Habilitar cache HTTP (Redis)
- [ ] Configurar CDN (Cloudflare - grátis)
- [ ] Otimizar queries PostgreSQL (índices)
- [ ] Rate limiting no Nginx
- [ ] Gzip compression no Nginx

---

## 🆘 Suporte

- **Logs**: `docker-compose logs -f --tail=100`
- **Shell no container**: `docker exec -it evaonline-api bash`
- **Restart rápido**: `docker-compose restart api celery-worker`
- **Rebuild completo**: `docker-compose down && docker-compose build --no-cache && docker-compose up -d`
