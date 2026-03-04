"""
Graphical Abstract for EVAonline paper (Environmental Modelling & Software).

Elsevier requirements:
  - Minimum: 531 x 1328 pixels (h x w), readable at 5 x 13 cm
  - Preferred formats: TIFF, EPS, PDF
  - Landscape orientation, 3-panel professional layout

Design inspired by Elsevier GA template and high-quality examples:
  - Colored header banners per section
  - Large fonts (~14-22 pt in canvas → ~6-9 pt at 5×13 cm print)
  - 3 panels: Data Sources | Methodology | Results
  - Minimal text, maximum visual impact

Pipeline: 6 Climate APIs → QC + Weighted Fusion → Kalman (Precip) →
          FAO-56 PM → Kalman (ETo) → Platform + Validation
"""

import matplotlib
matplotlib.use("Agg")  # Non-interactive backend for CI/CD
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle

# ================================================================
#  DIMENSIONS — Elsevier minimum: 531 × 1328 px (h × w)
#  Canvas: 13.28 × 5.31 inches at 300 DPI → 3984 × 1593 px
#  Print at 5 × 13 cm ≈ 0.39× scale → fonts need ≥ 14 pt canvas
# ================================================================
DPI = 150
FIG_W = 13.28  # inches (landscape)
FIG_H = 5.31   # inches

fig, ax = plt.subplots(1, 1, figsize=(FIG_W, FIG_H), dpi=DPI)
ax.set_xlim(0, 100)
ax.set_ylim(0, 40)
ax.axis("off")
fig.patch.set_facecolor("white")

# ================================================================
#  COLOR PALETTE — modern, vibrant, professional
# ================================================================
C_TITLE_BG = "#1B4F72"   # Deep navy — title banner
C_TITLE_FG = "#FFFFFF"   # White text on banner
C_PANEL1   = "#2E86C1"   # Cerulean blue — Data Sources
C_PANEL1_L = "#D6EAF8"   # Light blue background
C_PANEL2   = "#D35400"   # Burnt orange — Methodology
C_PANEL2_L = "#FEF5E7"   # Light orange background
C_PANEL3   = "#1A8B5E"   # Forest green — Results
C_PANEL3_L = "#E8F8F0"   # Light green background
C_TEXT     = "#1C2833"    # Near-black body text
C_GRAY     = "#5D6D7E"   # Subtle gray for secondary text
C_ACCENT   = "#C0392B"   # Red for key metrics
C_ARROW    = "#2C3E50"   # Dark arrow color
C_WHITE    = "#FFFFFF"


# ================================================================
#  HELPERS
# ================================================================
def draw_rect(x, y, w, h, fc, ec="none", lw=0, alpha=1.0, zorder=1):
    """Filled rectangle (sharp corners for clean panels)."""
    rect = Rectangle((x, y), w, h, linewidth=lw,
                      edgecolor=ec, facecolor=fc, alpha=alpha, zorder=zorder)
    ax.add_patch(rect)

def draw_rounded(x, y, w, h, fc, ec, lw=1.5, alpha=1.0, zorder=2):
    """Rounded box for cards."""
    box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.3",
                         facecolor=fc, edgecolor=ec,
                         linewidth=lw, alpha=alpha, zorder=zorder)
    ax.add_patch(box)

def draw_arrow(x1, y1, x2, y2, color=C_ARROW, lw=2.5):
    """Thick directional arrow."""
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="-|>", color=color, lw=lw,
                                connectionstyle="arc3,rad=0"),
                zorder=10)


# ================================================================
#  TITLE BANNER — full-width dark navy bar
# ================================================================
draw_rect(0, 34, 100, 6, C_TITLE_BG, zorder=3)
ax.text(50, 37.8, "EVAonline", fontsize=28, fontweight="bold",
        ha="center", va="center", color=C_TITLE_FG, zorder=4,
        fontfamily="sans-serif")
