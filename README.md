<table>
<tr>
  <td width="200">
    <img src="frontend/assets/images/logo_evaonline_png.png" alt="EVAonline Logo" width="200">
  </td>
  <td>
    🌦️ <strong>EVAonline</strong> is a comprehensive web application for calculating reference evapotranspiration (ET₀) using the <strong>FAO-56 Penman-Monteith</strong> method. It employs a sophisticated <strong>Kalman-filter data fusion</strong> approach, integrating real-time meteorological data from multiple global sources (NASA POWER, Open-Meteo, MET Norway, and the U.S. National Weather Service). Built with Dash + FastAPI, it provides interactive dashboards, real-time WebSocket progress tracking, per-table/chart downloads, water-deficit analysis, and full bilingual support (EN/PT).
  </td>
</tr>
</table>

---

## 🏗️ Architecture

### Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | Dash 3, Dash Bootstrap Components, dash-leaflet, Plotly 6 |
| **Backend** | FastAPI, Celery (3 worker types), Redis Pub/Sub |
| **Database** | PostgreSQL 16 + PostGIS 3.4, Alembic migrations |
| **Cache** | Redis 7 (caching + message broker) |
| **Infra** | Docker Compose (13 services), Nginx, Prometheus + Grafana |
| **i18n** | JSON-based translations (EN / PT) |
| **CI/Quality** | pytest, black, flake8, mypy, pre-commit |

### Service Map (Docker Compose)

```
┌──────────────┐  ┌──────────────┐  ┌──────────────────┐
│   Nginx      │→ │  API (Dash + │→ │  PostgreSQL 16   │
│  (reverse    │  │  FastAPI +   │  │  + PostGIS 3.4   │
│   proxy)     │  │  Uvicorn)    │  └──────────────────┘
└──────────────┘  └──────┬───────┘           ↑
                         │ WebSocket         │ Alembic
                         ↓                   │
                  ┌──────────────┐  ┌────────┴─────────┐
                  │  Redis 7     │← │  Celery Workers   │
                  │  (cache +    │  │  • general        │
                  │   broker)    │  │  • eto-dedicated  │
                  └──────────────┘  │  • beat scheduler │
                         ↑         └────────────────────┘
                  ┌──────┴───────┐
                  │   Flower     │  (Celery monitoring UI)
                  └──────────────┘
                  ┌──────────────┐  ┌──────────────┐
                  │  Prometheus  │→ │   Grafana    │
                  └──────────────┘  └──────────────┘
```

---

## 📁 Project Structure

```
EVAONLINE/
├── backend/                    # Backend application
│   ├── api/                   # FastAPI layer
│   │   ├── routes/            # REST endpoints (ETo, health, geolocation, visitors, climate)
│   │   ├── websocket/         # WebSocket service (real-time task progress)
│   │   ├── middleware/        # Request middleware
│   │   └── services/          # API business services
│   ├── core/                  # Core business logic
│   │   ├── data_processing/   # Kalman filters, climate fusion, ensemble, limits
│   │   ├── data_results/      # Result graphs, tables, statistics, layout
│   │   ├── eto_calculation/   # FAO-56 PM ETo engine
│   │   ├── analytics/         # Data analytics
│   │   └── utils/             # Backend utilities
│   ├── database/              # SQLAlchemy models & connections
│   ├── infrastructure/        # Cache, Celery workers, loaders, visitor tracking
│   └── tests/                 # Backend tests
├── frontend/                   # Dash application
│   ├── app.py                 # Main Dash app entry point
│   ├── pages/                 # Page components (home, documentation, architecture, about)
│   ├── callbacks/             # Dash callbacks (ETo, home, navbar, navigation, cache, visitor)
│   ├── components/            # Reusable components (navbar, footer, map, info cards)
│   ├── services/              # Frontend services
│   ├── assets/                # Static files (CSS, JS, images)
│   ├── utils/                 # Frontend utilities
│   └── tests/                 # Frontend tests
├── config/                     # Configuration
│   ├── settings/              # App settings (dev, prod, test)
│   ├── translations/          # i18n files (en.json, pt.json)
│   └── logging_config.py      # Loguru configuration
├── shared_utils/               # Shared modules (translations, logging, WebSocket client)
├── data/                       # Data assets
│   ├── csv/                   # Preloaded CSV datasets
│   ├── geojson/               # GeoJSON boundaries
│   ├── historical/            # Historical climate data
│   └── scripts/               # Data preparation scripts
├── database/                   # DB config, init scripts, seed data
├── alembic/                    # Database migrations
├── scripts/                    # Operational scripts (coverage, sync, validation)
├── docker/                     # Docker configs (backend, nginx, monitoring)
├── docs/                       # Technical documentation
├── EVAonline_validation_v1.0.0/ # Independent validation package
├── docker-compose.yml          # 13-service orchestration
├── Dockerfile                  # Multi-stage build (builder + runtime)
├── pyproject.toml              # Project metadata & dependencies
└── requirements.txt            # Locked dependencies (uv pip compile)
```

