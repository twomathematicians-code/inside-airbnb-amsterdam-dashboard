# 🏠 Inside Airbnb Gent — Housing Displacement Dashboard

**Production-grade interactive geospatial dashboard** analyzing the impact of short-term rentals on housing availability in Ghent, Belgium. Built with **Dash + Plotly**, featuring real-time cross-filtering, choropleth mapping, and statistical distribution analysis.

## 📸 Visualizations

### Price Distribution Analysis
<p align="center">
  <img src="assets/chart-price-histogram.png" alt="Price Distribution Histogram" width="800"/>
</p>
*Interactive histogram with range slider — filter listings by nightly price to identify market segments and pricing density.*

### Housing Displacement by Room Type
<p align="center">
  <img src="assets/chart-room-type-pie.png" alt="Room Type Pie Chart" width="600"/>
</p>
*Proportion of entire homes vs. shared/private rooms — quantifies units removed from long-term housing. Filterable by neighbourhood.*

### Geospatial Concentration & Price Inequality
<p align="center">
  <img src="assets/chart-map.png" alt="Choropleth Map with Scatter Overlay" width="800"/>
</p>
*Choropleth map of average price per neighbourhood + individual listing scatter overlay. Master neighbourhood filter drives both the map and pie chart simultaneously.*

---

## 📊 Overview

This dashboard transforms raw Airbnb listing data into actionable intelligence for housing policy. It reveals three critical dimensions of the short-term rental market:

| Dimension | Visualization | Insight |
|---|---|---|
| **Price Structure** | Histogram with range slider | Price distribution density & market segmentation |
| **Housing Displacement** | Interactive pie chart | Share of entire homes removed from long-term market |
| **Spatial Inequality** | Choropleth + scatter overlay | Geographic concentration of listings & price disparity |

A **single master filter** (neighbourhood dropdown) drives two linked views simultaneously — demonstrating reactive, event-driven dashboard architecture.

---

## 🎯 Key Findings

- **Displacement crisis**: "Entire home/apt" dominates — each listing represents a unit lost to the long-term rental pool
- **Tourism-saturated pricing**: Majority of listings cluster below €150/night, competing with budget accommodation
- **Geographic inequality**: Historic city center (Binnenstad) shows disproportionate listing density with prices reaching ~€250/night
- **Policy implications**: Evidence supports targeted zoning interventions in high-density neighbourhoods

---

## 🛠 Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Framework** | [Dash 3.x](https://dash.plotly.com/) | Reactive web application server |
| **Visualization** | [Plotly Express](https://plotly.com/python/plotly-express/) | Interactive charts, choropleth maps |
| **UI** | [Dash Bootstrap Components](https://dash-bootstrap-components.opensource.faculty.ai/) | Responsive MINTY-themed layout |
| **Data** | [Pandas](https://pandas.pydata.org/) | ETL pipeline, aggregation, filtering |
| **Geospatial** | GeoJSON + Mapbox | Neighbourhood boundary rendering |
| **Language** | Python 3.9+ | Full-stack implementation |

---

## 🏗 Architecture

```
┌─────────────────────────────────────────────────┐
│                  Dash Application                │
│                                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────────┐  │
│  │ layout.py │  │charts.py │  │ callbacks.py │  │
│  │           │  │          │  │              │  │
│  │ • DOM     │  │ • ETL    │  │ • Event      │  │
│  │ • Filters │  │ • Plots  │  │   binding    │  │
│  │ • Grid    │  │ • Maps   │  │ • Reactive   │  │
│  └─────┬─────┘  └────┬─────┘  └──────┬───────┘  │
│        │             │               │          │
│  ┌─────┴─────────────┴───────────────┴─────┐    │
│  │              app.py (entry)             │    │
│  │     Dash() → layout → callbacks         │    │
│  └─────────────────┬───────────────────────┘    │
└────────────────────┼────────────────────────────┘
                     │
          ┌──────────┴──────────┐
          │                     │
     listings.csv      neighbourhoods.geojson
```

### Data Flow

1. **Module load**: `charts.py` loads CSV + GeoJSON into global `LISTINGS_DF` and `NEIGHBOURHOODS_GEOJSON` (singleton pattern)
2. **Initial render**: `layout.py` calls `charts.get_*()` with default parameters → static `dcc.Graph` components
3. **User interaction**: `callbacks.py` listens to `Input` changes (dropdown, slider) → calls chart functions → returns updated `figure` objects
4. **Re-render**: Dash diffs the figure and updates only changed traces in the DOM

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- pip

```bash
# Clone
git clone https://github.com/twomathematicians-code/inside-airbnb-gent-dashboard.git
cd inside-airbnb-gent-dashboard

# Install
pip install -r src/requirements.txt

# Run
cd src
python app.py
```

Open **http://localhost:8051**

---

## 📁 Project Structure

```
├── README.md
├── TECHNICAL_SOP.md          # Architecture & engineering deep-dive
├── LICENSE
├── .gitignore
├── assets/                   # Screenshots & media
└── src/
    ├── app.py                # Application entry point
    ├── layout.py             # DOM composition & component tree
    ├── charts.py             # Data pipeline & Plotly figure factory
    ├── callbacks.py          # Reactive event binding
    ├── requirements.txt      # Pinned dependencies
    └── data/
        ├── listings.csv            # Airbnb listing records
        └── neighbourhoods.geojson  # Ghent boundary polygons
```

---

## 🔒 License

This project is licensed under the **MIT License** — see [LICENSE](LICENSE) for details.

---

## 📊 Data Attribution

Data sourced from [Inside Airbnb](http://insideairbnb.com/get-the-data.html), licensed under [Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/). All data rights belong to their respective owners. This project is an independent analysis and is not affiliated with Airbnb Inc.

---

## ⭐ Skills Demonstrated

- **Geospatial data visualization** — Choropleth + scatter map overlays with Mapbox
- **Reactive dashboard engineering** — Dash callbacks, cross-filtering, state management
- **Statistical EDA** — Price distribution analysis, categorical proportion quantification
- **Data pipeline design** — CSV parsing, type coercion, GeoJSON integration
- **UI/UX for data products** — Bootstrap theming, responsive grid layout, interactive controls
- **Production Python** — Modular architecture, separation of concerns, clean code patterns

---

*Built as a demonstration of full-stack data visualization engineering capabilities.*
