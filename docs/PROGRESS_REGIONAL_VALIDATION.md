# 📊 Validation Progress — EVAonline

**Version:** 2.0  
**Last updated:** 2025-02-23

---

## Overview

EVAonline has been validated using a comprehensive dataset covering the MATOPIBA region in Brazil (a major agricultural frontier spanning Maranhão, Tocantins, Piauí, and Bahia states).

## Validation Dataset

**Status:** ✅ Complete — Published on Zenodo

| Property | Value |
|----------|-------|
| **Package** | EVAonline Validation v1.0.0 |
| **Cities** | 17 (across 4 states) |
| **Period** | 1991–2020 (30 years) |
| **Repository** | Zenodo (DOI: pending) |
| **License** | MIT |

### Cities Validated

| # | City | State | Lat | Lon |
|---|------|-------|-----|-----|
| 1 | Alvorada do Gurguéia | PI | -8.42 | -43.78 |
| 2 | Araguaína | TO | -7.19 | -48.21 |
| 3 | Balsas | MA | -7.53 | -46.04 |
| 4 | Barreiras | BA | -12.15 | -45.00 |
| 5 | Bom Jesus | PI | -9.07 | -44.36 |
| 6 | Campos Lindos | TO | -7.99 | -46.87 |
| 7 | Carolina | MA | -7.33 | -47.47 |
| 8 | Corrente | PI | -10.44 | -45.16 |
| 9 | Formosa do Rio Preto | BA | -11.05 | -45.19 |
| 10 | Imperatriz | MA | -5.52 | -47.47 |
| 11 | Luís Eduardo Magalhães | BA | -12.10 | -45.80 |
| 12 | Pedro Afonso | TO | -8.97 | -48.17 |
| 13 | Piracicaba | SP | -22.72 | -47.63 |
| 14 | Porto Nacional | TO | -10.71 | -48.42 |
| 15 | São Desidério | BA | -12.36 | -44.97 |
| 16 | Tasso Fragoso | MA | -8.47 | -45.75 |
| 17 | Uruçuí | PI | -7.23 | -44.56 |

> **Piracicaba (SP)** was included as a reference station outside MATOPIBA for cross-validation.

---

## Validation Pipeline

The validation follows a 7-step pipeline:

```
Step 1: Generate MATOPIBA study area map
Step 2: Generate descriptive statistics of raw climate data
Step 3: Concatenate raw datasets (NASA POWER + Open-Meteo)
Step 4: Calculate ETo from individual sources
Step 5: Validate ETo calculations (source comparison)
Step 6: Validate full pipeline (Kalman fusion)
Step 7: Compare all ETo sources
```

### Scripts (in validation package)

| Script | Description |
|--------|-------------|
| `1_generate_matopiba_map.py` | Study area map with city locations |
| `2_generate_descriptive_stats.py` | Descriptive statistics by variable |
| `3_concat_row_dataset_nasapower_openmeteo.py` | Merge raw climate datasets |
| `4_calculate_eto_data_from_openmeteo_or_nasapower.py` | ETo from individual sources |
| `5_validate_eto_calc.py` | Cross-validate ETo calculations |
| `6_validate_full_pipeline.py` | Validate Kalman fusion pipeline |
| `7_compare_all_eto_sources.py` | Compare all sources + fusion |

---

## Metrics Used

| Metric | Formula | Ideal |
|--------|---------|-------|
| **RMSE** | $\sqrt{\frac{1}{n}\sum(O_i - E_i)^2}$ | 0 |
| **MAE** | $\frac{1}{n}\sum|O_i - E_i|$ | 0 |
| **R²** | $1 - \frac{\sum(O_i - E_i)^2}{\sum(O_i - \bar{O})^2}$ | 1 |
| **NSE** | $1 - \frac{\sum(O_i - E_i)^2}{\sum(O_i - \bar{O})^2}$ | 1 |
| **PBIAS** | $\frac{\sum(O_i - E_i)}{\sum O_i} \times 100$ | 0% |
| **d** | Willmott index of agreement | 1 |

---

## Key Results

### ETo Comparison (Daily, all cities pooled)

| Source | RMSE (mm/day) | R² | NSE | PBIAS (%) |
|--------|---------------|-----|------|-----------|
| NASA POWER only | 0.5–0.8 | >0.85 | >0.80 | <5% |
| Open-Meteo only | 0.6–1.0 | >0.80 | >0.75 | <8% |
| **Kalman Fusion** | **0.4–0.6** | **>0.90** | **>0.85** | **<3%** |

### Seasonal Performance

| Season | Best Source | Fusion Improvement |
|--------|-----------|-------------------|
| Dry (May–Sep) | NASA POWER | +5–10% R² |
| Wet (Oct–Apr) | Open-Meteo | +8–15% R² |
| Transition | Fusion critical | +15–20% R² |

---

## Notebooks

| Notebook | Description |
|----------|-------------|
| `complete_validation_analysis.ipynb` | Full statistical analysis + figures |
| `tutorial_full_pipeline.ipynb` | Step-by-step tutorial for reproduction |

---

## API Demos (in validation package)

| Notebook | Description |
|----------|-------------|
| `01_nasa_power_api_demo.ipynb` | NASA POWER API usage examples |
| `02_openmeteo_archive_api_demo.ipynb` | Open-Meteo Archive API |
| `03_openmeteo_forecast_api_demo.ipynb` | Open-Meteo Forecast API |
| `04_met_norway_api_demo.ipynb` | MET Norway (Yr) API |
| `05_nws_forecast_api_demo.ipynb` | NWS Forecast API |
| `06_nws_stations_api_demo.ipynb` | NWS Stations API |

---

## Reproducibility

To reproduce the validation:

```bash
# 1. Download from Zenodo
# 2. Create environment
conda env create -f environment.yml
conda activate evaonline-validation

# 3. Run pipeline
cd scripts
python 1_generate_matopiba_map.py
python 2_generate_descriptive_stats.py
python 3_concat_row_dataset_nasapower_openmeteo.py
python 4_calculate_eto_data_from_openmeteo_or_nasapower.py
python 5_validate_eto_calc.py
python 6_validate_full_pipeline.py
python 7_compare_all_eto_sources.py
```

---

**Last updated:** 2025-02-23  
**Version:** 2.0