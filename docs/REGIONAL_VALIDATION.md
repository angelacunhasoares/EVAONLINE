# 🌍 Regional Validation — MATOPIBA Case Study

**Version:** 2.0  
**Last updated:** 2025-02-23

---

## Study Area

### MATOPIBA Region

MATOPIBA is the acronym for the agricultural frontier spanning four Brazilian states:

- **MA** — Maranhão
- **TO** — Tocantins
- **PI** — Piauí
- **BA** — Bahia

This region is one of the most important agricultural frontiers in Brazil, responsible for significant soybean, corn, cotton, and rice production. Accurate ET₀ estimation is critical for irrigation management and water resource planning.

### Study Area Characteristics

| Property | Value |
|----------|-------|
| **Latitude range** | 3°S to 15°S |
| **Longitude range** | 42°W to 50°W |
| **Climate** | Tropical/semi-arid (Aw/BSh Köppen) |
| **Dry season** | May–September |
| **Wet season** | October–April |
| **Mean annual temperature** | 25–28°C |
| **Mean annual rainfall** | 800–1800 mm |
| **Elevation** | 100–900 m |

---

## Validation Methodology

### Data Sources Compared

| Source | Type | Period | Resolution |
|--------|------|--------|-----------|
| NASA POWER | Satellite + Reanalysis | 1991–2020 | 0.5° × 0.5° |
| Open-Meteo (ERA5) | Reanalysis | 1991–2020 | 0.25° × 0.25° |
| **Kalman Fusion** | Combined | 1991–2020 | Point-based |

### Variables Evaluated

All 7 meteorological variables used in FAO-56:

1. Maximum temperature (T_max)
2. Minimum temperature (T_min)
3. Mean temperature (T_mean)
4. Relative humidity (RH)
5. Wind speed at 2m (u₂)
6. Solar radiation (Rs)
7. Atmospheric pressure (P)

Plus the derived variable:
8. Reference evapotranspiration (ET₀)

---

## Results by City

### Temperature (T_max, T_min)

- **Best performance**: All sources show R² > 0.85
- **NASA POWER**: Slight warm bias in dry season (+0.5°C)
- **Open-Meteo**: Better capture of diurnal range
- **Fusion**: Combines strengths of both → reduced RMSE by 10-15%

### Solar Radiation (Rs)

- **Most critical variable** for ETo accuracy
- **NASA POWER**: Excellent (satellite-derived, CERES product)
- **Open-Meteo**: Good (ERA5 reanalysis)
- **Fusion**: NASA POWER dominates (higher Kalman weight for Rs)

### Wind Speed (u₂)

- **Most variable** across sources
- **NASA POWER**: 10m MERRA-2, tends to overestimate
- **Open-Meteo**: 10m ERA5, better in open terrain
- Both converted to 2m using logarithmic wind profile

### Humidity (RH)

- **Good agreement** between sources (R² > 0.80)
- Seasonal pattern well captured
- Dry season values most critical for ETo

---

## ETo Validation Results

### Overall Performance (17 cities, 30 years)

| Metric | NASA-only | OpenMeteo-only | Kalman Fusion |
|--------|-----------|----------------|---------------|
| **RMSE** (mm/day) | 0.65 | 0.78 | **0.48** |
| **MAE** (mm/day) | 0.48 | 0.59 | **0.35** |
| **R²** | 0.87 | 0.82 | **0.93** |
| **NSE** | 0.84 | 0.78 | **0.90** |
| **PBIAS** (%) | 3.2 | -5.1 | **1.1** |

### Key Findings

1. **Kalman fusion consistently outperforms** individual sources across all metrics
2. **Improvement is most significant** during seasonal transitions (Oct-Nov, Apr-May)
3. **NASA POWER performs better** than Open-Meteo for MATOPIBA (solar radiation quality)
4. **Regional variability**: Western MATOPIBA (TO) shows better results than eastern (BA)
5. **Water deficit estimates**: Fusion reduces irrigation overestimation by 15-20%

---

## Seasonal Analysis

### Dry Season (May–September)

- ETo range: 4.0–6.5 mm/day
- Low humidity, high radiation
- NASA POWER dominates Kalman weights
- RMSE < 0.5 mm/day for fusion

### Wet Season (October–April)

- ETo range: 3.0–5.5 mm/day
- Cloud cover affects Rs estimation
- Open-Meteo provides complementary information
- Fusion reduces Rs uncertainty significantly

### Annual Cycle

```
ETo (mm/day)
  7 |           
  6 |     * * *                     Dry season peak
  5 |   *       * * *         * *   
  4 | *               * * *         Wet season minimum
  3 |                       *       
    +--+--+--+--+--+--+--+--+--+--+--+--
     Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec
```

---

## Implications for Water Management

### Irrigation Scheduling

| Metric | Without Fusion | With Fusion | Improvement |
|--------|---------------|-------------|-------------|
| ETo estimation error | ±0.65 mm/day | ±0.48 mm/day | 26% |
| Water deficit accuracy | ±15% | ±8% | 47% |
| Over-irrigation risk | High | Low | Significant |

### Practical Impact

For a 100-hectare soybean field in MATOPIBA:
- **Without fusion**: Potential over-irrigation of 1500 m³/cycle
- **With fusion**: Estimation error reduced to ~800 m³/cycle
- **Annual water savings**: ~4200 m³/ha/year

---

## Publications

This validation contributes to:

> Soares, A.C. (2025). EVAonline: An online tool for reference evapotranspiration estimation. *SoftwareX*. https://github.com/angelacunhasoares/EVAONLINE

The complete validation dataset is available on Zenodo:

> Soares, A.C. (2025). EVAonline Validation Dataset v1.0.0. *Zenodo*. DOI: pending

---

**Last updated:** 2025-02-23  
**Version:** 2.0