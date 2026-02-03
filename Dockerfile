# ===========================================
# MULTI-STAGE DOCKERFILE - EVAonline OTIMIZADO
# Usa pyproject.toml como única fonte de dependências
# ===========================================

# ===========================================
# Stage 1: Builder - Production Dependencies
# ===========================================
FROM python:3.12-slim AS builder-prod

# Metadata para melhor rastreabilidade da imagem
LABEL maintainer="Ângela Cunha Soares <angelassilviane@gmail.com>"
LABEL stage="builder-prod"
LABEL description="Builder stage for production dependencies"

# Configurar diretório de trabalho para o build
WORKDIR /build

# Copiar apenas os arquivos necessários para instalar dependências
COPY pyproject.toml ./
COPY requirements.txt ./

# Instalar dependências de compilação APENAS para build
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libgdal-dev \
    libgeos-dev \
    libproj-dev \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependências de produção usando requirements.txt em diretório isolado
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --target /dependencies -r requirements.txt

# ===========================================
# Stage 1B: Builder - Development Dependencies
# ===========================================
FROM builder-prod AS builder-dev

LABEL stage="builder-dev"

# Instalar dependências de desenvolvimento do pyproject.toml
# [dev] refere-se à seção project.optional-dependencies no pyproject.toml
RUN pip install --no-cache-dir --user .[dev]

# ===========================================
# Stage 2: Runtime (Production) - IMAGEM FINAL LEVE
# ===========================================
FROM python:3.12-slim AS runtime

# Metadata da imagem final
LABEL maintainer="Ângela Cunha Soares <angelassilviane@gmail.com>"
LABEL stage="runtime"
LABEL description="Production runtime image for EVAonline"

# Instalar APENAS dependências essenciais de runtime
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Runtime do PostgreSQL
    libpq5 \
    # Bibliotecas geoespaciais
    libgdal36 \
    libgeos-c1t64 \
    libproj25 \
    # Para health checks e scripts
    curl \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Criar usuário não-root para segurança
RUN useradd -m -u 1000 -s /bin/bash evaonline


# Configurar variáveis de ambiente para otimização Python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app:/dependencies \
    PATH="/dependencies/bin:${PATH}" \
    TZ=America/Sao_Paulo

WORKDIR /app

# Criar diretórios ANTES de copiar arquivos
RUN mkdir -p /app/logs /app/data /app/temp && \
    chown -R evaonline:evaonline /app

# Copiar APENAS dependências de produção (não inclui dev tools)
COPY --from=builder-prod --chown=evaonline:evaonline /dependencies /dependencies

# Copiar código em ordem estratégica para cache
# Arquivos que mudam pouco primeiro (melhor cache)
COPY --chown=evaonline:evaonline pyproject.toml .
COPY --chown=evaonline:evaonline alembic.ini .
COPY --chown=evaonline:evaonline pytest.ini .

# Copiar entrypoint (como root para definir permissões)
USER root
COPY --chown=root:root docker/backend/entrypoint.sh /entrypoint.sh
COPY --chown=root:root docker/backend/healthcheck.sh /healthcheck.sh
RUN chmod 755 /entrypoint.sh /healthcheck.sh && \
    dos2unix /entrypoint.sh /healthcheck.sh 2>/dev/null || sed -i 's/\r$//' /entrypoint.sh /healthcheck.sh

# Arquivos que mudam com média frequência
COPY --chown=evaonline:evaonline config/ ./config/
COPY --chown=evaonline:evaonline alembic/ ./alembic/
COPY --chown=evaonline:evaonline shared_utils/ ./shared_utils/

# Arquivos que mudam frequentemente (últimos - pior cache)
COPY --chown=evaonline:evaonline backend/ ./backend/
COPY --chown=evaonline:evaonline frontend/ ./frontend/

# Mudar para usuário não-root para segurança
USER evaonline

# Expor porta padrão da aplicação
EXPOSE 8000

# Health check adaptado ao tipo de serviço
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD /healthcheck.sh

# Entrypoint para inicialização flexível
ENTRYPOINT ["/entrypoint.sh"]

# Comando padrão para produção
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]

# ===========================================
# Stage 3: Development - Hot Reload e Debug
# ===========================================
FROM runtime AS development

LABEL stage="development"
LABEL description="Development image com hot-reload"

# Copiar dependências de desenvolvimento SOBRESCREVENDO produção
COPY --from=builder-dev --chown=evaonline:evaonline /dependencies-dev /dependencies

USER evaonline

# Variáveis de ambiente para desenvolvimento
ENV RELOAD=true \
    ENVIRONMENT=development \
    LOG_LEVEL=DEBUG \
    PYTHONPATH=/app:/dependencies

# Comando padrão para desenvolvimento com hot-reload
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# ===========================================
# Stage 4: Testing - Ambiente de Testes
# ===========================================
FROM development AS testing

LABEL stage="testing"
LABEL description="Testing image com pytest"

# Instalar ferramentas adicionais para testes
USER root

RUN apk add --no-cache \
    # Ferramentas para testes de integração
    postgresql-client \
    redis

USER evaonline

# Copiar testes
COPY --chown=evaonline:evaonline backend/tests/ ./backend/tests/

# Copiar entrypoint dos testes (se existir)
COPY --chown=evaonline:evaonline docker/docker-entrypoint-tests.sh /entrypoint-tests.sh
RUN chmod +x /entrypoint-tests.sh

# Variáveis de ambiente para testes
ENV ENVIRONMENT=testing \
    TESTING=true

# Entrypoint para execução de testes
ENTRYPOINT ["/entrypoint-tests.sh"]

# Fallback para execução direta de testes
CMD ["pytest", "-v", "--tb=short", "--color=yes"]