ax.text(50, 35.2,
        "Open-source platform for global reference evapotranspiration "
        "via multi-source reanalysis data fusion",
        fontsize=13, ha="center", va="center", color="#AED6F1", zorder=4,
        fontfamily="sans-serif", style="italic")

# ================================================================
#  PANEL LAYOUT — 3 columns with colored header bars
# ================================================================
# Column boundaries (with wider gutters between panels)
P1_X, P1_W = 0.5, 28       # Panel 1: Data Sources
P2_X, P2_W = 33, 30         # Panel 2: Methodology
P3_X, P3_W = 67.5, 32       # Panel 3: Results
PANEL_Y, PANEL_H = 0.5, 33  # All panels same height
HDR_H = 3.5                 # Header bar height

# --- Panel 1: DATA SOURCES ---
draw_rect(P1_X, PANEL_Y, P1_W, PANEL_H, C_PANEL1_L, ec=C_PANEL1, lw=2.5)
draw_rect(P1_X, PANEL_Y + PANEL_H - HDR_H, P1_W, HDR_H, C_PANEL1, zorder=3)
ax.text(P1_X + P1_W/2, PANEL_Y + PANEL_H - HDR_H/2,
        "Data Sources", fontsize=18, fontweight="bold",
        ha="center", va="center", color=C_WHITE, zorder=4)

# Source cards
sources = [
    ("NASA POWER",         "MERRA-2 + CERES  \u2022  Global 0.5\u00b0"),
    ("Open-Meteo Archive", "ERA5-Land / ERA5  \u2022  Global 0.25\u00b0"),
    ("Open-Meteo Forecast","Multi-NWP blend  \u2022  Global 0.25\u00b0"),
    ("MET Norway (Yr)",    "MEPS / ECMWF  \u2022  Global 2.5\u201310 km"),
    ("NWS Forecast",       "NDFD (GFS/NAM)  \u2022  CONUS 2.5 km"),
    ("NWS Stations",       "ASOS in-situ  \u2022  ~900 US stations"),
]
card_h = 3.5
card_gap = 0.4
y_start = PANEL_Y + PANEL_H - HDR_H - card_h - 0.8

for i, (name, desc) in enumerate(sources):
    cy = y_start - i * (card_h + card_gap)
    draw_rounded(P1_X + 1.2, cy, P1_W - 2.4, card_h,
                 C_WHITE, C_PANEL1, lw=1.2)
    ax.text(P1_X + 2.2, cy + card_h/2 + 0.5, name,
            fontsize=11, fontweight="bold", color=C_PANEL1, va="center")
    ax.text(P1_X + 2.2, cy + card_h/2 - 0.8, desc,
            fontsize=8.5, color=C_GRAY, va="center")

# "6 APIs" badge at bottom
ax.text(P1_X + P1_W/2, 1.5,
        "6 APIs  \u2022  Region-adaptive auto-selection",
        fontsize=10, fontweight="bold", ha="center", va="center",
        color=C_PANEL1,
        bbox=dict(boxstyle="round,pad=0.4", facecolor=C_WHITE,
                  edgecolor=C_PANEL1, linewidth=1.5))

# --- Panel 2: METHODOLOGY ---
draw_rect(P2_X, PANEL_Y, P2_W, PANEL_H, C_PANEL2_L, ec=C_PANEL2, lw=2.5)
draw_rect(P2_X, PANEL_Y + PANEL_H - HDR_H, P2_W, HDR_H, C_PANEL2, zorder=3)
ax.text(P2_X + P2_W/2, PANEL_Y + PANEL_H - HDR_H/2,
        "Methodology", fontsize=18, fontweight="bold",
        ha="center", va="center", color=C_WHITE, zorder=4)

