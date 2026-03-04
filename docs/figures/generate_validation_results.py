"""
Validation figures for EVAonline EMS article (Figure 6a–6f).

Generates 6 SEPARATE publication-quality figures from REAL validation data
stored in EVAonline_validation_v1.0.0 (Zenodo package).

Output files:
  Figure_6a_scatter_nasa.png / .pdf
  Figure_6b_scatter_openmeteo.png / .pdf
  Figure_6c_scatter_fusion.png / .pdf
  Figure_6d_error_distribution.png / .pdf
  Figure_6e_kge_by_city.png / .pdf
  Figure_6f_seasonal_performance.png / .pdf

Data sources:
  - BR-DWGD reference ET₀:  original_data/eto_xavier_csv/{city}.csv
  - NASA POWER ET₀:         4_eto_nasa_only/{city}_ETo_NASA_ONLY.csv
  - Open-Meteo ET₀:         4_eto_openmeteo_only/{city}_ETo_OpenMeteo_ONLY.csv
  - EVAonline Fusion ET₀:   6_validation_full_pipeline/xavier_validation/preprocessed/{city}_FUSED_ETo.csv
  - Metrics by city/source:  7_comparison_all_sources/COMPARISON_ALL_SOURCES.csv

Key statistics from the article abstract (must match figures):
  EVAonline Fusion: KGE = 0.814 ± 0.053, NSE = 0.676 ± 0.085,
                    MAE = 0.423 mm/d, PBIAS = 0.71 ± 0.53%
  RMSE reduction: 34% vs Open-Meteo API (best individual), 49% vs NASA POWER
"""

from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap
from scipy import stats

# ---------------------------------------------------------------------------
# Matplotlib global style — journal quality
# ---------------------------------------------------------------------------
plt.rcParams.update({
    "font.family": "serif",
    "font.size": 13,
    "axes.labelsize": 14,
    "axes.titlesize": 15,
    "xtick.labelsize": 12,
    "ytick.labelsize": 12,
    "legend.fontsize": 11,
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "savefig.facecolor": "white",
    "axes.grid": False,
    "axes.spines.top": True,
    "axes.spines.right": True,
})

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent          # docs/figures/
PROJECT_ROOT = SCRIPT_DIR.parent.parent               # EVAONLINE/
DATA_ROOT = PROJECT_ROOT / "EVAonline_validation_v1.0.0" / "data"

XAVIER_DIR = DATA_ROOT / "original_data" / "eto_xavier_csv"
NASA_DIR = DATA_ROOT / "4_eto_nasa_only"
OPENMETEO_DIR = DATA_ROOT / "4_eto_openmeteo_only"
FUSION_DIR = (DATA_ROOT / "6_validation_full_pipeline" /
              "xavier_validation" / "preprocessed")
METRICS_CSV = DATA_ROOT / "7_comparison_all_sources" / "COMPARISON_ALL_SOURCES.csv"

OUTPUT_DIR = SCRIPT_DIR

# ---------------------------------------------------------------------------
# City list (17 cities: 16 MATOPIBA + Piracicaba/SP)
# ---------------------------------------------------------------------------
CITIES = [
    "Alvorada_do_Gurgueia_PI",
    "Araguaina_TO",
    "Balsas_MA",
    "Barreiras_BA",
    "Bom_Jesus_PI",
    "Campos_Lindos_TO",
    "Carolina_MA",
    "Corrente_PI",
    "Formosa_do_Rio_Preto_BA",
    "Imperatriz_MA",
    "Luiz_Eduardo_Magalhaes_BA",
    "Pedro_Afonso_TO",
    "Piracicaba_SP",
    "Porto_Nacional_TO",
    "Sao_Desiderio_BA",
    "Tasso_Fragoso_MA",
    "Urucui_PI",
]

CITY_SHORT = {
    "Alvorada_do_Gurgueia_PI": "ALV",
    "Araguaina_TO": "ARA",
    "Balsas_MA": "BAL",
    "Barreiras_BA": "BAR",
    "Bom_Jesus_PI": "BOM",
    "Campos_Lindos_TO": "CAM",
    "Carolina_MA": "CAR",
    "Corrente_PI": "COR",
    "Formosa_do_Rio_Preto_BA": "FOR",
    "Imperatriz_MA": "IMP",
    "Luiz_Eduardo_Magalhaes_BA": "LEM",
    "Pedro_Afonso_TO": "PEA",
    "Piracicaba_SP": "PIR",
    "Porto_Nacional_TO": "PON",
    "Sao_Desiderio_BA": "SAD",
    "Tasso_Fragoso_MA": "TAF",
    "Urucui_PI": "URU",
}

