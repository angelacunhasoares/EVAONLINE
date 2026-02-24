# 📊 EVAonline — Monitoring & Observability

**Version:** 2.0  
**Last updated:** 2025-02-23

---

## Overview

EVAonline uses a **Prometheus + Grafana + Flower** stack for monitoring, all accessed through the **Nginx reverse proxy** (no direct port exposure).

## Access Points

| Tool | URL | Authentication |
|------|-----|---------------|
| **Grafana** | `http://localhost/grafana/` | admin / `GRAFANA_ADMIN_PASSWORD` |
| **Flower** | `http://localhost/flower/` | admin / `FLOWER_PASSWORD` |
| **Prometheus** | Internal only | Via Grafana → Explore |
| **API Health** | `http://localhost/api/v1/health` | None (public) |
| **API Health Detailed** | `http://localhost/api/v1/health/detailed` | None (public) |

> ⚠️ **Prometheus has no public URL.** Access metrics via Grafana or `docker exec`.

---

## Prometheus Configuration

### Scrape Targets

Only **3 jobs** are configured (matching services in `docker-compose.yml`):

| Job | Target | Interval | Metrics Path |
|-----|--------|----------|-------------|
| `prometheus` | `localhost:9090` | 15s | `/metrics` |
| `evaonline-api` | `api:8000` | 15s | `/metrics` |
| `flower` | `flower:5555` | 30s | `/flower/metrics` |

> **Note:** `postgres-exporter`, `redis-exporter`, and `node-exporter` are NOT deployed. Add them to `docker-compose.yml` first, then update `prometheus.yml`.

### Key Metrics

#### API Metrics (from FastAPI)
```promql
# Request rate (per second)
rate(http_requests_total[5m])

# Request latency (p95)
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# Error rate (5xx)
rate(http_requests_total{status=~"5.."}[5m])

# Active requests
http_requests_in_progress

# ETo calculations by mode
eto_calculations_total{mode="recent"}
eto_calculations_total{mode="historical"}
eto_calculations_total{mode="forecast"}

# Climate API calls by source
climate_api_requests_total{source="nasa_power", status="success"}
climate_api_requests_total{source="open_meteo", status="error"}
```

#### Celery Metrics (from Flower)
```promql
# Active workers
celery_workers_active

# Task count by state
celery_tasks_by_state{state="STARTED"}
celery_tasks_by_state{state="SUCCESS"}
celery_tasks_by_state{state="FAILURE"}
```

---

## Grafana Dashboards

### Pre-configured Dashboards

Located in `docker/monitoring/grafana/dashboards/`:

1. **EVAonline Metrics** (`evaonline-metrics.json`)
   - API request rate and latency
   - Error rates by endpoint
   - Active connections
   - Memory/CPU usage

2. **EVAonline User Dashboard** (`evaonline-user-dashboard.json`)
   - ETo calculations per mode
   - Data source usage distribution
   - Calculation success/failure rates
   - Average processing time

### Datasource

Prometheus is auto-provisioned as datasource via:
```
docker/monitoring/grafana/provisioning/datasources/prometheus.yml
```

Configuration:
```yaml
datasources:
  - name: Prometheus
    type: prometheus
    url: http://prometheus:9090
    access: proxy
    isDefault: true
```

---

## Health Checks

### Endpoints

```bash
# Basic health (is API running?)
curl http://localhost/api/v1/health
# {"status": "healthy", "timestamp": "..."}

# Detailed health (DB, Redis, Celery status)
curl http://localhost/api/v1/health/detailed
# {
#   "overall_status": "healthy",
#   "postgres": {"status": "healthy", "response_time_ms": 5.2},
#   "redis": {"status": "healthy", "response_time_ms": 2.1},
#   "celery": {"status": "healthy", "active_workers": 2},
#   "api": {"status": "healthy", "version": "1.0.0"}
# }

# Readiness probe (used by Docker health check)
curl http://localhost/api/v1/ready
# {"ready": true}
```

### Docker Health Checks

All services have configured health checks in `docker-compose.yml`:

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/ready"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

---

## Debugging

### View Container Status

```bash
docker compose ps
```

### Check Logs

```bash
# All services
docker compose logs --tail=30

# Specific service
docker compose logs api --tail=50
docker compose logs nginx --tail=30
docker compose logs celery-worker --tail=30
docker compose logs prometheus --tail=20
docker compose logs grafana --tail=20
```

### Query Prometheus Directly

```bash
# Check targets health
docker exec evaonline-prometheus wget -qO- http://localhost:9090/api/v1/targets

# Run a PromQL query
docker exec evaonline-prometheus wget -qO- \
  'http://localhost:9090/api/v1/query?query=up'
```

### Verify Grafana Datasource

```bash
docker exec evaonline-grafana wget -qO- \
  --header="Authorization: Basic $(echo -n admin:PASSWORD | base64)" \
  http://localhost:3000/grafana/api/datasources
```

---

## Alerting (Future)

Prometheus alerting rules and Alertmanager are not yet configured. To add:

1. Create `docker/monitoring/alert_rules.yml`
2. Add Alertmanager service to `docker-compose.yml`
3. Configure notification channels (email, Slack, etc.)

---

**Last updated:** 2025-02-23  
**Version:** 2.0