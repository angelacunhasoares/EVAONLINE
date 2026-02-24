"""
Graphical Abstract for EVAonline paper.
Generates a landscape figure (525x292px minimum) showing the pipeline:
Left: 6 climate APIs → Center: Two-stage fusion → Right: Dashboard + Results
"""

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

# --- Configuration ---
fig, ax = plt.subplots(1, 1, figsize=(14, 5.5), dpi=300)
ax.set_xlim(0, 14)
ax.set_ylim(0, 5.5)
ax.axis('off')
fig.patch.set_facecolor('white')

# --- Color palette ---
C_API = '#3498db'       # Blue - data sources
C_FUSION = '#e67e22'    # Orange - fusion
C_ETO = '#2ecc71'       # Green - ETo
C_OUTPUT = '#9b59b6'    # Purple - output
C_ARROW = '#2c3e50'     # Dark - arrows
C_BG_LIGHT = '#ecf0f1'  # Light gray background
C_TEXT = '#2c3e50'       # Dark text

# === SECTION 1: Data Sources (left) ===
# Background box
ax.add_patch(FancyBboxPatch((0.2, 0.3), 3.0, 4.8, boxstyle="round,pad=0.15",
                             facecolor='#ebf5fb', edgecolor=C_API, linewidth=1.5))
ax.text(1.7, 4.85, 'Climate Data\nSources', ha='center', va='top',
        fontsize=9, fontweight='bold', color=C_API)

sources = [
    ('NASA POWER', 'Satellite+Reanalysis'),
    ('Open-Meteo\nArchive', 'ERA5 Reanalysis'),
    ('Open-Meteo\nForecast', 'NWP Global'),
    ('MET Norway', 'ECMWF IFS'),
    ('NWS Forecast', 'USA NWP'),
    ('NWS Stations', 'In-situ obs.'),
]

for i, (name, desc) in enumerate(sources):
    y = 4.2 - i * 0.65
    ax.add_patch(FancyBboxPatch((0.4, y - 0.22), 2.6, 0.5,
                                 boxstyle="round,pad=0.08",
                                 facecolor='white', edgecolor=C_API,
                                 linewidth=1.0))
    ax.text(1.0, y + 0.02, name, ha='center', va='center',
            fontsize=6, fontweight='bold', color=C_TEXT)
    ax.text(2.5, y + 0.02, desc, ha='center', va='center',
            fontsize=5, color='gray', style='italic')

# === SECTION 2: Two-Stage Fusion (center) ===
# Arrow from sources to fusion
ax.annotate('', xy=(3.8, 2.6), xytext=(3.3, 2.6),
            arrowprops=dict(arrowstyle='->', color=C_ARROW, lw=2.0))

# Stage 1 box
ax.add_patch(FancyBboxPatch((3.9, 3.2), 2.8, 1.7, boxstyle="round,pad=0.15",
                             facecolor='#fef9e7', edgecolor=C_FUSION, linewidth=1.5))
ax.text(5.3, 4.65, 'Stage 1', ha='center', va='top',
        fontsize=8, fontweight='bold', color=C_FUSION)
ax.text(5.3, 4.35, 'Quality Control\n+ Region-Adaptive\nWeighted Averaging',
        ha='center', va='top', fontsize=6.5, color=C_TEXT)
ax.text(5.3, 3.5, r'$\hat{z}_{k,j} = \frac{\sum w_i \cdot z_{k,i,j}}{\sum w_i}$',
        ha='center', va='center', fontsize=7, color=C_FUSION,
        math_fontfamily='dejavuserif')

# Arrow Stage 1 → Stage 2
ax.annotate('', xy=(5.3, 2.85), xytext=(5.3, 3.15),
            arrowprops=dict(arrowstyle='->', color=C_ARROW, lw=2.0))

# Stage 2 box
ax.add_patch(FancyBboxPatch((3.9, 0.6), 2.8, 2.15, boxstyle="round,pad=0.15",
                             facecolor='#fdf2e9', edgecolor=C_FUSION, linewidth=1.5))
ax.text(5.3, 2.5, 'Stage 2', ha='center', va='top',
        fontsize=8, fontweight='bold', color=C_FUSION)
ax.text(5.3, 2.2, 'Adaptive Kalman Filter\n(1991–2020 priors,\nP01/P99 bounds)',
        ha='center', va='top', fontsize=6.5, color=C_TEXT)