# ---------------------------------------------------------------------------
# Colors (consistent across all 6 figures)
# ---------------------------------------------------------------------------
C_NASA = "#2980b9"
C_OPENMETEO = "#e67e22"
C_OPENMETEO_API = "#8e44ad"
C_FUSION = "#27ae60"

SOURCE_COLORS = {
    "NASA_ONLY": C_NASA,
    "OPENMETEO_ONLY": C_OPENMETEO,
    "OPENMETEO_API": C_OPENMETEO_API,
    "EVAONLINE_FUSION": C_FUSION,
}
SOURCE_LABELS = {
    "NASA_ONLY": "NASA POWER",
    "OPENMETEO_ONLY": "Open-Meteo Archive (ERA5-Land)",
    "OPENMETEO_API": "Open-Meteo API (ERA5)",
    "EVAONLINE_FUSION": "EVAonline Fusion",
}


# ═══════════════════════════════════════════════════════════════════════════
# DATA LOADING
# ═══════════════════════════════════════════════════════════════════════════
def load_daily_data() -> pd.DataFrame:
    """Load and merge daily ET₀ for all 17 cities (ref + 3 estimated)."""
    frames = []
    for city in CITIES:
        df_ref = pd.read_csv(XAVIER_DIR / f"{city}.csv", parse_dates=["date"])
        df_ref = df_ref.rename(columns={"eto_xavier": "eto_ref"})

        df_nasa = pd.read_csv(
            NASA_DIR / f"{city}_ETo_NASA_ONLY.csv", parse_dates=["date"]
        )[["date", "eto_evaonline"]].rename(columns={"eto_evaonline": "eto_nasa"})

        df_om = pd.read_csv(
            OPENMETEO_DIR / f"{city}_ETo_OpenMeteo_ONLY.csv", parse_dates=["date"]
        )[["date", "eto_evaonline"]].rename(columns={"eto_evaonline": "eto_openmeteo"})

        df_fus = pd.read_csv(
            FUSION_DIR / f"{city}_FUSED_ETo.csv", parse_dates=["date"]
        )[["date", "eto_final"]].rename(columns={"eto_final": "eto_fusion"})

        df = (df_ref.merge(df_nasa, on="date")
                    .merge(df_om, on="date")
                    .merge(df_fus, on="date"))
        df["city"] = city
        df["month"] = df["date"].dt.month
        frames.append(df)

    return pd.concat(frames, ignore_index=True)


def load_metrics() -> pd.DataFrame:
    """Load pre-computed metrics per city per source."""
    return pd.read_csv(METRICS_CSV)


def _save(fig, name: str):
    """Save figure as PNG + PDF and close."""
    png = OUTPUT_DIR / f"{name}.png"
    pdf = OUTPUT_DIR / f"{name}.pdf"
    fig.savefig(str(png))
    fig.savefig(str(pdf))
    plt.close(fig)
    print(f"   ✅ {name}.png / .pdf")


