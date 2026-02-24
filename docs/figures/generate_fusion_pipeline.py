"""
Figure 2: Two-stage data fusion pipeline for EVAonline paper.
"""

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

fig, ax = plt.subplots(1, 1, figsize=(12, 8), dpi=300)
ax.set_xlim(0, 12)
ax.set_ylim(0, 8)
ax.axis('off')
fig.patch.set_facecolor('white')

# Colors
C_INPUT = '#3498db'
C_QC = '#e74c3c'
C_S1 = '#e67e22'
C_S2 = '#8e44ad'
C_OUTPUT = '#27ae60'
C_TEXT = '#2c3e50'
BOX_H = 0.8

def draw_box(x, y, w, h, color, title, subtitle='', fontsize_t=9, fontsize_s=7):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.1",
                                 facecolor=f'{color}15', edgecolor=color, linewidth=1.5))
    if subtitle:
        ax.text(x + w/2, y + h*0.65, title, ha='center', va='center',
                fontsize=fontsize_t, fontweight='bold', color=color)
        ax.text(x + w/2, y + h*0.3, subtitle, ha='center', va='center',
                fontsize=fontsize_s, color=C_TEXT, style='italic')
    else:
        ax.text(x + w/2, y + h/2, title, ha='center', va='center',
                fontsize=fontsize_t, fontweight='bold', color=color)

def draw_arrow(x1, y1, x2, y2):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='->', color=C_TEXT, lw=1.5))

# === ROW 1: Data Sources ===
sources = ['NASA\nPOWER', 'Open-Meteo\nArchive', 'Open-Meteo\nForecast',
           'MET\nNorway', 'NWS\nForecast', 'NWS\nStations']
for i, s in enumerate(sources):
    x = 0.3 + i * 1.9
    draw_box(x, 7.0, 1.6, 0.8, C_INPUT, s, fontsize_t=7)

ax.text(6.0, 7.95, '6 Climate Data Sources (standardized schema)',
        ha='center', va='center', fontsize=10, fontweight='bold', color=C_INPUT)

# Arrow down
for i in range(6):
    draw_arrow(0.3 + i*1.9 + 0.8, 7.0, 6.0, 6.55)

# === ROW 2: Quality Control ===
draw_box(2.0, 5.7, 8.0, BOX_H, C_QC, 'Quality Control Pipeline')

qc_items = [
    '① Physical Range Validation (WMO + Brazil-specific bounds)',
    '② Adaptive IQR Outlier Detection (max 5% removal)',
    '③ Circuit Breaker: exclude sources with quality < 60%',
]
for i, item in enumerate(qc_items):
    ax.text(6.0, 6.35 - i*0.2, item, ha='center', va='center',
            fontsize=6.5, color=C_TEXT)

draw_arrow(6.0, 5.7, 6.0, 5.25)

# === ROW 3: Stage 1 ===
draw_box(1.5, 4.0, 9.0, 1.2, C_S1, '')
ax.text(6.0, 5.0, 'STAGE 1: Region-Adaptive Weighted Averaging',
        ha='center', va='center', fontsize=10, fontweight='bold', color=C_S1)

ax.text(6.0, 4.6, r'$\hat{z}_{k,j} = \frac{\sum_{i \in \mathcal{S}_{k,j}} w_i \cdot z_{k,i,j}}{\sum_{i \in \mathcal{S}_{k,j}} w_i}$',
        ha='center', va='center', fontsize=11, color=C_S1,
        math_fontfamily='dejavuserif')

ax.text(3.5, 4.2, 'USA: NWS=0.50, OM=0.30, MET=0.20',
        ha='center', va='center', fontsize=6.5, color=C_TEXT)
ax.text(6.0, 4.2, 'Nordic: MET=0.80, OM=0.20',
        ha='center', va='center', fontsize=6.5, color=C_TEXT)
ax.text(8.5, 4.2, 'Global: OM=0.70, MET=0.30',
        ha='center', va='center', fontsize=6.5, color=C_TEXT)

draw_arrow(6.0, 4.0, 6.0, 3.55)

# === ROW 4: Stage 2 ===
draw_box(1.5, 1.5, 9.0, 2.0, C_S2, '')
ax.text(6.0, 3.3, 'STAGE 2: Adaptive Kalman Filter (per variable)',
        ha='center', va='center', fontsize=10, fontweight='bold', color=C_S2)

ax.text(3.5, 2.85, 'Prediction:', ha='center', va='center',
        fontsize=7, fontweight='bold', color=C_S2)
ax.text(3.5, 2.55, r'$\hat{x}_k^- = \hat{x}_{k-1}^+$' + '\n' +
        r'$P_k^- = P_{k-1}^+ + Q_m$',
        ha='center', va='center', fontsize=8, color=C_S2,
        math_fontfamily='dejavuserif')

ax.text(6.0, 2.85, 'Update:', ha='center', va='center',
        fontsize=7, fontweight='bold', color=C_S2)
ax.text(6.0, 2.55, r'$K_k = P_k^- / (P_k^- + R_k)$' + '\n' +
        r'$\hat{x}_k^+ = \hat{x}_k^- + K_k(z_k - \hat{x}_k^-)$',
        ha='center', va='center', fontsize=8, color=C_S2,
        math_fontfamily='dejavuserif')

ax.text(9.0, 2.85, 'Adaptive R:', ha='center', va='center',
        fontsize=7, fontweight='bold', color=C_S2)
ax.text(9.0, 2.4, 'Normal: R = 0.3025\n'
        'P01/P99 exceeded: R × 50\n'
        'Extreme: R × 500',
        ha='center', va='center', fontsize=6.5, color=C_TEXT)

ax.text(6.0, 1.75, 'Climatological Priors: 1991–2020 monthly normals + P01/P99 percentiles (27 reference cities)',
        ha='center', va='center', fontsize=7, color=C_TEXT, style='italic')

draw_arrow(6.0, 1.5, 6.0, 1.05)

# === ROW 5: Output ===
draw_box(2.5, 0.2, 7.0, BOX_H, C_OUTPUT,
         'Fused meteorological variables → FAO-56 PM → ET₀ + Water Deficit')

plt.tight_layout(pad=0.3)
plt.savefig('docs/figures/fig_fusion_pipeline.png', dpi=300,
            bbox_inches='tight', facecolor='white')
plt.savefig('docs/figures/fig_fusion_pipeline.pdf', dpi=300,
            bbox_inches='tight', facecolor='white')
print("✅ Fusion pipeline figure saved")
plt.show()