# Technical SOP — Inside Airbnb Gent Dashboard

**Standard Operating Procedure for development, deployment, and maintenance of the Dash geospatial analytics dashboard.**

---

## 1. System Architecture

### 1.1 High-Level Design

```
Browser (client)
    │
    ▼
Flask Dev Server (Werkzeug) :8051
    │
    ▼
Dash Application Instance
    ├── layout.py      → Component Tree (DOM specification)
    ├── charts.py      → Data Layer + Figure Factory
    └── callbacks.py   → Reactive Binding Layer
```

The application follows a **modular Dash pattern** — layout, data, and interactivity are cleanly separated into three modules, wired together by `app.py`.

### 1.2 Module Responsibilities

| Module | Responsibility | Key Exports |
|---|---|---|
| `app.py` | Instantiation, configuration, server launch | `app` (Dash instance) |
| `layout.py` | HTML/DCC component composition, grid structure | `get_app_layout()` |
| `charts.py` | Data ingestion, transformation, Plotly figure generation | `get_price_distribution_chart()`, `get_room_type_pie_chart()`, `get_map()` |
| `callbacks.py` | Input/Output binding, event wiring | `register_callbacks(app)` |

---

## 2. Data Pipeline

### 2.1 Data Sources

| File | Type | Rows | Key Columns |
|---|---|---|---|
| `data/listings.csv` | CSV (UTF-8) | ~2,000+ | `price`, `room_type`, `neighbourhood`, `latitude`, `longitude`, `host_name` |
| `data/neighbourhoods.geojson` | GeoJSON | 25 polygons | `properties.neighbourhood` |

### 2.2 ETL Process

```python
# charts.py — load-on-import singleton pattern
LISTINGS_DF = _load_listings_data()       # pd.read_csv → price coercion
NEIGHBOURHOODS_GEOJSON = _load_geojson()  # json.load → dict
```

**Price cleaning pipeline:**
1. Read CSV with `pd.read_csv(path)`
2. Strip `$` and `,` from `price` column via regex: `r'\$'` → `''`, `,` → `''`
3. Cast to `float64`
4. Store in module-level `LISTINGS_DF` for zero-reload access

**Error handling:** Both loaders catch `Exception`, log to stderr, and return empty DataFrame / `None` to prevent crash-on-start.

### 2.3 GeoJSON Feature Key Contract