# ═══════════════════════════════════════════════════════════════════════════
# FIGURE (a)/(b)/(c) — DENSITY SCATTER PLOTS
# ═══════════════════════════════════════════════════════════════════════════
def make_scatter(df, col_est, color_base, title, filename, n_total_str):
    """Single large density scatter with 1:1 line, regression, colorbar."""
    x = df["eto_ref"].values
    y = df[col_est].values
    mask = np.isfinite(x) & np.isfinite(y)
    x, y = x[mask], y[mask]

    fig, ax = plt.subplots(figsize=(8, 8))

    # Density colormap
    base_rgb = plt.matplotlib.colors.to_rgb(color_base)
    cmap = LinearSegmentedColormap.from_list("d", [(1, 1, 1), base_rgb], N=256)

    hb = ax.hexbin(x, y, gridsize=80, cmap=cmap, mincnt=1,
                   linewidths=0.1, edgecolors="none", extent=[0, 10, 0, 10])
    cb = fig.colorbar(hb, ax=ax, shrink=0.78, pad=0.02)
    cb.set_label("Observation count", fontsize=12)

    # 1:1 reference (red dashed)
    ax.plot([0, 10], [0, 10], color="red", ls="--", lw=1.5,
            label="1:1 reference", zorder=5)

    # Linear regression (blue solid)
    slope, intercept, r_val, _, _ = stats.linregress(x, y)
    xf = np.array([0, 10])
    ax.plot(xf, slope * xf + intercept, color="blue", ls="-", lw=1.5,
            label=f"y = {slope:.3f}x + {intercept:.3f}", zorder=5)

    # Statistics
    rmse = np.sqrt(np.mean((y - x) ** 2))
    r2 = r_val ** 2
    mae = np.mean(np.abs(y - x))
    bias = np.mean(y - x)
    pbias = 100.0 * np.sum(y - x) / np.sum(x)
    nse = 1.0 - np.sum((y - x) ** 2) / np.sum((x - np.mean(x)) ** 2)

    # KGE
    r_corr = np.corrcoef(x, y)[0, 1]
    alpha_kge = np.std(y) / np.std(x)
    beta_kge = np.mean(y) / np.mean(x)
    kge = 1.0 - np.sqrt((r_corr - 1) ** 2 + (alpha_kge - 1) ** 2 + (beta_kge - 1) ** 2)

    textstr = (
        f"n = {len(x):,}\n"
        f"$R^2$ = {r2:.4f}\n"
        f"KGE = {kge:.4f}\n"
        f"NSE = {nse:.4f}\n"
        f"RMSE = {rmse:.3f} mm d$^{{-1}}$\n"
        f"MAE = {mae:.3f} mm d$^{{-1}}$\n"
        f"Bias = {bias:+.3f} mm d$^{{-1}}$\n"
        f"PBIAS = {pbias:+.2f}%"
    )
    ax.text(0.03, 0.97, textstr, transform=ax.transAxes, fontsize=12,
            verticalalignment="top", fontfamily="monospace",
            bbox=dict(boxstyle="round,pad=0.4", facecolor="white",
                      alpha=0.92, edgecolor="gray", linewidth=0.8))

    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.set_aspect("equal")
    ax.set_xlabel(r"BR-DWGD reference ET$_0$ (mm d$^{-1}$)")
    ax.set_ylabel(r"Estimated ET$_0$ (mm d$^{-1}$)")
    ax.set_title(title, fontsize=16, fontweight="bold", pad=12)
    ax.legend(loc="lower right", fontsize=11, framealpha=0.9)

    # Tick formatting
    ax.xaxis.set_major_locator(mticker.MultipleLocator(2))
    ax.yaxis.set_major_locator(mticker.MultipleLocator(2))
    ax.xaxis.set_minor_locator(mticker.MultipleLocator(1))
    ax.yaxis.set_minor_locator(mticker.MultipleLocator(1))

    fig.tight_layout()
    _save(fig, filename)