# Pipeline stages as stacked boxes with arrows
stages = [
    ("Quality Control + Weighted Fusion",
     r"$\hat{z}_{k,j} = \sum_i w_{i,j}\, z_{k,i,j}\; /\; \sum_i w_{i,j}$",
     "Range + IQR filters  \u2022  Per-variable weights"),
    ("Kalman Filter \u2014 Precipitation",
     r"$\hat{x}_k^{+} = \hat{x}_k^{-} + K_k\,(z_k - \hat{x}_k^{-})$",
     "Adaptive covariance  \u2022  P01/P99 bounds"),
    ("FAO-56 Penman\u2013Monteith  \u2192  ET\u2080",
     r"$ET_0 = \frac{0.408\,\Delta(R_n-G) + \gamma\frac{900}{T+273}\,u_2\,(e_s-e_a)}"
     r"{\Delta + \gamma(1+0.34\,u_2)}$",
     "Reference evapotranspiration + water deficit"),
    ("Kalman Filter \u2014 ET\u2080",
     "",
     "Adaptive smoothing on computed ET\u2080"),
]
stage_h = 5.8
stage_gap = 2.0
sy_start = PANEL_Y + PANEL_H - HDR_H - stage_h - 0.6
cx = P2_X + P2_W / 2

for i, (title, eq, subtitle) in enumerate(stages):
    # Last stage (no equation) gets a shorter box
    has_eq = bool(eq)
    this_h = stage_h if has_eq else 3.6
    sy = sy_start - i * (stage_h + stage_gap)
    if not has_eq:
        # Shift up to compensate for smaller box
        sy = sy + (stage_h - this_h)
    # Color alternation: odd stages slightly different
    bg = C_WHITE if i % 2 == 0 else "#FFF8F0"
    draw_rounded(P2_X + 1.2, sy, P2_W - 2.4, this_h,
                 bg, C_PANEL2, lw=1.5)
    if has_eq:
        ax.text(cx, sy + this_h - 1.0, title,
                fontsize=11.5, fontweight="bold", ha="center", va="center",
                color=C_PANEL2)
        ax.text(cx, sy + this_h / 2, eq,
                fontsize=10, ha="center", va="center",
                color=C_TEXT, math_fontfamily="dejavuserif")
        ax.text(cx, sy + 1.0, subtitle,
                fontsize=8.5, ha="center", va="center",
                color=C_GRAY, style="italic")
    else:
        ax.text(cx, sy + this_h / 2 + 0.5, title,
                fontsize=11.5, fontweight="bold", ha="center", va="center",
                color=C_PANEL2)
        ax.text(cx, sy + this_h / 2 - 0.8, subtitle,
                fontsize=8.5, ha="center", va="center",
                color=C_GRAY, style="italic")
    # Arrow between stages
    if i < len(stages) - 1:
        draw_arrow(cx, sy - 0.1, cx, sy - stage_gap + 0.1,
                   color=C_PANEL2, lw=2.5)

# --- Panel 3: RESULTS & PLATFORM ---
draw_rect(P3_X, PANEL_Y, P3_W, PANEL_H, C_PANEL3_L, ec=C_PANEL3, lw=2.5)
draw_rect(P3_X, PANEL_Y + PANEL_H - HDR_H, P3_W, HDR_H, C_PANEL3, zorder=3)
ax.text(P3_X + P3_W/2, PANEL_Y + PANEL_H - HDR_H/2,
        "Results & Platform", fontsize=18, fontweight="bold",
        ha="center", va="center", color=C_WHITE, zorder=4)

rx = P3_X + P3_W / 2  # center of panel 3

# -- Validation header --
val_y = 27.5
ax.text(rx, val_y + 1.2, "Validation \u2014 MATOPIBA, Brazil",
        fontsize=13, fontweight="bold", ha="center", va="center",
        color=C_ACCENT)
ax.text(rx, val_y - 0.3,
        "17 sites  \u2022  1991\u20132020  \u2022  186,286 daily observations",
        fontsize=9.5, ha="center", va="center", color=C_GRAY)

