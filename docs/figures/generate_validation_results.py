"""
Figure 3: Validation scatter plots and box plots.
Uses placeholder data — replace with actual validation results from Zenodo.
"""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.gridspec import GridSpec

np.random.seed(42)

fig = plt.figure(figsize=(14, 10), dpi=300)
gs = GridSpec(2, 3, figure=fig, hspace=0.35, wspace=0.35)
fig.patch.set_facecolor('white')

# --- Simulated data (REPLACE with real data from validation notebooks) ---
n = 365 * 5  # 5 years of daily data
eto_ref = np.random.uniform(2.0, 7.0, n)  # BR-DWGD reference

# Individual sources (with bias)
eto_nasa = eto_ref + np.random.normal(0.15, 0.55, n)
eto_openmeteo = eto_ref + np.random.normal(0.28, 0.70, n)

# Fusion (much better)
eto_fusion = eto_ref + np.random.normal(0.03, 0.38, n)

# --- Panel A: NASA POWER scatter ---
ax1 = fig.add_subplot(gs[0, 0])
ax1.scatter(eto_ref, eto_nasa, alpha=0.1, s=2, c='#3498db', rasterized=True)
ax1.plot([0, 10], [0, 10], 'k--', lw=1, label='1:1 line')
ax1.set_xlabel(r'BR-DWGD ET$_0$ (mm d$^{-1}$)', fontsize=9)
ax1.set_ylabel(r'Estimated ET$_0$ (mm d$^{-1}$)', fontsize=9)
ax1.set_title('(a) NASA POWER', fontsize=10, fontweight='bold')
ax1.set_xlim(0, 10)
ax1.set_ylim(0, 10)
ax1.set_aspect('equal')