ax.text(5.3, 1.15, r'$K_k = \frac{P_k^-}{P_k^- + R_k}$',
        ha='center', va='center', fontsize=7, color=C_FUSION,
        math_fontfamily='dejavuserif')
ax.text(5.3, 0.78, r'$\hat{x}_k^+ = \hat{x}_k^- + K_k(z_k - \hat{x}_k^-)$',
        ha='center', va='center', fontsize=6, color=C_FUSION,
        math_fontfamily='dejavuserif')

# === SECTION 3: FAO-56 PM (center-right) ===
ax.annotate('', xy=(7.3, 2.6), xytext=(6.8, 2.6),
            arrowprops=dict(arrowstyle='->', color=C_ARROW, lw=2.0))

ax.add_patch(FancyBboxPatch((7.4, 1.5), 2.4, 2.2, boxstyle="round,pad=0.15",
                             facecolor='#eafaf1', edgecolor=C_ETO, linewidth=1.5))
ax.text(8.6, 3.45, 'FAO-56\nPenman-Monteith', ha='center', va='top',
        fontsize=8, fontweight='bold', color=C_ETO)
ax.text(8.6, 2.7, r'$ET_0 = \frac{0.408\Delta(R_n-G)+\gamma\frac{900}{T+273}u_2(e_s-e_a)}{\Delta+\gamma(1+0.34u_2)}$',
        ha='center', va='center', fontsize=5, color=C_ETO,
        math_fontfamily='dejavuserif')
ax.text(8.6, 2.15, '+ Water Deficit\n  Analysis', ha='center', va='center',
        fontsize=6.5, color=C_TEXT)
ax.text(8.6, 1.7, r'$WD = K_c \cdot ET_0 - P_{eff}$',
        ha='center', va='center', fontsize=6, color=C_ETO,
        math_fontfamily='dejavuserif')

# === SECTION 4: Output (right) ===
ax.annotate('', xy=(10.3, 2.6), xytext=(9.9, 2.6),
            arrowprops=dict(arrowstyle='->', color=C_ARROW, lw=2.0))

ax.add_patch(FancyBboxPatch((10.4, 0.6), 3.2, 4.3, boxstyle="round,pad=0.15",
                             facecolor='#f4ecf7', edgecolor=C_OUTPUT, linewidth=1.5))
ax.text(12.0, 4.65, 'EVAonline Platform', ha='center', va='top',
        fontsize=9, fontweight='bold', color=C_OUTPUT)

outputs = [
    '🌐 Web Dashboard',
    '📊 Interactive Charts',
    '📥 CSV/Excel Export',
    '📧 Email Delivery',
    '🔄 3 Modes: Recent,\n     Historical, Forecast',
    '🌍 Global Coverage',
]
for i, text in enumerate(outputs):
    y = 4.1 - i * 0.55
    ax.text(10.7, y, text, ha='left', va='center', fontsize=6.5, color=C_TEXT)

# Validation result box
ax.add_patch(FancyBboxPatch((10.6, 0.75), 2.8, 0.9, boxstyle="round,pad=0.08",
                             facecolor='white', edgecolor=C_OUTPUT, linewidth=1.0))
ax.text(12.0, 1.4, 'Validation (17 MATOPIBA sites)', ha='center', va='center',
        fontsize=6, fontweight='bold', color=C_OUTPUT)
ax.text(12.0, 1.05, 'KGE = 0.814 | RMSE −26%\nMAE = 0.423 mm/d | PBIAS = 0.71%',
        ha='center', va='center', fontsize=5.5, color=C_TEXT)

# === Title ===
ax.text(7.0, 5.35, 'EVAonline: Multi-Source Climate Data Fusion for ET₀ Estimation',
        ha='center', va='center', fontsize=11, fontweight='bold', color=C_TEXT)

plt.tight_layout(pad=0.3)
plt.savefig('docs/figures/graphical_abstract.png', dpi=300, bbox_inches='tight',
            facecolor='white', edgecolor='none')
plt.savefig('docs/figures/graphical_abstract.pdf', dpi=300, bbox_inches='tight',
            facecolor='white', edgecolor='none')
print("✅ Graphical abstract saved to docs/figures/")
plt.show()