The choropleth requires exact alignment between:
- CSV column: `neighbourhood` (listing's neighbourhood name)
- GeoJSON property: `properties.neighbourhood` (polygon feature identifier)

This is enforced in `px.choropleth_mapbox(..., featureidkey="properties.neighbourhood")`.

---

## 3. Callback Architecture

### 3.1 Callback Map

```
┌──────────────────────────────┐
│  price-range-slider          │──── Input ──► update_price_histogram()
│  (RangeSlider 0–500)         │               ▼
└──────────────────────────────┘     ex1A-basic-chart-price-dist (figure)


┌──────────────────────────────┐
│  master-filter-neighbourhood │──── Input ──► update_room_type_pie_chart()
│  (Dropdown)                  │               ▼
└──────────────────────────────┘     ex1B-basic-chart-room-type (figure)

                              │
                              ├──── Input ──► update_map_by_neighbourhood()
                              │               ▼
                              │      ex3-map-visualization (figure)
```

### 3.2 Callback Execution Flow

1. User selects neighbourhood from dropdown → `master-filter-neighbourhood.value` changes
2. Dash invokes **both** `update_room_type_pie_chart` and `update_map_by_neighbourhood` in parallel
3. Each callback:
   - Receives the selected neighbourhood string (or `'All'`)
   - Filters `LISTINGS_DF` via boolean mask: `df[df['neighbourhood'] == selected]`
   - Generates updated Plotly `figure` object
   - Returns figure → Dash diffs & updates DOM

### 3.3 Performance Characteristics

- **Data load**: O(n) on import, O(1) thereafter (global singleton)
- **Filter**: O(n) boolean mask per callback invocation
- **Figure generation**: Plotly Express constructs trace objects in memory — O(n) for scatter, O(n) for histogram binning
- **Network payload**: JSON-serialized figure objects (~50–200 KB per response)
- **No database**: Zero network calls after initial page load; all filtering is in-memory

---

## 4. Component Specification

### 4.1 Price Distribution Histogram

- **Type**: `px.histogram`
- **Bins**: 50 (fixed)
- **Color**: Teal sequential (`px.colors.sequential.Teal[4]`)
- **Dimensions**: 350px height, responsive width
- **Interaction**: Linked to `price-range-slider` (min/max range)
- **Filter logic**: `(price >= min) & (price <= max)`

### 4.2 Room Type Pie Chart

- **Type**: `px.pie`
- **Categories**: `room_type` column values
- **Color mapping**: Fixed discrete map
  - Entire home/apt → `#1f77b4`
  - Private room → `#ff7f0e`
  - Shared room → `#2ca02c`
  - Hotel room → `#d62728`
- **Labels**: Percent + label, positioned outside with leader lines
- **Dimensions**: 350px height

### 4.3 Choropleth + Scatter Map

- **Layer 1 (Choropleth)**: `px.choropleth_mapbox`
  - Color axis: `average_price` (Viridis scale)
  - Aggregation: `groupby('neighbourhood')['price'].mean()`
  - Opacity: 0.7
  - Range capped at 95th percentile to prevent outlier skew

- **Layer 2 (Scatter)**: `px.scatter_mapbox`
  - Individual listing markers
  - Color-coded by `room_type` (same discrete map)
  - Hover data: host name, price, room type
  - Opacity: 0.8

- **Composition**: Scatter traces are added to choropleth figure via `add_trace()`

- **Map Config**:
  - Style: `carto-positron` (light basemap)
  - Center: Mean lat/lon of all listings
  - Zoom: 10.5
  - Height: 500px

### 4.4 Master Filter Dropdown

- **Type**: `dcc.Dropdown`
- **Options**: Dynamically populated from `LISTINGS_DF['neighbourhood'].unique()`
- **Default**: `'All'` (no filter)
- **Width**: 6-column Bootstrap grid, centered

---

## 5. Deployment Guide

### 5.1 Development

```bash
cd src
python app.py
# → http://localhost:8051
# Debug mode: ON (Flask reloader disabled for Python 3.14 compat)
```

### 5.2 Production (Gunicorn)

```bash
pip install gunicorn
gunicorn app:server -b 0.0.0.0:8051 -w 4
```

`app.server` exposes the underlying Flask WSGI application.

### 5.3 Docker (Recommended)

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY src/requirements.txt .
RUN pip install -r requirements.txt
COPY src/ .
EXPOSE 8051
CMD ["gunicorn", "app:server", "-b", "0.0.0.0:8051", "-w", "2"]
```

### 5.4 Environment Variables

| Variable | Default | Description |
|---|---|---|
| `PORT` | `8051` | Server listen port |
| `DEBUG` | `false` | Enable Dash debug mode |
| `DATA_PATH` | `data/` | Override data directory location |

---

## 6. Testing Strategy

### 6.1 Unit Tests

```python
# test_charts.py
def test_price_cleaning():
    """Verify $ and , stripping from price strings."""
    
def test_filter_empty_dataframe():
    """Chart functions return {} when LISTINGS_DF is empty."""
    
def test_neighbourhood_filter():
    """Room type pie chart correctly subsets by neighbourhood."""
```

### 6.2 Integration Tests

```python
# test_dashboard.py
def test_app_starts():
    """Dash app instantiates without errors."""
    
def test_all_callbacks_registered():
    """verify callbacks map to valid component IDs."""
```

### 6.3 Visual Regression

- Screenshot comparison of initial dashboard state
- Validate figure schema: required keys (`data`, `layout`), trace count, color mapping

---

## 7. Code Quality Standards

- **PEP 8** compliant formatting
- **Type hints** recommended for all function signatures
- **Docstrings** required for public functions (Google style)
- **No hardcoded paths** — use module-level constants with fallbacks
- **Fail gracefully** — empty data returns empty figure dicts, never crashes

---

## 8. Known Limitations & Mitigations

| Limitation | Impact | Mitigation |
|---|---|---|
| In-memory data only | Restart required for data refresh | Implement periodic CSV reload via `Interval` component |
| Single-threaded Flask dev server | One user at a time | Use Gunicorn/WSGI in production |
| No caching | Repeated computation on callback | Add `@flask_caching` for expensive aggregations |
| Python 3.14 incompatibility | `pkgutil.find_loader` removed | Hot reload disabled; use watchdog-based reloader |

---

## 9. Changelog

| Version | Date | Changes |
|---|---|---|
| 1.0.0 | 2025-10 | Initial release — histogram, pie chart, choropleth map |
| 1.0.1 | 2026-08 | Python 3.14 compatibility fix, portfolio restructuring |

---

*This SOP is maintained alongside the codebase. Update with each significant architectural change.*