# Metrics text box
rmse_nasa = np.sqrt(np.mean((eto_nasa - eto_ref)**2))
r2_nasa = np.corrcoef(eto_ref, eto_nasa)[0, 1]**2
mae_nasa = np.mean(np.abs(eto_nasa - eto_ref))
textstr = f'RMSE = {rmse_nasa:.3f}\n$r^2$ = {r2_nasa:.3f}\nMAE = {mae_nasa:.3f}'
ax1.text(0.05, 0.95, textstr, transform=ax1.transAxes, fontsize=8,
         verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

# --- Panel B: Open-Meteo scatter ---
ax2 = fig.add_subplot(gs[0, 1])
ax2.scatter(eto_ref, eto_openmeteo, alpha=0.1, s=2, c='#e67e22', rasterized=True)
ax2.plot([0, 10], [0, 10], 'k--', lw=1)
ax2.set_xlabel(r'BR-DWGD ET$_0$ (mm d$^{-1}$)', fontsize=9)
ax2.set_ylabel(r'Estimated ET$_0$ (mm d$^{-1}$)', fontsize=9)
ax2.set_title('(b) Open-Meteo Archive', fontsize=10, fontweight='bold')
ax2.set_xlim(0, 10)
ax2.set_ylim(0, 10)
ax2.set_aspect('equal')

rmse_om = np.sqrt(np.mean((eto_openmeteo - eto_ref)**2))
r2_om = np.corrcoef(eto_ref, eto_openmeteo)[0, 1]**2
mae_om = np.mean(np.abs(eto_openmeteo - eto_ref))
textstr = f'RMSE = {rmse_om:.3f}\n$r^2$ = {r2_om:.3f}\nMAE = {mae_om:.3f}'
ax2.text(0.05, 0.95, textstr, transform=ax2.transAxes, fontsize=8,
         verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

# --- Panel C: EVAonline Fusion scatter ---
ax3 = fig.add_subplot(gs[0, 2])
ax3.scatter(eto_ref, eto_fusion, alpha=0.1, s=2, c='#27ae60', rasterized=True)
ax3.plot([0, 10], [0, 10], 'k--', lw=1)
ax3.set_xlabel(r'BR-DWGD ET$_0$ (mm d$^{-1}$)', fontsize=9)
ax3.set_ylabel(r'Estimated ET$_0$ (mm d$^{-1}$)', fontsize=9)
ax3.set_title('(c) EVAonline Fusion', fontsize=10, fontweight='bold')
ax3.set_xlim(0, 10)
ax3.set_ylim(0, 10)
ax3.set_aspect('equal')

rmse_fus = np.sqrt(np.mean((eto_fusion - eto_ref)**2))
r2_fus = np.corrcoef(eto_ref, eto_fusion)[0, 1]**2
mae_fus = np.mean(np.abs(eto_fusion - eto_ref))
textstr = f'RMSE = {rmse_fus:.3f}\n$r^2$ = {r2_fus:.3f}\nMAE = {mae_fus:.3f}'
ax3.text(0.05, 0.95, textstr, transform=ax3.transAxes, fontsize=8,
         verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

# --- Panel D: Box plots of errors by source ---
ax4 = fig.add_subplot(gs[1, 0])
errors = [eto_nasa - eto_ref, eto_openmeteo - eto_ref, eto_fusion - eto_ref]
bp = ax4.boxplot(errors, labels=['NASA\nPOWER', 'Open-Meteo\nArchive', 'EVAonline\nFusion'],
                  patch_artist=True, showfliers=False,
                  medianprops=dict(color='black', linewidth=1.5))
colors = ['#3498db', '#e67e22', '#27ae60']
for patch, color in zip(bp['boxes'], colors):
    patch.set_facecolor(color)
    patch.set_alpha(0.6)
ax4.axhline(y=0, color='red', linestyle='--', linewidth=0.8, alpha=0.5)
ax4.set_ylabel(r'Error (mm d$^{-1}$)', fontsize=9)
ax4.set_title('(d) Error Distribution', fontsize=10, fontweight='bold')

# --- Panel E: KGE by city ---
ax5 = fig.add_subplot(gs[1, 1])
cities = ['ALV', 'ARA', 'BAL', 'BAR', 'BOM', 'CAM', 'CAR', 'COR',
          'FOR', 'IMP', 'LEM', 'PEA', 'PON', 'SAD', 'TAF', 'URU', 'PIR']
kge_fusion = np.random.normal(0.814, 0.053, 17)
kge_fusion = np.clip(kge_fusion, 0.7, 0.92)
kge_nasa = kge_fusion - np.random.uniform(0.05, 0.15, 17)

x_pos = np.arange(len(cities))
width = 0.35
ax5.bar(x_pos - width/2, kge_nasa, width, label='NASA POWER', color='#3498db', alpha=0.7)
ax5.bar(x_pos + width/2, kge_fusion, width, label='EVAonline', color='#27ae60', alpha=0.7)
ax5.set_xticks(x_pos)
ax5.set_xticklabels(cities, rotation=45, ha='right', fontsize=6)
ax5.set_ylabel('KGE', fontsize=9)
ax5.set_title('(e) KGE by City', fontsize=10, fontweight='bold')
ax5.legend(fontsize=7, loc='lower right')
ax5.set_ylim(0.5, 1.0)

# --- Panel F: Monthly RMSE ---
ax6 = fig.add_subplot(gs[1, 2])
months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
          'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
# Dry season (May-Sep) has lower RMSE
rmse_monthly_nasa = [0.65, 0.60, 0.55, 0.58, 0.50, 0.48,
                      0.45, 0.47, 0.52, 0.62, 0.70, 0.68]
rmse_monthly_fusion = [0.48, 0.44, 0.40, 0.42, 0.36, 0.34,
                        0.33, 0.35, 0.38, 0.45, 0.52, 0.50]

ax6.plot(months, rmse_monthly_nasa, 'o-', color='#3498db', label='NASA POWER',
         markersize=5, linewidth=1.5)
ax6.plot(months, rmse_monthly_fusion, 's-', color='#27ae60', label='EVAonline',
         markersize=5, linewidth=1.5)
ax6.fill_between(range(4, 9), 0, 0.8, alpha=0.1, color='orange', label='Dry season')
ax6.set_ylabel(r'RMSE (mm d$^{-1}$)', fontsize=9)
ax6.set_title('(f) Monthly RMSE', fontsize=10, fontweight='bold')
ax6.legend(fontsize=7)
ax6.tick_params(axis='x', rotation=45)
ax6.set_ylim(0.2, 0.8)

plt.savefig('docs/figures/fig_validation_results.png', dpi=300,
            bbox_inches='tight', facecolor='white')
plt.savefig('docs/figures/fig_validation_results.pdf', dpi=300,
            bbox_inches='tight', facecolor='white')
print("✅ Validation results figure saved")
plt.show()