---

## 📊 Features

### ETo Calculation Engine
- **FAO-56 Penman-Monteith** method with all required climate variables
- **7 input variables**: Tmax, Tmin, Tmean (°C), relative humidity (%), wind speed at 2 m (m/s), solar radiation (MJ/m²/day), precipitation (mm)
- **3 operation modes**: Dashboard (quick), Forecast (6-day), Historical (any period, async via email)
- **Automatic ocean/water body detection** — blocks invalid calculations

### Data Fusion (Kalman Filters)
- **Multi-source integration**: NASA POWER + Open-Meteo + regional sources
- **Kalman Ensemble filter**: optimal weighting of concurrent data sources
- **Climate limits validation**: automatic QC with plausible-range checks
- **Fusion modes**: Full Kalman / Simple average / Single source (auto-selected)

### Regional Specialized Sources
| Region | Source | Details |
|---|---|---|
| **Global** | NASA POWER, Open-Meteo | Satellite + reanalysis data |
| **Europe** | MET Norway (Frost API) | High-resolution station data |
| **USA** | National Weather Service | Real-time NWS station card with distance, elevation, last observation |
| **Brazil / MATOPIBA** | Open-Meteo + historical validation | Validated against Xavier's gridded dataset |

### Results & Analysis
- **Summary tab**: ETo totals, water balance, data sources, fusion mode, irrigation recommendations
- **Data tables**: daily climate data, ETo summary, descriptive statistics, normality test — each with individual **CSV & Excel download** buttons
- **5 interactive charts** (Plotly): ETo vs Temperature, ETo vs Radiation, Temperature & Precipitation, Water Deficit, Correlation Heatmap — each with **PNG & JPG download** buttons
- **Statistical analysis**: mean, median, SD, quartiles, IQR, CV%, skewness, kurtosis, Shapiro-Wilk normality test, trend analysis
- **30-day minimum rule**: CV%, skewness, kurtosis, Shapiro-Wilk, and correlation heatmap require ≥30 days of data
- **Water deficit analysis**: daily water balance (P − ETo), deficit/surplus days, cumulative deficit, interactive area chart
- **ETo comparison**: EVAonline ETo vs Open-Meteo reference ETo side-by-side
- **Locale-aware exports**: PT (`;` separator, `,` decimal) / EN (`,` separator, `.` decimal)

### Visualization & Maps
- **Interactive world map**: dash-leaflet with OpenStreetMap tiles
- **GeoJSON layers**: country/region boundaries
- **City heatmap**: kernel density estimation
- **Real-time progress**: WebSocket-powered task tracking with translated status messages

### Internationalization (i18n)
- Full **English** and **Portuguese** support
- Language toggle in navbar (persisted in dcc.Store)
- All UI strings, progress messages, NWS station cards, error messages, and documentation pages translated

