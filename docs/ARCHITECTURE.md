# 🏗️ EVAonline — Architecture Documentation

**Version:** 2.0.0  
**Last updated:** 2025-02-23  
**Status:** Production-ready

---

## 📋 Table of Contents

1. [System Overview](#system-overview)
2. [High-Level Architecture](#high-level-architecture)
3. [Service Architecture (Docker)](#service-architecture-docker)
4. [Backend Architecture](#backend-architecture)
5. [Frontend Architecture](#frontend-architecture)
6. [Data Flow](#data-flow)
7. [Climate Data Sources](#climate-data-sources)
8. [Kalman Filter Data Fusion](#kalman-filter-data-fusion)
9. [ETo Calculation (FAO-56)](#eto-calculation-fao-56)
10. [WebSocket Progress System](#websocket-progress-system)
11. [Download System](#download-system)
12. [Database & Caching](#database--caching)
13. [API Endpoints](#api-endpoints)
14. [Monitoring & Observability](#monitoring--observability)
15. [Security Architecture](#security-architecture)
16. [Directory Structure](#directory-structure)

---

## System Overview

EVAonline is a comprehensive web application for calculating reference evapotranspiration (ET₀) using the **FAO-56 Penman-Monteith** method. It integrates real-time meteorological data from **multiple global sources** using a **Kalman-filter data fusion** approach.

### Key Features
- **5 Climate Data Sources**: NASA POWER, Open-Meteo, MET Norway, NWS Forecast, NWS Stations
- **3 Calculation Modes**: Recent (7 days), Historical (custom range), Forecast (7 days)
- **Kalman Filter Fusion**: Optimal merging of multi-source data with quality weighting
- **Real-time Progress**: WebSocket-based progress tracking for long calculations
- **Per-table/chart Downloads**: CSV, Excel, PNG for each result component
- **Bilingual Interface**: Full EN/PT support with runtime switching
- **Water Deficit Analysis**: Irrigation requirement calculations
- **Interactive Maps**: Click-to-select location with Leaflet.js

### Technology Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | Dash 2.x + Plotly + dash-leaflet |
| **Backend API** | FastAPI 0.100+ + Uvicorn |
| **Task Queue** | Celery 5.x + Redis broker |
| **Database** | PostgreSQL 16 + SQLAlchemy 2.0 |
| **Cache** | Redis 7.x |
| **Reverse Proxy** | Nginx (single entry point) |
| **Monitoring** | Prometheus + Grafana + Flower |
| **Container** | Docker Compose (13 services) |

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        NGINX (port 80/443)                       │
│              Single public entry point + SSL termination          │
├──────────┬──────────────┬───────────────┬────────────────────────┤
│   /      │  /api/v1/*   │  /grafana/*   │  /flower/*             │
│  Dash UI │  FastAPI     │  Grafana      │  Flower                │
└────┬─────┴──────┬───────┴───────┬───────┴──────────┬─────────────┘
     │            │               │                  │
     ▼            ▼               ▼                  ▼
┌─────────┐ ┌──────────┐  ┌──────────┐        ┌──────────┐
│  Dash   │ │ FastAPI  │  │ Grafana  │        │  Flower  │
│ Frontend│ │ Backend  │  │ (3000)   │        │  (5555)  │
│ (8050)  │ │ (8000)   │  └────┬─────┘        └────┬─────┘
└────┬────┘ └────┬─────┘       │                    │
     │           │              │                    │
     │     ┌─────┴──────┐      │              ┌─────┴──────┐
     │     │  WebSocket  │      │              │   Celery   │
     │     │  /ws/eto/   │      │              │  Workers   │
     │     └─────┬───────┘      │              └─────┬──────┘
     │           │              │                    │
     ▼           ▼              ▼                    ▼
┌────────────────────────────────────────────────────────────┐
│                    Docker Internal Network                   │
│                    (evaonline-network)                        │
├──────────────┬──────────────┬────────────────────────────────┤
│  PostgreSQL  │    Redis     │         Prometheus             │
│   (5432)     │   (6379)     │          (9090)                │
│  + PostGIS   │  broker +    │   scrapes /metrics             │
│              │  cache       │   from API + Flower            │
└──────────────┴──────────────┴────────────────────────────────┘
```

---

## Service Architecture (Docker)

The application runs as **13 Docker services** defined in `docker-compose.yml`:

### Core Services

| Service | Image | Port | Role |
|---------|-------|------|------|
| `postgres` | postgres:16-alpine | 5432 (internal) | Primary database + PostGIS |
| `redis` | redis:7-alpine | 6379 (internal) | Celery broker + result cache |
| `api` | evaonline (custom) | 8000 (internal) | FastAPI backend + WebSocket |
| `dash` | evaonline (custom) | 8050 (internal) | Dash frontend application |
| `celery-worker` | evaonline (custom) | — | Async ETo calculation tasks |
| `celery-beat` | evaonline (custom) | — | Periodic task scheduler |
| `nginx` | nginx:1.25-alpine | **80 (public)** | Reverse proxy, rate limiting |

### Monitoring Services

| Service | Image | Port | Role |
|---------|-------|------|------|
| `prometheus` | prom/prometheus | 9090 (internal) | Metrics collection |
| `grafana` | grafana/grafana | 3000 (internal) | Dashboards & visualization |
| `flower` | mher/flower | 5555 (internal) | Celery task monitoring |

### Database Init Services

| Service | Role |
|---------|------|
| `db-init` | Creates initial schema + extensions |
| `db-migrate` | Runs Alembic migrations |
| `db-seed` | Seeds reference data |

### Key Design Decisions

1. **Only port 80/443 is public** — all other services use Docker internal network
2. **Nginx handles**: routing, rate limiting, security headers, static caching, gzip
3. **Health checks** on all services with restart policies
4. **Named volumes** for data persistence (postgres-data, redis-data, grafana-data)

---

## Backend Architecture

### Module Structure

```
backend/
├── api/
│   ├── main.py                    # FastAPI app factory
│   ├── routes/
│   │   ├── climate_routes.py      # Climate data endpoints
│   │   ├── eto_routes.py          # ETo calculation endpoints
│   │   ├── health_routes.py       # Health check endpoints
│   │   └── download_routes.py     # File download endpoints
│   ├── middleware/
│   │   ├── prometheus.py          # Prometheus metrics middleware
│   │   └── cors.py                # CORS configuration
│   └── websocket/
│       └── eto_websocket.py       # WebSocket progress handler
├── core/
│   ├── eto_calculator.py          # FAO-56 Penman-Monteith implementation
│   ├── kalman_fusion.py           # Kalman filter data fusion
│   ├── wind_height_correction.py  # Wind speed height adjustment
│   └── water_deficit.py           # Water deficit analysis
├── data_sources/
│   ├── base_source.py             # Abstract base class
│   ├── nasa_power.py              # NASA POWER API client
│   ├── open_meteo.py              # Open-Meteo API client
│   ├── met_norway.py              # MET Norway (Yr) API client
│   ├── nws_forecast.py            # NWS Forecast API client
│   ├── nws_stations.py            # NWS Stations API client
│   ├── source_manager.py          # Multi-source orchestration
│   └── elevation_service.py       # Elevation API (Open-Elevation)
├── infrastructure/
│   ├── celery/
│   │   ├── celery_config.py       # Celery app configuration
│   │   └── tasks.py               # Async ETo calculation tasks
│   ├── database/
│   │   ├── connection.py          # SQLAlchemy engine + sessions
│   │   └── models.py              # ORM models
│   ├── cache/
│   │   └── redis_client.py        # Redis cache operations
│   └── websocket/
│       └── manager.py             # WebSocket connection manager
├── services/
│   ├── eto_service.py             # ETo calculation orchestration
│   ├── climate_service.py         # Climate data service layer
│   └── download_service.py        # File generation (CSV, Excel, PNG)
├── schemas/
│   ├── eto_schemas.py             # Pydantic models for ETo
│   ├── climate_schemas.py         # Pydantic models for climate
│   └── common_schemas.py          # Shared response models
└── tests/
    ├── unit/                      # Unit tests
    ├── integration/               # Integration tests
    └── conftest.py                # Pytest fixtures
```

### Request Processing Flow

```
HTTP Request → Nginx → FastAPI Router → Service Layer → Data Sources
                                            │                │
                                            ▼                ▼
                                       Kalman Fusion ← API Responses
                                            │
                                            ▼
                                     ETo Calculator
                                            │
                                            ▼
                                    PostgreSQL + Redis Cache
                                            │
                                            ▼
                                     HTTP Response (JSON)
```

### Async Task Processing (Celery)

For long-running ETo calculations:

```
1. Client sends POST /api/v1/eto/calculate
2. FastAPI creates Celery task → returns task_id
3. Client connects WebSocket /ws/eto/{task_id}
4. Celery worker executes:
   a. Fetch data from 5 climate APIs (parallel)
   b. Apply Kalman filter fusion
   c. Calculate ETo for each day
   d. Store results in PostgreSQL
   e. Send progress updates via WebSocket (10%, 30%, 60%, 90%, 100%)
5. Client receives real-time progress + final results
```

---

## Frontend Architecture

### Module Structure

```
frontend/
├── app.py                          # Dash app initialization
├── main.py                         # Entry point
├── callbacks/
│   ├── __init__.py                 # Callback registration
│   ├── eto_callbacks.py            # Main ETo calculation callbacks
│   ├── download_callbacks.py       # Per-table/chart download handlers
│   ├── map_callbacks.py            # Map interaction callbacks
│   ├── language_callbacks.py       # Language switching (EN/PT)
│   └── ui_callbacks.py             # UI state management
├── components/
│   ├── map_component.py            # Leaflet map with click handler
│   ├── results_panel.py            # ETo results display
│   ├── download_buttons.py         # Download buttons per section
│   ├── header.py                   # App header with language toggle
│   ├── footer.py                   # Footer with links + license
│   └── input_panel.py              # Calculation parameters input
├── layouts/
│   ├── main_layout.py              # Main page layout
│   ├── documentation_layout.py     # Documentation page
│   ├── architecture_layout.py      # Architecture page
│   └── about_layout.py             # About page
├── pages/
│   ├── home.py                     # Dashboard (/)
│   ├── documentation.py            # Documentation (/documentation)
│   ├── architecture.py             # Architecture (/architecture)
│   └── about.py                    # About (/about)
└── assets/
    ├── styles.css                  # Main stylesheet
    ├── custom.js                   # Custom JavaScript
    └── images/                     # Static images
```

### Multi-Page Navigation

| Route | Page | Description |
|-------|------|-------------|
| `/` | Dashboard | Main ETo calculator with map |
| `/documentation` | Documentation | User guide, methodology, downloads |
| `/architecture` | Architecture | System architecture diagrams |
| `/about` | About | Project info, team, publications |

### Download System

Each results section has individual download buttons:

```
Results Panel
├── Summary Table         → [CSV] [Excel] [PNG]
├── Daily ETo Chart       → [PNG] [CSV]
├── Monthly Summary       → [CSV] [Excel] [PNG]
├── Data Sources Table    → [CSV] [Excel]
├── Water Deficit Chart   → [PNG] [CSV]
└── Full Report           → [Excel] (all sheets)
```

Downloads are generated server-side via `download_service.py` and served through Dash callbacks using `dcc.Download`.

---

## Data Flow

### Complete ETo Calculation Pipeline

```
┌──────────────────────────────────────────────────────────────────┐
│ STEP 1: User Input                                                │
│ • Latitude/Longitude (map click or manual)                        │
│ • Mode: Recent | Historical | Forecast                            │
│ • Date range (historical only)                                    │
│ • Language: EN | PT                                               │
└──────────┬───────────────────────────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────────────────────────┐
│ STEP 2: Elevation Retrieval                                       │
│ • Source: Open-Elevation API (open-elevation.com)                 │
│ • Fallback: Estimate from latitude                                │
│ • Cache: Redis (24h TTL)                                          │
└──────────┬───────────────────────────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────────────────────────┐
│ STEP 3: Multi-Source Climate Data Fetch (parallel)                │
│                                                                    │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐              │
│  │  NASA POWER   │ │  Open-Meteo  │ │ MET Norway   │              │
│  │  (Global)     │ │  (Global)    │ │ (Nordic opt.) │              │
│  │  Daily/hourly │ │  Archive +   │ │ Forecast      │              │
│  │  1981-present │ │  Forecast    │ │ 10 days       │              │
│  └──────┬───────┘ └──────┬───────┘ └──────┬───────┘              │
│         │                │                │                       │
│  ┌──────┴───────┐ ┌──────┴───────┐                               │
│  │ NWS Forecast │ │ NWS Stations │                                │
│  │  (US only)   │ │  (US only)   │                                │
│  │ 7-day fcst   │ │ Observations │                                │
│  └──────┬───────┘ └──────┬───────┘                               │
│         │                │                                        │
│         ▼                ▼                                        │
│  Each source returns standardized DataFrame:                      │
│  [date, temp_max, temp_min, temp_mean, humidity, wind_speed,      │
│   solar_radiation, pressure, precipitation, ...]                  │
└──────────┬───────────────────────────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────────────────────────┐
│ STEP 4: Data Quality Assessment                                   │
│ • Completeness check (% non-null per variable)                    │
│ • Physical range validation (e.g., temp -50 to +60°C)            │
│ • Temporal consistency (no future dates, sorted)                  │
│ • Source reliability scoring (NASA=0.9, OpenMeteo=0.85, etc.)     │
└──────────┬───────────────────────────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────────────────────────┐
│ STEP 5: Kalman Filter Data Fusion                                 │
│ • State vector: [T_max, T_min, T_mean, RH, u₂, R_s, P]         │
│ • Process noise Q: estimated from source variability              │
│ • Measurement noise R: per-source, per-variable                   │
│ • Innovation sequence: detects outliers                           │
│ • Output: optimal fused estimate + uncertainty                    │
│ (See "Kalman Filter Data Fusion" section for details)             │
└──────────┬───────────────────────────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────────────────────────┐
│ STEP 6: Wind Height Correction                                    │
│ • Convert wind speed to 2m reference height                       │
│ • Formula: u₂ = uz × [4.87 / ln(67.8z - 5.42)]                  │
│ • NASA POWER: z=10m, Open-Meteo: z=10m, others vary              │
└──────────┬───────────────────────────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────────────────────────┐
│ STEP 7: FAO-56 Penman-Monteith ETo Calculation                   │
│                                                                    │
│        0.408 Δ(Rn - G) + γ [900/(T+273)] u₂ (es - ea)           │
│ ETo = ─────────────────────────────────────────────────           │
│                     Δ + γ(1 + 0.34 u₂)                           │
│                                                                    │
│ Where:                                                             │
│   Rn = net radiation (from Rs, latitude, day of year)             │
│   G  = soil heat flux (≈0 for daily)                              │
│   Δ  = slope of vapor pressure curve                              │
│   γ  = psychrometric constant (from altitude/pressure)            │
│   es = saturation vapor pressure (from Tmax, Tmin)                │
│   ea = actual vapor pressure (from humidity or Tmin)              │
│   u₂ = wind speed at 2m height                                   │
└──────────┬───────────────────────────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────────────────────────┐
│ STEP 8: Water Deficit Analysis                                    │
│ • ETc = ETo × Kc (crop coefficient, user-defined or default)     │
│ • Water deficit = ETc - Effective Precipitation                   │
│ • Irrigation requirement = max(0, deficit)                        │
│ • Cumulative deficit over period                                  │
└──────────┬───────────────────────────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────────────────────────┐
│ STEP 9: Results & Storage                                         │
│ • Store in PostgreSQL (eto_calculations table)                    │
│ • Cache in Redis (TTL based on mode)                              │
│ • Return JSON via API / WebSocket                                 │
│ • Frontend renders: tables, charts, download buttons              │
└──────────────────────────────────────────────────────────────────┘
```

---

## Climate Data Sources

### Source Specifications

| Source | Coverage | Variables | Update Freq. | Latency |
|--------|----------|-----------|-------------|---------|
| **NASA POWER** | Global | T, RH, Wind, Rs, P, Precip | Daily | ~3 days |
| **Open-Meteo** | Global | T, RH, Wind, Rs, P, Precip | Hourly | Real-time |
| **MET Norway** | Global (forecast) | T, RH, Wind, Precip, Pressure | 6-hourly | Real-time |
| **NWS Forecast** | US only | T, RH, Wind, Precip | 12-hourly | Real-time |
| **NWS Stations** | US only | T, RH, Wind, Precip, Pressure | Hourly | ~1 hour |

### Source Implementation Details

Each source extends `BaseClimateSource` (abstract class):

```python
class BaseClimateSource(ABC):
    @abstractmethod
    async def fetch_data(
        self,
        latitude: float,
        longitude: float,
        start_date: date,
        end_date: date
    ) -> pd.DataFrame:
        """Fetch and return standardized climate data."""
        pass

    @abstractmethod
    def get_source_quality(self) -> float:
        """Return quality score 0-1 for Kalman filter weighting."""
        pass
```

### Variable Standardization

All sources map their native variables to a common schema:

| Standard Variable | Unit | NASA POWER | Open-Meteo | MET Norway |
|-------------------|------|------------|------------|------------|
| `temp_max` | °C | T2M_MAX | temperature_2m_max | air_temperature (max) |
| `temp_min` | °C | T2M_MIN | temperature_2m_min | air_temperature (min) |
| `temp_mean` | °C | T2M | temperature_2m_mean | computed |
| `humidity` | % | RH2M | relative_humidity_2m_mean | relative_humidity |
| `wind_speed` | m/s | WS10M | wind_speed_10m_max | wind_speed |
| `solar_radiation` | MJ/m²/day | ALLSKY_SFC_SW_DWN | shortwave_radiation_sum | — |
| `pressure` | kPa | PS | surface_pressure | air_pressure_at_sea_level |
| `precipitation` | mm | PRECTOTCORR | precipitation_sum | precipitation_amount |

### Elevation Service

- **Primary**: Open-Elevation API (`https://api.open-elevation.com/api/v1/lookup`)
- **Fallback**: Estimation from latitude using empirical formula
- **Cache**: Redis with 24-hour TTL
- **Used for**: Atmospheric pressure estimation when not available from sources

---

## Kalman Filter Data Fusion

### Overview

The Kalman filter optimally fuses data from multiple climate sources, accounting for:
- **Different measurement accuracies** per source
- **Missing data** (sources may fail or have gaps)
- **Temporal dynamics** of weather variables
- **Outlier detection** via innovation sequence

### Implementation (`backend/core/kalman_fusion.py`)

```python
class KalmanFusion:
    """
    Multi-source climate data fusion using Kalman filter.
    
    State vector x = [T_max, T_min, T_mean, RH, u₂, R_s, P]
    Each source provides a measurement z_k with noise R_k
    """
    
    def fuse(self, source_data: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """
        Fuse multiple source DataFrames into optimal estimate.
        
        For each day and variable:
        1. Predict: x̂⁻ = F·x̂⁺ₖ₋₁, P⁻ = F·P⁺ₖ₋₁·Fᵀ + Q
        2. For each source with data:
           a. Innovation: ỹ = z - H·x̂⁻
           b. Innovation covariance: S = H·P⁻·Hᵀ + R
           c. Kalman gain: K = P⁻·Hᵀ·S⁻¹
           d. Update: x̂⁺ = x̂⁻ + K·ỹ
           e. Update: P⁺ = (I - K·H)·P⁻
        3. Store fused estimate
        """
```

### Quality Weighting

Sources are weighted by their measurement noise covariance R:

| Source | Base Quality | R (noise) | Notes |
|--------|-------------|-----------|-------|
| NASA POWER | 0.90 | Low | Satellite + reanalysis, well-validated |
| Open-Meteo | 0.85 | Medium-Low | ERA5 reanalysis + forecast models |
| MET Norway | 0.80 | Medium | Good for Nordic, less tested elsewhere |
| NWS Forecast | 0.75 | Medium-High | Forecast only, US coverage |
| NWS Stations | 0.85 | Medium-Low | Ground observations, US only |

### Fusion Modes

| Mode | Sources Used | Strategy |
|------|-------------|----------|
| **Recent** | All available (real-time) | Full Kalman fusion |
| **Historical** | NASA POWER + Open-Meteo Archive | Dual-source fusion |
| **Forecast** | Open-Meteo + MET Norway + NWS | Forecast-weighted fusion |

---

## ETo Calculation (FAO-56)

### Implementation (`backend/core/eto_calculator.py`)

The FAO-56 Penman-Monteith equation:

$$
ET_0 = \frac{0.408 \Delta (R_n - G) + \gamma \frac{900}{T+273} u_2 (e_s - e_a)}{\Delta + \gamma (1 + 0.34 u_2)}
$$

### Intermediate Calculations

1. **Psychrometric constant** (γ):
   $$\gamma = \frac{c_p \cdot P}{\epsilon \cdot \lambda} = 0.665 \times 10^{-3} P$$

2. **Saturation vapor pressure** (es):
   $$e_s = \frac{e°(T_{max}) + e°(T_{min})}{2}$$
   where $e°(T) = 0.6108 \exp\left[\frac{17.27T}{T+237.3}\right]$

3. **Actual vapor pressure** (ea):
   $$e_a = \frac{RH_{mean}}{100} \cdot e_s$$

4. **Slope of vapor pressure curve** (Δ):
   $$\Delta = \frac{4098 \cdot e°(T_{mean})}{(T_{mean} + 237.3)^2}$$

5. **Net radiation** (Rn):
   - Net shortwave: $R_{ns} = (1 - \alpha) R_s$ where α = 0.23
   - Net longwave: $R_{nl} = \sigma \left[\frac{T_{max,K}^4 + T_{min,K}^4}{2}\right](0.34 - 0.14\sqrt{e_a})\left(1.35\frac{R_s}{R_{so}} - 0.35\right)$
   - Net radiation: $R_n = R_{ns} - R_{nl}$

6. **Extraterrestrial radiation** (Ra):
   - Computed from latitude and day of year
   - Used for clear-sky radiation: $R_{so} = (0.75 + 2 \times 10^{-5} z) R_a$

### Wind Height Correction

Wind speed must be adjusted to 2m reference height:

$$u_2 = u_z \cdot \frac{4.87}{\ln(67.8z - 5.42)}$$

| Source | Measurement Height | Correction Factor |
|--------|-------------------|-------------------|
| NASA POWER | 10m | 0.748 |
| Open-Meteo | 10m | 0.748 |
| MET Norway | 10m | 0.748 |
| NWS | varies | computed per station |

---

## WebSocket Progress System

### Architecture

```
Frontend (Dash)                    Backend (FastAPI)
     │                                    │
     │  1. POST /api/v1/eto/calculate     │
     │ ──────────────────────────────────► │
     │  ◄── { task_id: "abc-123" }        │
     │                                    │
     │  2. WS /ws/eto/abc-123             │
     │ ◄═══════════════════════════════►  │
     │                                    │
     │  3. Progress messages:             │
     │  ◄── { progress: 10, step: "Fetching NASA POWER..." }
     │  ◄── { progress: 30, step: "Fetching Open-Meteo..." }
     │  ◄── { progress: 60, step: "Applying Kalman fusion..." }
     │  ◄── { progress: 90, step: "Calculating ETo..." }
     │  ◄── { progress: 100, step: "Complete", data: {...} }
     │                                    │
     │  4. Connection closed              │
     │ ════════════════════════════════╝   │
```

### WebSocket Message Format

```json
{
    "type": "progress",
    "task_id": "abc-123",
    "progress": 60,
    "step": "Applying Kalman filter fusion...",
    "details": {
        "sources_completed": 3,
        "sources_total": 5,
        "current_source": "MET Norway"
    }
}
```

### Frontend Integration

The Dash frontend uses `DashWebSocketManager` (from `shared_utils/websocket_client.py`) to:
1. Connect to the WebSocket endpoint
2. Display progress bar with step description
3. Handle reconnection on connection loss
4. Parse final results and render charts/tables

---

## Download System

### Per-Component Downloads

Each results section generates downloads independently:

```python
# backend/services/download_service.py

class DownloadService:
    def generate_csv(self, data: pd.DataFrame, section: str) -> bytes:
        """Generate CSV for a specific results section."""
    
    def generate_excel(self, data: Dict[str, pd.DataFrame]) -> bytes:
        """Generate Excel with multiple sheets."""
    
    def generate_chart_png(self, figure: go.Figure) -> bytes:
        """Export Plotly chart as PNG image."""
```

### Available Downloads

| Section | CSV | Excel | PNG |
|---------|-----|-------|-----|
| Daily ETo Table | ✅ | ✅ | — |
| Daily ETo Chart | — | — | ✅ |
| Monthly Summary | ✅ | ✅ | — |
| Source Comparison | ✅ | ✅ | — |
| Water Deficit Chart | — | — | ✅ |
| Full Report | — | ✅ (multi-sheet) | — |

---

## Database & Caching

### PostgreSQL Schema

```sql
-- Core tables
CREATE TABLE eto_calculations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    latitude FLOAT NOT NULL,
    longitude FLOAT NOT NULL,
    elevation FLOAT,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    mode VARCHAR(20) NOT NULL,  -- 'recent', 'historical', 'forecast'
    sources_used TEXT[],
    created_at TIMESTAMP DEFAULT NOW(),
    results JSONB NOT NULL
);

CREATE TABLE climate_data_cache (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    latitude FLOAT NOT NULL,
    longitude FLOAT NOT NULL,
    source VARCHAR(50) NOT NULL,
    date DATE NOT NULL,
    data JSONB NOT NULL,
    fetched_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(latitude, longitude, source, date)
);
```

### Redis Caching Strategy

| Key Pattern | TTL | Content |
|-------------|-----|---------|
| `elevation:{lat}:{lon}` | 24h | Elevation in meters |
| `climate:{source}:{lat}:{lon}:{date}` | 6h | Raw climate data |
| `eto:{lat}:{lon}:{start}:{end}:{mode}` | 1h | Calculated ETo results |
| `task:{task_id}` | 24h | Celery task status |

---

## API Endpoints

### Health & Status

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/health` | Basic health check |
| GET | `/api/v1/health/detailed` | Detailed health (DB, Redis, Celery) |
| GET | `/api/v1/ready` | Readiness probe (Docker) |

### Climate Data

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/climate/sources/available` | List available sources |
| GET | `/api/v1/climate/data` | Fetch raw climate data |

### ETo Calculation

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/eto/calculate` | Start async ETo calculation |
| GET | `/api/v1/eto/result/{task_id}` | Get calculation result |
| WS | `/ws/eto/{task_id}` | WebSocket progress stream |

### Documentation

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/docs` | Swagger UI |
| GET | `/api/v1/redoc` | ReDoc documentation |
| GET | `/api/v1/openapi.json` | OpenAPI schema |

---

## Monitoring & Observability

### Prometheus Metrics

Collected from API (`:8000/metrics`) and Flower (`:5555/flower/metrics`):

- `http_requests_total{method, endpoint, status}` — Request count
- `http_request_duration_seconds{method, endpoint}` — Request latency (histogram)
- `http_requests_in_progress` — Active requests (gauge)
- `eto_calculations_total{mode, status}` — ETo calculations count
- `climate_api_requests_total{source, status}` — External API calls
- `celery_tasks_active_total` — Active Celery tasks

### Grafana Dashboards

Pre-configured dashboards in `docker/monitoring/grafana/dashboards/`:

1. **EVAonline Metrics** — API latency, error rates, throughput
2. **User Dashboard** — ETo calculations per mode, source usage

### Access Points (all via Nginx)

| Tool | URL | Auth |
|------|-----|------|
| Grafana | `http://localhost/grafana/` | admin / (from .env) |
| Flower | `http://localhost/flower/` | admin / (from .env) |
| Prometheus | Internal only | Via Grafana Explore |

---

## Security Architecture

### Network Security

- **Single entry point**: Only Nginx port 80/443 is publicly accessible
- **Internal network**: All services communicate via Docker bridge network
- **No direct DB/Redis access**: PostgreSQL (5432) and Redis (6379) are internal only

### Application Security

- **Rate limiting**: 30 req/s general, 5 req/s for API calculations (Nginx)
- **CORS**: Configurable allowed origins
- **Security headers**: X-Frame-Options, X-Content-Type-Options, X-XSS-Protection
- **Input validation**: Pydantic schemas on all API inputs
- **/metrics blocked**: Prometheus metrics endpoint returns 404 via Nginx

### Authentication

- **Grafana**: Username/password (configured in `.env`)
- **Flower**: HTTP Basic Auth (configured in `.env`)
- **API**: Currently open (designed for public use)

### Secrets Management

- All secrets in `.env` file (not committed to git)
- `.env.example` provides template with placeholder values
- Docker Compose reads secrets from `.env` at build/run time

---

## Directory Structure

```
EVAONLINE/
├── alembic/                    # Database migrations
│   ├── versions/               # Migration scripts
│   └── env.py                  # Alembic configuration
├── backend/                    # Python backend
│   ├── api/                    # FastAPI routes + middleware
│   ├── core/                   # Business logic (ETo, Kalman, Wind)
│   ├── data_sources/           # Climate API clients
│   ├── infrastructure/         # Celery, DB, Redis, WebSocket
│   ├── services/               # Service layer
│   ├── schemas/                # Pydantic models
│   └── tests/                  # Unit + integration tests
├── config/                     # Configuration
│   ├── settings/               # App settings (Pydantic)
│   ├── translations/           # EN/PT JSON translations
│   └── logging_config.py       # Logging setup
├── data/                       # Static data files
├── database/                   # DB config (pg_hba, postgresql.conf)
├── docker/                     # Docker configs
│   ├── monitoring/             # Prometheus + Grafana configs
│   │   ├── prometheus.yml      # Prometheus scrape config
│   │   └── grafana/            # Grafana provisioning + dashboards
│   └── nginx/                  # Nginx configuration
│       ├── nginx.conf          # Main Nginx config
│       └── ssl/                # SSL certificates (gitignored)
├── docs/                       # Technical documentation
├── frontend/                   # Dash application
│   ├── callbacks/              # Dash callbacks
│   ├── components/             # UI components
│   ├── layouts/                # Page layouts
│   ├── pages/                  # Multi-page routing
│   └── assets/                 # CSS, JS, images
├── init-db/                    # Database initialization scripts
├── scripts/                    # Utility scripts
├── shared_utils/               # Shared frontend/backend utilities
├── docker-compose.yml          # 13-service orchestration
├── Dockerfile                  # Multi-stage build
├── pyproject.toml              # Project metadata + dependencies
├── requirements.txt            # Locked dependencies
└── README.md                   # Project README
```

---

**Last updated:** 2025-02-23  
**Version:** 2.0.0  
**Maintained by:** EVAonline Development Team