# ═══════════════════════════════════════════════════════════════════════════
# FIGURE (d) — ERROR DISTRIBUTION BOX PLOTS (all 4 sources)
# ═══════════════════════════════════════════════════════════════════════════
def make_error_boxplot(df):
    """Box plots of daily error for all 4 sources."""
    fig, ax = plt.subplots(figsize=(10, 7))

    err_nasa = (df["eto_nasa"] - df["eto_ref"]).dropna().values
    err_om = (df["eto_openmeteo"] - df["eto_ref"]).dropna().values
    err_fus = (df["eto_fusion"] - df["eto_ref"]).dropna().values

    data = [err_nasa, err_om, err_fus]
    labels = ["NASA POWER\n(FAO-56)", "Open-Meteo Archive\n(ERA5-Land)",
              "EVAonline\nFusion"]
    colors = [C_NASA, C_OPENMETEO, C_FUSION]

    bp = ax.boxplot(
        data,
        tick_labels=labels,
        patch_artist=True,
        showfliers=False,
        widths=0.55,
        medianprops=dict(color="black", linewidth=2),
        whiskerprops=dict(linewidth=1.2),
        capprops=dict(linewidth=1.2),
        boxprops=dict(linewidth=1.2),
    )
    for patch, color in zip(bp["boxes"], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.55)

    ax.axhline(y=0, color="red", ls="--", lw=1.2, alpha=0.7, label="Zero error")

    # Annotate statistics
    for i, (lbl, errs, color) in enumerate(zip(
        ["NASA", "Open-Meteo", "Fusion"], data, colors
    )):
        med = np.median(errs)
        q25, q75 = np.percentile(errs, [25, 75])
        mae = np.mean(np.abs(errs))
        rmse = np.sqrt(np.mean(errs ** 2))
        ax.text(i + 1, q75 + 0.15,
                f"Median = {med:+.3f}\nMAE = {mae:.3f}\nRMSE = {rmse:.3f}",
                ha="center", va="bottom", fontsize=10,
                color="dimgray", fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.2", facecolor="white",
                          alpha=0.85, edgecolor="lightgray"))

    ax.set_ylabel(r"Error: Estimated $-$ Reference (mm d$^{-1}$)", fontsize=14)
    ax.set_title("(d) Error Distribution by Source", fontsize=16,
                 fontweight="bold", pad=12)
    ax.legend(loc="upper right", fontsize=11)
    ax.tick_params(axis="x", labelsize=12)

    fig.tight_layout()
    _save(fig, "Figure_6d_error_distribution")


# ═══════════════════════════════════════════════════════════════════════════
# FIGURE (e) — KGE BY CITY (all 4 sources)
# ═══════════════════════════════════════════════════════════════════════════
def make_kge_by_city(metrics):
    """Grouped bar chart: KGE for each city, all 4 sources."""
    fig, ax = plt.subplots(figsize=(14, 7))

    sources = ["NASA_ONLY", "OPENMETEO_ONLY", "OPENMETEO_API", "EVAONLINE_FUSION"]
    sorted_cities = sorted(CITIES)
    n_cities = len(sorted_cities)
    n_sources = len(sources)
    width = 0.20
    x = np.arange(n_cities)

    for i, src in enumerate(sources):
        src_data = metrics[metrics["source"] == src].set_index("city")
        kge_vals = [src_data.loc[c, "kge"] if c in src_data.index else 0
                    for c in sorted_cities]
        offset = (i - (n_sources - 1) / 2) * width
        ax.bar(x + offset, kge_vals, width * 0.92,
               label=SOURCE_LABELS[src],
               color=SOURCE_COLORS[src],
               alpha=0.80, edgecolor="white", linewidth=0.6)

    # City labels
    city_labels = [CITY_SHORT[c] for c in sorted_cities]
    ax.set_xticks(x)
    ax.set_xticklabels(city_labels, rotation=50, ha="right", fontsize=11)

    ax.set_ylabel("KGE (Kling-Gupta Efficiency)", fontsize=14)
    ax.set_title("(e) KGE Comparison by City and Source", fontsize=16,
                 fontweight="bold", pad=12)
    ax.set_ylim(-0.7, 1.05)
    ax.axhline(y=0, color="gray", ls="-", lw=0.5, alpha=0.3)
    ax.axhline(y=0.5, color="gray", ls=":", lw=0.8, alpha=0.5,
               label="KGE = 0.5 threshold")

    # Mean KGE annotations
    mean_box_lines = []
    for src in sources:
        src_data = metrics[metrics["source"] == src]
        m = src_data["kge"].mean()
        s = src_data["kge"].std()
        mean_box_lines.append(
            f"{SOURCE_LABELS[src]}: {m:.3f} ± {s:.3f}"
        )
    mean_text = "Mean KGE ± σ:\n" + "\n".join(mean_box_lines)
    ax.text(0.01, 0.98, mean_text, transform=ax.transAxes, fontsize=9.5,
            verticalalignment="top", fontfamily="monospace",
            bbox=dict(boxstyle="round,pad=0.4", facecolor="lightyellow",
                      alpha=0.95, edgecolor="gray"))

    ax.legend(loc="lower left", fontsize=10, ncol=2, framealpha=0.9)

    fig.tight_layout()
    _save(fig, "Figure_6e_kge_by_city")