### Performance & Infrastructure
- **Redis caching**: sub-second responses for repeated queries
- **3 Celery worker types**: general, ETo-dedicated, beat scheduler
- **Flower**: web UI for Celery task monitoring
- **Prometheus + Grafana**: API metrics, response times, cache hit rates
- **Structured logging**: Loguru with configurable levels
- **Health checks**: `/health`, `/health/detailed`, `/ready` endpoints

---

## 🚀 Getting Started

### Prerequisites

- **Docker** and **Docker Compose** v2+
- **Python 3.12+** (for local development)
- **Git**

### Quick Start (Docker)

```bash
# 1. Clone
git clone https://github.com/angelacunhasoares/EVAONLINE.git
cd EVAONLINE

# 2. Configure environment
cp .env.example .env
# Edit .env with your database passwords and API keys

# 3. Build and start all services
docker compose up --build -d

# 4. Access the application
#    Dashboard:    http://localhost
#    API docs:     http://localhost/api/v1/docs
#    Grafana:      http://localhost/grafana/
#    Flower:       http://localhost/flower/
#    Adminer:      http://localhost:5050  (dev profile only)
```

### Local Development

```bash
# Install dependencies (requires Python 3.12+)
pip install -e ".[dev]"

# Start only database + cache
docker compose up postgres redis -d

# Run API server
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# Run Celery worker
celery -A backend.infrastructure.celery worker --loglevel=info

# Run tests
pytest backend/tests/ frontend/tests/ -v
```

---

## 🔧 Configuration

### Environment Variables

Key configuration options in `.env`:

| Variable | Description |
|---|---|
| `POSTGRES_*` | PostgreSQL connection settings |
| `REDIS_*` | Redis cache and broker settings |
| `FASTAPI_*` | API server configuration |
| `DASH_*` | Dashboard application settings |
| `CELERY_*` | Worker concurrency and queues |
| `SECRET_KEY` | Application secret for sessions |

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/eto/calculate` | Submit ETo calculation task |
| `POST` | `/api/eto/location-info` | Get location metadata (elevation, timezone) |
| `GET` | `/api/climate-sources` | List available climate data sources |
| `WebSocket` | `/ws/task_status/{task_id}` | Real-time task progress updates |
| `GET` | `/health` | Basic health check |
| `GET` | `/health/detailed` | Detailed health (DB, Redis, Celery) |
| `GET` | `/ready` | Readiness probe |

---

## 📈 Monitoring

- **Nginx**: reverse proxy, rate limiting, security headers, SSL termination
- **Prometheus** (internal only): collects API response times, request counts, error rates, cache metrics
- **Grafana** (`/grafana/`): pre-configured dashboards for system performance (auth required)
- **Flower** (`/flower/`): Celery task monitoring with basic auth (queue depth, worker status, task history)
- **Loguru**: structured application logs with rotation
- **Health endpoints**: `/api/v1/health`, `/api/v1/health/detailed`, `/api/v1/ready`

> **Security**: Only Nginx exposes public ports (80/443). Prometheus, Grafana, Flower, PostgreSQL, and Redis are accessible only via internal Docker network.

---

## 🧪 Validation

The `EVAonline_validation_v1.0.0/` directory contains an **independent validation package** with:
- Complete validation analysis notebook
- Tutorial pipeline notebook
- Validation scripts and reference data
- Reproducible environment (`environment.yml`, `requirements.txt`)
- Citation file (`CITATION.cff`)

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

---

## 📄 License

This project is licensed under the **GNU Affero General Public License v3.0** (AGPL-3.0). See the [LICENSE](LICENSE) file for details.

---

## 🎯 Citation

If you use EVAonline in your research, please cite:

```bibtex
@article{evaonline2025,
  title     = {EVAonline: An online tool for reference evapotranspiration estimation},
  author    = {Soares, Silviane Angela Cunha},
  journal   = {SoftwareX},
  year      = {2025},
  url       = {https://github.com/angelacunhasoares/EVAONLINE}
}
```

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/angelacunhasoares/EVAONLINE/issues)
- **Contact**: angelassilviane@gmail.com

---

Built with ❤️ for the agricultural and environmental research community.