# -- Four metric boxes --
metrics = [
    ("KGE",   "0.814"),
    ("R\u00b2",    "0.710"),
    ("RMSE",  "0.566"),
    ("PBIAS", "+0.71%"),
]
mbox_w = 7.0
mbox_h = 5.5
mbox_gap = 0.8
mx_start = P3_X + (P3_W - (len(metrics) * mbox_w + (len(metrics)-1) * mbox_gap)) / 2
my = 20.5

for i, (label, value) in enumerate(metrics):
    mx = mx_start + i * (mbox_w + mbox_gap)
    draw_rounded(mx, my, mbox_w, mbox_h, C_WHITE, C_ACCENT, lw=2.0)
    ax.text(mx + mbox_w/2, my + mbox_h - 1.2, label,
            fontsize=11, fontweight="bold", ha="center", va="center",
            color=C_ACCENT)
    ax.text(mx + mbox_w/2, my + mbox_h/2 - 0.5, value,
            fontsize=16, fontweight="bold", ha="center", va="center",
            color=C_TEXT)

# -- Platform features --
feat_y = 17.0
ax.text(rx, feat_y + 1.5, "Open-Source Platform",
        fontsize=13, fontweight="bold", ha="center", va="center",
        color=C_PANEL3)

features = [
    "\u25B6  Interactive web dashboard (Dash + Leaflet)",
    "\u25B6  3 modes: Recent, Historical, Forecast",
    "\u25B6  Global coverage with auto-fusion",
    "\u25B6  CSV / Excel export + email delivery",
]
for i, text in enumerate(features):
    fy = feat_y - 0.5 - i * 2.0
    ax.text(P3_X + 2.5, fy, text,
            fontsize=10.5, color=C_TEXT, va="center")

# -- Architecture badge --
draw_rounded(P3_X + 2, 2.2, P3_W - 4, 5.5, C_WHITE, C_PANEL3, lw=1.5)
ax.text(rx, 6.3, "13 Docker Services", fontsize=12, fontweight="bold",
        ha="center", va="center", color=C_PANEL3)
ax.text(rx, 4.5, "Hexagonal Architecture",
        fontsize=11, ha="center", va="center", color=C_PANEL3)
ax.text(rx, 3.0,
        "FastAPI  \u2022  Celery  \u2022  Redis  \u2022  PostgreSQL  \u2022  Nginx",
        fontsize=9, ha="center", va="center", color=C_GRAY)

# ================================================================
#  INTER-PANEL ARROWS
# ================================================================
# Panel 1 → Panel 2
draw_arrow(P1_X + P1_W + 0.2, 17, P2_X - 0.2, 17,
           color=C_ARROW, lw=3.0)
# Panel 2 → Panel 3
draw_arrow(P2_X + P2_W + 0.2, 17, P3_X - 0.2, 17,
           color=C_ARROW, lw=3.0)


# ================================================================
#  SAVE — TIFF (Elsevier preferred), PDF, PNG
# ================================================================
plt.tight_layout(pad=0.1)

plt.savefig(
    "docs/figures/graphical_abstract.tiff",
    dpi=300, bbox_inches="tight", facecolor="white",
    edgecolor="none", pil_kwargs={"compression": "tiff_lzw"},
)
plt.savefig(
    "docs/figures/graphical_abstract.pdf",
    dpi=300, bbox_inches="tight", facecolor="white", edgecolor="none",
)
plt.savefig(
    "docs/figures/graphical_abstract.png",
    dpi=300, bbox_inches="tight", facecolor="white", edgecolor="none",
)

print("\u2705 Graphical abstract saved:")
print("   - docs/figures/graphical_abstract.tiff (Elsevier preferred)")
print("   - docs/figures/graphical_abstract.pdf  (vector)")
print("   - docs/figures/graphical_abstract.png  (preview)")
print(f"   - Canvas: {FIG_W} \u00d7 {FIG_H} in at {DPI} DPI")
print(f"   - Output at 300 DPI: {FIG_W*300:.0f} \u00d7 {FIG_H*300:.0f} px")
print(f"   - Elsevier minimum: 1328 \u00d7 531 px \u2714")
plt.show()