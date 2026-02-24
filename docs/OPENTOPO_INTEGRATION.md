# 🏔️ Elevation Service — Integration Documentation

**Version:** 2.0  
**Last updated:** 2025-02-23

---

## Overview

EVAonline requires elevation data at the user-selected coordinates to compute atmospheric pressure (when not available from climate sources) and to apply altitude corrections in the FAO-56 Penman-Monteith equation.

---

## Current Implementation

### Primary Source: Open-Elevation API

| Property | Value |
|----------|-------|
| **API** | Open-Elevation (open-source) |
| **URL** | `https://api.open-elevation.com/api/v1/lookup` |
| **Dataset** | SRTM 30m (Shuttle Radar Topography Mission) |
| **Coverage** | Global (60°S to 60°N) |
| **Resolution** | ~30m (1 arc-second) |
| **Cost** | Free, no API key required |
| **Rate Limit** | Fair use (no formal limit) |

### Implementation (`backend/data_sources/elevation_service.py`)

```python
class ElevationService:
    """
    Fetches elevation data for coordinates.
    
    Primary: Open-Elevation API
    Fallback: Latitude-based estimation
    Cache: Redis with 24h TTL
    """
    
    API_URL = "https://api.open-elevation.com/api/v1/lookup"
    
    async def get_elevation(self, lat: float, lon: float) -> float:
        # 1. Check Redis cache
        cached = await self.cache.get(f"elevation:{lat}:{lon}")
        if cached:
            return float(cached)
        
        # 2. Query Open-Elevation API
        try:
            response = await self.client.get(
                self.API_URL,
                params={"locations": f"{lat},{lon}"}
            )
            elevation = response.json()["results"][0]["elevation"]
        except Exception:
            # 3. Fallback: estimate from latitude
            elevation = self._estimate_from_latitude(lat)
        
        # 4. Cache result (24h)
        await self.cache.set(
            f"elevation:{lat}:{lon}",
            elevation,
            ex=86400
        )
        return elevation
```

### Fallback: Latitude-Based Estimation

When the API is unavailable, elevation is estimated using an empirical formula based on latitude. This provides a reasonable approximation for atmospheric pressure calculations.

```python
def _estimate_from_latitude(self, lat: float) -> float:
    """
    Rough elevation estimate based on latitude.
    Returns mean elevation for the latitude band.
    """
    # Global mean elevation ~800m
    # Tropical regions tend to be lower
    # Temperate regions vary more
    abs_lat = abs(lat)
    if abs_lat < 15:
        return 300.0  # Tropical lowlands
    elif abs_lat < 30:
        return 500.0  # Subtropical
    elif abs_lat < 45:
        return 400.0  # Temperate
    else:
        return 200.0  # High latitude
```

---

## Usage in ETo Calculation

### Atmospheric Pressure

When pressure is not available from climate sources, it is estimated from elevation:

$$P = 101.3 \left(\frac{293 - 0.0065 \cdot z}{293}\right)^{5.26}$$

Where:
- $P$ = atmospheric pressure (kPa)
- $z$ = elevation above sea level (m)

### Psychrometric Constant

Pressure is used to calculate the psychrometric constant:

$$\gamma = 0.665 \times 10^{-3} \cdot P$$

### Clear-Sky Radiation

Elevation affects the clear-sky solar radiation:

$$R_{so} = (0.75 + 2 \times 10^{-5} \cdot z) \cdot R_a$$

---

## Caching Strategy

| Key Pattern | TTL | Purpose |
|------------|-----|---------|
| `elevation:{lat}:{lon}` | 24 hours | Avoid repeated API calls |

Elevation is static (terrain doesn't change), so aggressive caching is appropriate. The 24h TTL is a balance between freshness and API courtesy.

---

## Error Handling

| Scenario | Action |
|----------|--------|
| API timeout (>10s) | Use fallback estimation |
| API returns error | Use fallback estimation |
| API rate limited | Use fallback estimation |
| Invalid coordinates | Return 0m with warning |
| Cache miss | Query API → cache result |

---

## Future Improvements

- [ ] Add OpenTopography API as secondary source (requires API key)
- [ ] Add GMRT (Global Multi-Resolution Topography) for ocean/coastal areas
- [ ] Allow user to manually input elevation
- [ ] Store elevation in PostgreSQL for frequently queried locations

---

**Last updated:** 2025-02-23  
**Version:** 2.0