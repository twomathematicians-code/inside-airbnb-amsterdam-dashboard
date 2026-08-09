# Technical SOP — Inside Airbnb Amsterdam Business Intelligence Dashboard

**Standard Operating Procedure** — architecture, deployment, testing, and maintenance.

---

## 1. System Architecture

### 1.1 Multi-Tab Dashboard Design

```
┌─────────────────────────────────────────────────────────┐
│                  Dash Application (app.py)               │
│                                                         │
│  ┌───────────────────────────────────────────────────┐  │
│  │ KPI Header (6 cards)  │  🟢 LIVE refresh badge   │  │
│  ├───────────────────────────────────────────────────┤  │
│  │  Tab 1: Market    │ Tab 2: Business  │ Tab 3:    │  │
│  │  Overview         │ Intelligence     │ Policy &  │  │
│  │                   │                  │ Compliance│  │
│  │  • Price hist     │ • Occupancy bar  │ • Min     │  │
│  │  • Room type pie  │ • Revenue box    │   nights  │  │
│  │  • Choropleth map │ • Demand-supply  │ • License │  │
│  │                   │ • Host conc.     │ • Occ vs  │  │
│  │                   │ • Pricing guide  │   price   │  │
│  │                   │ • Value matrix   │ • Policy  │  │
│  │                   │ • Revenue tree   │   recs    │  │
│  └───────────────────────────────────────────────────┘  │
│                                                         │
│  dcc.Interval (5 min) ──► KPI refresh + timestamp       │
└─────────────────────────────────────────────────────────┘
```

### 1.2 Module Map

| Module | Lines | Exports | Responsibility |
|---|---|---|---|
| `app.py` | ~40 | `app`, `server` | Instantiation, WSGI export, env config |
| `layout.py` | ~290 | `get_app_layout()` | 4-tab DOM, KPI header, freshness badge, filters |
| `charts.py` | ~460 | 14 figure functions + 10 placeholder components | Data pipeline, all Plotly figure generation |
| `callbacks.py` | ~200 | `register_callbacks(app)` | 15+ Input/Output bindings, live refresh logic |

---

## 2. Chart Inventory

### Tab 1 — Market Overview (3 charts)
| ID | Function | Type | Filter |
|---|---|---|---|
| `ex1A-basic-chart-price-dist` | `get_price_distribution_chart` | `px.histogram` | Price range slider |
| `ex1B-basic-chart-room-type` | `get_room_type_pie_chart` | `px.pie` | Master neighbourhood dropdown |
| `ex3-map-visualization` | `get_map` | `px.choropleth_mapbox` + `px.scatter_mapbox` | Master neighbourhood dropdown |

### Tab 2 — Business Intelligence (7 charts)
| ID | Function | Type | Business Question |
|---|---|---|---|
| `bi-occupancy-chart` | `get_occupancy_chart` | `px.bar` (horizontal) | Which areas have highest occupancy? |
| `bi-revenue-box` | `get_revenue_boxplot` | `px.box` | What's the revenue spread by room type? |
| `bi-demand-supply` | `get_demand_supply_chart` | `px.scatter` (bubble) | Where is demand outpacing supply? |
| `bi-host-concentration` | `get_host_concentration_chart` | `px.pie` (donut) | Is the market professionalized? |
| `bi-pricing-position` | `get_pricing_position_chart` | `go.Bar` (grouped) | How should I price my listing? |
| `bi-rating-price` | `get_rating_price_matrix` | `px.scatter` | What's the value sweet spot? |
| `bi-revenue-treemap` | `get_revenue_treemap` | `px.treemap` | Where's the revenue concentrated? |

### Tab 3 — Policy & Compliance (3 charts)
| ID | Function | Type | Policy Question |
|---|---|---|---|
| `policy-min-nights` | `get_minimum_nights_chart` | `px.histogram` (stacked) | Are minimum stays a barrier? |
| `policy-license` | `get_license_compliance_chart` | `go.Bar` (stacked, h) | Which areas lack compliance? |
| `policy-occupancy-timeline` | `get_occupancy_timeline` | `make_subplots` (dual-axis) | Price vs occupancy trade-off? |

---

## 3. Data Pipeline

### 3.1 Derived Metrics (computed at load)

```python
# All derived in _load_listings_data() — computed once, used everywhere
df['booked_days']        = 365 - df['availability_365']
df['occupancy_pct']      = (df['booked_days'] / 365 * 100).round(1)
df['est_annual_revenue'] = (df['price'] * df['booked_days']).round(2)
df['host_category']      = pd.cut(calculated_host_listings_count, bins=[0,1,5,inf])
df['license_status']     = df['license'].notna().map({True: 'Licensed', False: 'Unlicensed'})
```

### 3.2 Data Columns Used

