"""
Generate Entity-Relationship + Data Persistence diagram for EVAonline.
Includes PostgreSQL tables, Redis in-memory store, JSON files, and
external API data flow.  Publication-quality figure.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
from pathlib import Path

# ──────────────────────────────────────────────────────────
#  Canvas – 28 × 19 data-units, generous margins
# ──────────────────────────────────────────────────────────
fig, ax = plt.subplots(1, 1, figsize=(30, 20))
ax.set_xlim(0, 28)
ax.set_ylim(0, 19)
ax.axis('off')
fig.patch.set_facecolor('white')

# ──────────────────────────────────────────────────────────
#  Colour palette
# ──────────────────────────────────────────────────────────
C_CORE      = '#2980b9'
C_META      = '#27ae60'
C_ADMIN     = '#8e44ad'
C_API       = '#c0392b'
C_JSON      = '#e67e22'
C_REDIS     = '#d63031'
C_REDIS_BG  = '#fff5f5'
C_JSONB_TXT = '#d35400'
C_ARROW     = '#7f8c8d'
C_TITLE_BG  = '#2c3e50'


# ──────────────────────────────────────────────────────────
#  Helper – draw a PostgreSQL-style table box
# ──────────────────────────────────────────────────────────
def draw_table(ax, x, y, w, h, title, columns, color,
               title_fs=17, col_fs=14, row_h=0.44):
    body = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.06",
                          facecolor='white', edgecolor=color, linewidth=2.5)
    ax.add_patch(body)
    th = 0.75
    hdr = FancyBboxPatch((x, y + h - th), w, th, boxstyle="round,pad=0.06",
                          facecolor=color, edgecolor=color, linewidth=2.5)
    ax.add_patch(hdr)
    ax.text(x + w / 2, y + h - th / 2, title, ha='center', va='center',
            fontsize=title_fs, fontweight='bold', color='white',
            family='monospace')
    for i, col in enumerate(columns):
        ypos = y + h - th - 0.32 - i * row_h
        if ypos < y + 0.08:
            break
        is_key  = col.lstrip().startswith(('PK', 'UQ', 'FK'))
        is_jsonb = 'JSONB' in col
        clr = C_JSONB_TXT if is_jsonb else '#2c3e50'
        ax.text(x + 0.3, ypos, col, ha='left', va='center',
                fontsize=col_fs, fontweight='bold' if is_key else 'normal',
                family='monospace', color=clr)


# ──────────────────────────────────────────────────────────
#  Helper – draw a Redis namespace sub-box
# ──────────────────────────────────────────────────────────
def draw_redis_section(ax, x, y, w, h, title, items, color):
    rect = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.06",
                          facecolor='white', edgecolor=color,
                          linewidth=1.8, alpha=0.9)
    ax.add_patch(rect)
    ax.text(x + w / 2, y + h - 0.32, title, ha='center', va='center',
            fontsize=15, fontweight='bold', color=color, family='monospace')
    for i, item in enumerate(items):
        ypos = y + h - 0.75 - i * 0.44
        if ypos < y + 0.05:
            break
        ax.text(x + 0.25, ypos, item, ha='left', va='center',
                fontsize=13.5, family='monospace', color='#2c3e50')


# ════════════════════════════════════════════════════════════
#  TITLE
# ════════════════════════════════════════════════════════════
ax.text(14, 18.45,
        'EVAonline  \u2014  Data Persistence Architecture',
        ha='center', va='center', fontsize=26, fontweight='bold',
        color=C_TITLE_BG)
ax.text(14, 17.90,
        'PostgreSQL 16 + PostGIS 3.4   |   Redis 7 (in-memory)'
        '   |   JSON filesystem',
        ha='center', va='center', fontsize=16, color=C_ARROW)


# ════════════════════════════════════════════════════════════
#  ROW 1 – External climate APIs
# ════════════════════════════════════════════════════════════
api_labels = [
    'NASA POWER\nv2.0',
    'Open-Meteo\nArchive',
    'Open-Meteo\nForecast',
    'MET Norway\n(Yr)',
    'NWS Daily\nForecast',
    'NWS\nStations',
]
api_w, api_h = 2.8, 1.2
api_gap = 0.45
total_api_w = len(api_labels) * api_w + (len(api_labels) - 1) * api_gap
api_x0 = (21 - total_api_w) / 2      # centre across the PG-table zone
api_y  = 16.1

for i, label in enumerate(api_labels):
    bx = api_x0 + i * (api_w + api_gap)
    rect = FancyBboxPatch((bx, api_y), api_w, api_h,
                          boxstyle="round,pad=0.1",
                          facecolor='#fdf2f2', edgecolor=C_API, linewidth=2)
    ax.add_patch(rect)
    ax.text(bx + api_w / 2, api_y + api_h / 2, label,
            ha='center', va='center', fontsize=14, fontweight='bold',
            color=C_API, linespacing=1.3)

# arrows API → climate_data
cd_top_x = 6.3
cd_top_y = 15.0

for i in range(len(api_labels)):
    bx = api_x0 + i * (api_w + api_gap) + api_w / 2
    ax.annotate('', xy=(cd_top_x + (i - 2.5) * 0.55, cd_top_y),
                xytext=(bx, api_y),
                arrowprops=dict(arrowstyle='->', color=C_API,
                                lw=1.8, connectionstyle='arc3,rad=0.0'))

ax.text(cd_top_x, 15.35, 'HTTP + JSON  (httpx async)',
        ha='center', va='center', fontsize=14, color=C_API, style='italic')


# ════════════════════════════════════════════════════════════
#  ROW 2 – climate_data  +  api_variables
# ════════════════════════════════════════════════════════════

# --- climate_data  (large, left) ---
draw_table(ax, 1.3, 9.5, 10.0, 5.3, 'climate_data', [
    'PK   id  (SERIAL)',
    '     source_api  (VARCHAR 50)',
    '     latitude  (DOUBLE PRECISION)',
    '     longitude  (DOUBLE PRECISION)',
    '     elevation  (FLOAT)',
    '     date  (DATE)',
    '     raw_data  (JSONB)  \u2190 native API payload',
    '     harmonized_data  (JSONB)  \u2190 standard',
    '     eto_mm_day  (FLOAT)',
    '     quality_flags  (JSONB)',
    'UQ   (source_api, lat, lon, date)',
], C_CORE, title_fs=17, col_fs=14, row_h=0.43)

# --- api_variables  (right-centre) ---
draw_table(ax, 13.0, 11.5, 8.5, 3.3, 'api_variables', [
    'PK   id  (SERIAL)',
    '     source_api  (VARCHAR 50)',
    '     variable_name  (VARCHAR 100)',
    '     standard_name  (VARCHAR 100)',
    '     unit  (VARCHAR 50)',
    '     is_required_for_eto  (BOOLEAN)',
    'UQ   (source_api, variable_name)',
], C_META, title_fs=17, col_fs=14, row_h=0.37)

# dashed semantic link
ax.annotate('',
            xy=(13.0, 12.8), xytext=(11.3, 12.8),
            arrowprops=dict(arrowstyle='->', color=C_ARROW, lw=2,
                            linestyle='dashed'))
ax.text(12.15, 13.2, 'semantic lookup\nvia source_api',
        ha='center', va='bottom', fontsize=13, color=C_ARROW,
        style='italic')


# ════════════════════════════════════════════════════════════
#  ROW 3 – eto_results  +  JSON files  +  Redis
# ════════════════════════════════════════════════════════════

# --- eto_results ---
draw_table(ax, 1.3, 5.4, 9.0, 3.8, 'eto_results', [
    'PK   id  (SERIAL)',
    '     latitude  (DOUBLE PRECISION)',
    '     longitude  (DOUBLE PRECISION)',
    '     date  (DATE)',
    '     eto_mm_day  (FLOAT)',
    '     method  (VARCHAR 50)',
    '     source_api  (VARCHAR 50)',
    '     input_data  (JSONB)',
], C_CORE, title_fs=17, col_fs=14, row_h=0.40)

# arrow climate_data → eto_results
ax.annotate('',
            xy=(5.5, 9.2), xytext=(5.5, 9.5),
            arrowprops=dict(arrowstyle='->', color=C_CORE, lw=2.5))
ax.text(6.1, 9.35, 'FAO-56 PM calculation',
        ha='left', va='center', fontsize=14, color=C_CORE,
        fontweight='bold', style='italic')

# --- JSON historical files ---
jx, jy, jw, jh = 13.0, 10.1, 8.5, 1.2
json_box = FancyBboxPatch((jx, jy), jw, jh, boxstyle="round,pad=0.1",
                          facecolor='#fef9e7', edgecolor=C_JSON,
                          linewidth=2, linestyle='dashed')
ax.add_patch(json_box)
ax.text(jx + jw / 2, jy + jh * 0.62,
        'data/historical/cities/*.json',
        ha='center', va='center', fontsize=14.5, fontweight='bold',
        color='#7d6608', family='monospace')
ax.text(jx + jw / 2, jy + jh * 0.22,
        '27 cities \u00d7 12 months \u00d7 normals/std/P01\u2013P99  |  '
        'LRU cache',
        ha='center', va='center', fontsize=12, color='#7d6608')


# ════════════════════════════════════════════════════════════
#  REDIS 7  (in-memory data store) – right column
# ════════════════════════════════════════════════════════════
rx, ry, rw, rh = 12.5, 4.3, 15.0, 5.5

redis_outer = FancyBboxPatch((rx, ry), rw, rh, boxstyle="round,pad=0.12",
                              facecolor=C_REDIS_BG, edgecolor=C_REDIS,
                              linewidth=3)
ax.add_patch(redis_outer)

ax.text(rx + rw / 2, ry + rh - 0.42,
        'Redis 7  (in-memory data store)',
        ha='center', va='center', fontsize=20, fontweight='bold',
        color=C_REDIS, family='sans-serif')

# 4 namespace sections  (2 × 2 grid)
sec_w  = 6.8
sec_h1 = 1.95    # top row (3 items)
sec_h2 = 1.55    # bottom row (2 items)
sec_gx = 0.5
sec_gy = 0.3
sec_x1 = rx + 0.45
sec_x2 = sec_x1 + sec_w + sec_gx
sec_yt = ry + rh - 1.1   # top of top row

# ① Climate cache  — top-left
draw_redis_section(ax, sec_x1, sec_yt - sec_h1, sec_w, sec_h1,
    '\u2460 Climate Data Cache', [
    'KEY  climate:{src}:{lat}:{lon}:{dates}',
    'VAL  pickle(DataFrame)',
    'TTL  1h (forecast) \u2192 30d (historical)',
], C_REDIS)

# ② Celery broker + results  — top-right
draw_redis_section(ax, sec_x2, sec_yt - sec_h1, sec_w, sec_h1,
    '\u2461 Celery Task Broker + Results', [
    'QUEUE  eto | general | data_download',
    'KEY    celery-task-meta-{uuid}',
    'TTL    24h  (task results)',
], C_REDIS)

# ③ Pub/Sub  — bottom-left
draw_redis_section(ax, sec_x1,
    sec_yt - sec_h1 - sec_gy - sec_h2, sec_w, sec_h2,
    '\u2462 Pub/Sub (WebSocket progress)', [
    'CHANNEL  task:{uuid}',
    'MSG      {pct, stage, timestamp}',
], C_REDIS)

# ④ Rate limits + counters  — bottom-right
draw_redis_section(ax, sec_x2,
    sec_yt - sec_h1 - sec_gy - sec_h2, sec_w, sec_h2,
    '\u2463 Rate Limits & Counters', [
    'KEY  calc_limit:{ip}:{mode}:{date}',
    'KEY  visitors:count | unique:today',
], C_REDIS)


# ════════════════════════════════════════════════════════════
#  Arrows  PostgreSQL ↔ Redis
# ════════════════════════════════════════════════════════════

# climate_data ↔ Redis cache (write-through)
# From climate_data right edge (11.3) to Redis left edge (12.5)
ax.annotate('', xy=(12.5, 8.6), xytext=(11.3, 9.7),
            arrowprops=dict(arrowstyle='<->', color=C_REDIS, lw=2.2,
                            connectionstyle='arc3,rad=0.0'))
ax.text(11.9, 9.45, 'write-through\ncache',
        ha='center', va='center', fontsize=13, color=C_REDIS,
        style='italic', fontweight='bold',
        bbox=dict(boxstyle='round,pad=0.2', facecolor='white',
                  edgecolor=C_REDIS, alpha=0.9))

# eto_results → Redis  (Celery task results)
# From eto_results right edge (10.3) to Redis left edge (12.5)
ax.annotate('', xy=(12.5, 7.0), xytext=(10.3, 7.0),
            arrowprops=dict(arrowstyle='->', color=C_REDIS, lw=2,
                            connectionstyle='arc3,rad=0.0'))
ax.text(11.4, 7.45, 'task results',
        ha='center', va='center', fontsize=13, color=C_REDIS,
        style='italic', fontweight='bold',
        bbox=dict(boxstyle='round,pad=0.15', facecolor='white',
                  edgecolor=C_REDIS, alpha=0.9))

# Redis counters → visitor_stats  (periodic sync)
# From Redis bottom edge down to visitor_stats top edge
ax.annotate('', xy=(14.0, 3.8), xytext=(18.0, 4.3),
            arrowprops=dict(arrowstyle='->', color=C_ADMIN, lw=1.8,
                            linestyle='dashed',
                            connectionstyle='arc3,rad=0.15'))
ax.text(16.5, 4.35, 'periodic sync (Celery Beat)',
        ha='center', va='center', fontsize=13, color=C_ADMIN,
        style='italic',
        bbox=dict(boxstyle='round,pad=0.15', facecolor='white',
                  edgecolor=C_ADMIN, alpha=0.9))


# ════════════════════════════════════════════════════════════
#  ROW 4 – Admin / operational tables  (full width)
# ════════════════════════════════════════════════════════════
admin_specs = [
    ('admin_users', [
        'PK   id  (SERIAL)',
        '     username  (VARCHAR, UQ)',
        '     password_hash  (TEXT)',
        '     role  (VARCHAR 20)',
        '     api_token  (VARCHAR)',
    ]),
    ('visitor_stats', [
        'PK   id  (SERIAL)',
        '     session_id  (VARCHAR)',
        '     ip_address  (INET)',
        '     page_visited  (VARCHAR)',
        '     timestamp  (TIMESTAMPTZ)',
    ]),
    ('user_cache', [
        'PK   id  (SERIAL)',
        '     session_id  (VARCHAR, UQ)',
        '     user_agent  (TEXT)',
        '     cache_size_mb  (FLOAT)',
        '     last_access  (TIMESTAMPTZ)',
    ]),
]
atw  = 7.0
ath  = 3.2
agap = 0.8
total_admin_w = len(admin_specs) * atw + (len(admin_specs) - 1) * agap
ax0 = (28 - total_admin_w) / 2      # centre across full 28 width
ay  = 0.6

for i, (name, cols) in enumerate(admin_specs):
    draw_table(ax, ax0 + i * (atw + agap), ay, atw, ath, name, cols,
               C_ADMIN, title_fs=17, col_fs=14, row_h=0.44)

ax.text(14, 3.85, 'Administration & Analytics (independent tables)',
        ha='center', va='center', fontsize=14, color=C_ADMIN,
        style='italic')


# ════════════════════════════════════════════════════════════
#  Legend
# ════════════════════════════════════════════════════════════
legend_items = [
    mpatches.Patch(facecolor='#fdf2f2', edgecolor=C_API,
                   label='External climate APIs (6)'),
    mpatches.Patch(facecolor='white', edgecolor=C_CORE,
                   label='Core PostgreSQL tables'),
    mpatches.Patch(facecolor='white', edgecolor=C_META,
                   label='Metadata / mapping table'),
    mpatches.Patch(facecolor='white', edgecolor=C_ADMIN,
                   label='Admin / analytics tables'),
    mpatches.Patch(facecolor=C_REDIS_BG, edgecolor=C_REDIS,
                   label='Redis 7 (in-memory store)'),
    mpatches.Patch(facecolor='#fef9e7', edgecolor=C_JSON,
                   label='JSON files (filesystem)'),
]
ax.legend(handles=legend_items, loc='lower right', fontsize=15,
          framealpha=0.95, edgecolor='#bdc3c7', fancybox=True,
          ncol=2, bbox_to_anchor=(0.99, 0.005))


# ════════════════════════════════════════════════════════════
#  Save
# ════════════════════════════════════════════════════════════
out = Path('docs/figures')
out.mkdir(parents=True, exist_ok=True)

plt.tight_layout(pad=0.5)
plt.savefig(out / 'Figure_database_er.png', dpi=300,
            bbox_inches='tight', facecolor='white')
plt.savefig(out / 'Figure_database_er.pdf',
            bbox_inches='tight', facecolor='white')
print("\u2705 Database ER diagram saved  \u2192  docs/figures/Figure_database_er.png + .pdf")
plt.show()