# ═══════════════════════════════════════════════════════════════════════════
# FIGURE (f) — SEASONAL PERFORMANCE (Monthly RMSE, dry vs wet)
# ═══════════════════════════════════════════════════════════════════════════
def make_seasonal(df):
    """Monthly RMSE lines for 3 sources + dry season shading."""
    fig, ax = plt.subplots(figsize=(11, 7))

    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    source_configs = [
        ("eto_nasa", "NASA POWER", C_NASA, "o", "-"),
        ("eto_openmeteo", "Open-Meteo Archive", C_OPENMETEO, "^", "-"),
        ("eto_fusion", "EVAonline Fusion", C_FUSION, "s", "-"),
    ]

    for col, label, color, marker, ls in source_configs:
        rmse_by_month = []
        mae_by_month = []
        for m in range(1, 13):
            mask = df["month"] == m
            ref = df.loc[mask, "eto_ref"].values
            est = df.loc[mask, col].values
            valid = np.isfinite(ref) & np.isfinite(est)
            err = est[valid] - ref[valid]
            rmse_by_month.append(np.sqrt(np.mean(err ** 2)))
            mae_by_month.append(np.mean(np.abs(err)))
        ax.plot(months, rmse_by_month, marker=marker, ls=ls, color=color,
                label=f"{label}", markersize=8, linewidth=2.2, zorder=3)

    # Dry season shading
    ax.axvspan(3.6, 8.4, alpha=0.12, color="orange", label="Dry season (May–Sep)")

    # Annotations for dry/wet means
    for col, label, color in [
        ("eto_nasa", "NASA", C_NASA),
        ("eto_fusion", "Fusion", C_FUSION),
    ]:
        dry_err, wet_err = [], []
        for m in range(1, 13):
            mask = df["month"] == m
            ref = df.loc[mask, "eto_ref"].values
            est = df.loc[mask, col].values
            valid = np.isfinite(ref) & np.isfinite(est)
            err = est[valid] - ref[valid]
            rmse_m = np.sqrt(np.mean(err ** 2))
            if m in {5, 6, 7, 8, 9}:
                dry_err.append(rmse_m)
            else:
                wet_err.append(rmse_m)

    ax.set_xlabel("Month", fontsize=14)
    ax.set_ylabel(r"RMSE (mm d$^{-1}$)", fontsize=14)
    ax.set_title("(f) Seasonal Performance — Monthly RMSE",
                 fontsize=16, fontweight="bold", pad=12)
    ax.legend(fontsize=11, loc="upper left", framealpha=0.9)
    ax.tick_params(axis="x", rotation=45, labelsize=12)

    fig.tight_layout()
    _save(fig, "Figure_6f_seasonal_performance")


# ═══════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════
def main():
    print("=" * 65)
    print("  EVAonline — Generating validation figures (a)–(f)")
    print("=" * 65)

    print("\n📂 Loading daily data (17 cities × 30 years)...")
    df = load_daily_data()
    n = len(df)
    print(f"   ✅ {n:,} observations ({len(CITIES)} cities × "
          f"{n // len(CITIES):,} days)")

    metrics = load_metrics()
    print(f"   ✅ {len(metrics)} metric rows\n")

    n_str = f"{n:,}"

    # ---- Scatter plots (a), (b), (c) ----
    print("📊 Generating scatter plots...")
    make_scatter(df, "eto_nasa", C_NASA,
                 "(a) NASA POWER (FAO-56)",
                 "Figure_6a_scatter_nasa", n_str)

    make_scatter(df, "eto_openmeteo", C_OPENMETEO,
                 "(b) Open-Meteo Archive (ERA5-Land)",
                 "Figure_6b_scatter_openmeteo", n_str)

    make_scatter(df, "eto_fusion", C_FUSION,
                 "(c) EVAonline Two-Stage Fusion",
                 "Figure_6c_scatter_fusion", n_str)

    # ---- Error distribution (d) ----
    print("📊 Generating error distribution...")
    make_error_boxplot(df)

    # ---- KGE by city (e) ----
    print("📊 Generating KGE by city...")
    make_kge_by_city(metrics)

    # ---- Seasonal performance (f) ----
    print("📊 Generating seasonal performance...")
    make_seasonal(df)

    print(f"\n{'=' * 65}")
    print(f"  ✅ All 6 figures saved to: {OUTPUT_DIR}")
    print(f"{'=' * 65}")


if __name__ == "__main__":
    main()