| Column | Type | Used In |
|---|---|---|
| `price` | float | 8 charts |
| `room_type` | categorical | 7 charts |
| `neighbourhood` | categorical | 7 charts |
| `availability_365` | int → `booked_days`, `occupancy_pct` | 4 charts |
| `reviews_per_month` | float | 2 charts |
| `calculated_host_listings_count` | int → `host_category` | 1 chart |
| `minimum_nights` | int | 1 chart |
| `license` | str → `license_status` | 1 chart |
| `latitude`, `longitude` | float | 1 chart |

---

## 4. Callback Architecture

### 4.1 Filter Independence

Each tab has its **own** neighbourhood dropdown filter:
- `master-filter-neighbourhood` → Tab 1 (Room Type Pie + Map)
- `bi-neighbourhood-filter` → Tab 2 (Occupancy, Revenue Box, Host Conc, Revenue Treemap)
- `policy-neighbourhood-filter` → Tab 3 (Min Nights)

This prevents cross-tab filter interference — changing Tab 1's filter doesn't affect Tab 2.

### 4.2 Live Refresh Mechanism

```
dcc.Interval(id='live-refresh-interval', interval=300000ms)
    │
    ├──► Output: freshness-badge.children (timestamp update)
    └──► Output: kpi-header-row.children (KPI recalculation)
```

The interval triggers `charts.get_kpi_metrics()` which recomputes all 6 KPIs from the in-memory DataFrame. No re-reading of CSV — sub-millisecond refresh.

### 4.3 Callback Count

| Category | Count |
|---|---|
| Tab 1 (Market Overview) | 3 |
| Tab 2 (Business Intelligence) | 7 |
| Tab 3 (Policy & Compliance) | 3 |
| Live Refresh | 1 |
| **Total** | **14** |

---

## 5. Deployment

### 5.1 Local Development
```bash
cd src && python app.py          # Debug off, port 8051
DEBUG=true python app.py          # Debug mode on
```

### 5.2 Docker
```bash
docker compose up -d              # Build + start
docker compose logs -f            # Follow logs
docker compose down               # Stop
```

### 5.3 Render.com (Free Tier)
1. Fork repo → connect in Render dashboard
2. `render.yaml` auto-detected — no manual config needed
3. Deploys at `https://airbnb-amsterdam-dashboard.onrender.com`
4. Free tier: spins down after 15 min inactivity, auto-wakes on next request

### 5.4 Environment Variables

| Variable | Default | Description |
|---|---|---|
| `PORT` | `8051` | Server listen port |
| `DEBUG` | `false` | Enable Dash debug mode |
| `HOST` | `127.0.0.1` | Bind address |

---

## 6. Performance Profile

| Operation | Complexity | Typical Time |
|---|---|---|
| Data load (startup) | O(n) | ~100ms |
| KPI calculation | O(1) mem access | <1ms |
| Filter + chart render | O(n) boolean mask | ~50-200ms |
| Map render (choropleth + scatter) | O(n) | ~500ms |
| Live refresh (all KPIs) | O(1) | <5ms |

Memory: ~30MB (DataFrame + GeoJSON in memory)

---

## 7. Testing Strategy

### Unit
- `test_price_cleaning()` — verify $ and , stripping
- `test_derived_columns()` — booked_days, occupancy_pct, host_category
- `test_empty_dataframe_returns_empty_dict()` — graceful degradation

### Integration
- `test_all_tabs_render()` — verify no exceptions on layout build
- `test_all_callbacks_registered()` — 14 callbacks bound
- `test_live_refresh_updates_timestamp()` — interval triggers correctly

### Visual Regression
- Export all 14 charts via `export_charts.py`
- Compare pixel hashes against baseline

---

## 8. Business Use Case Mapping

| Chart | Stakeholder | Decision It Supports |
|---|---|---|
| Occupancy Bar | Property Owner | "Should I raise/lower my price based on area occupancy?" |
| Revenue Boxplot | Investor | "Which room type yields the best revenue distribution?" |
| Demand–Supply Matrix | Tourism Board | "Where should we direct marketing spend?" |
| Host Concentration | Regulator | "Is the market dominated by professional operators?" |
| Pricing Position Guide | Host | "Is my €85/night private room competitive?" |
| Value Matrix | Host | "Am I underpriced for my demand level?" |
| Revenue Treemap | Investor | "Which neighbourhood × room type combo generates most revenue?" |
| Min Nights Histogram | Regulator | "What policy threshold would impact the fewest listings?" |
| License Compliance | Regulator | "Where should enforcement focus?" |
| Occupancy vs Price | Host | "What's the optimal price for maximum occupancy?" |

---

## 9. Changelog

| Version | Date | Changes |
|---|---|---|
| 1.0.0 | 2025-10 | Initial: 3 charts, 1 filter |
| 2.0.0 | 2026-08 | Major: 14 charts, 4 tabs, KPI header, live refresh, Docker, cloud deployment |

---

*Maintained alongside the codebase. Update on architectural changes.*
