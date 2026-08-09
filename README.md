# 🏠 Inside Airbnb Amsterdam — Strategic Intelligence Dashboard

**Production-grade market intelligence platform** for Airbnb housing analytics — 7 tabs, 20+ visualizations, live refresh, early warning system, automated briefings, and one-click cloud deployment.

<p align="center">
  <img src="assets/chart-map.png" alt="Amsterdam Geospatial Intelligence" width="800"/>
</p>

---

## 🧠 Architecture: EU Policy Intelligence → Housing Market Intelligence

This dashboard implements the **full intelligence cycle** — from raw data ingestion to automated strategic briefings:

```
┌──────────────────────────────────────────────────────────────┐
│                   DATA ENGINEERING LAYER                     │
│  Inside Airbnb CSV + GeoJSON → Pandas ETL → Derived Metrics  │
├──────────────────────────────────────────────────────────────┤
│                    ANALYTICS ENGINE                          │
│  Market Surveillance · Risk Scoring · Anomaly Detection      │
│  Stakeholder Profiling · Concentration Analysis (HHI)        │
├──────────────────────────────────────────────────────────────┤
│                  STRATEGIC INTELLIGENCE                      │
│  Early Warning System · Automated Briefings                  │
│  Opportunity Scoring · Strategic Positioning Matrix          │
├──────────────────────────────────────────────────────────────┤
│                   BUSINESS LAYER                             │
│  Data Explorer · ROI Calculator · Neighbourhood Comparison   │
│  Policy Recommendations · CSV Export                         │
└──────────────────────────────────────────────────────────────┘
```

---

## 📊 Dashboard Tabs

### 📍 Market Overview
Price distribution, room type displacement pie, interactive choropleth map with master filter.

### 💼 Business Intelligence (7 charts)
Occupancy rates, revenue boxplots, demand–supply matrix, host concentration, pricing percentile guide, value matrix, revenue treemap.

### 📋 Policy & Compliance
Minimum nights distribution, license compliance tracking, occupancy–price optimization, actionable policy recommendations.

### 🔍 Data Explorer
Search by host/listing name, filter by neighbourhood/room type/price range, sortable DataTable, one-click CSV download.

### 🧮 ROI Calculator + Comparison
Revenue projection (price × occupancy × listings) with market benchmarks. Side-by-side neighbourhood comparison across 10 KPIs.

### 🧠 Strategic Intelligence (NEW)
| Component | Description |
|---|---|
| **🚨 Early Warning System** | Auto-detected alerts: high-risk areas, occupancy anomalies, price overheating, compliance gaps |
| **📊 Risk–Opportunity Matrix** | Strategic positioning scatter — 4-quadrant analysis of all 22 neighbourhoods |
| **📉 Price Volatility Index** | CV% per neighbourhood with green/yellow/red indicators |
| **🏛️ Market Concentration (HHI)** | Herfindahl-Hirschman Index — antitrust-style revenue concentration measurement |
| **☀️ Stakeholder Influence Map** | Sunburst: Host Type → Neighbourhood → Revenue Share |
| **📊 Host Professionalization** | Stacked % of Individual / Small / Professional operators per area |
| **🤖 Automated Market Briefing** | Rule-based AI narrative: demand hotspots, regulatory risk, opportunities, 3 recommended actions |

---

## 🎯 Business Problems Solved

| Stakeholder | Problem | Dashboard Solution |
|---|---|---|
| **Property Owners / Hosts** | "How should I price?" | Pricing guide, ROI calculator, volatility index |
| **Real Estate Investors** | "Which neighbourhood?" | Risk–Opportunity matrix, HHI concentration, revenue treemap |
| **Tourism Boards** | "Where are visitors?" | Demand proxy mapping, occupancy heat maps |
| **City Regulators** | "Who's non-compliant?" | License compliance, professionalization tracking, policy recs |
| **Policy Analysts** | "What's the market structure?" | Stakeholder sunburst, host concentration, automated briefings |

---

## 🔄 Live Features

- 🟢 **Auto-refresh** every 5 minutes — KPIs, early warnings, and briefings update automatically
- **6 KPI cards**: Listings, Avg Price, Occupancy, Revenue, Entire Home Share, License Compliance
- **12-point Early Warning System** with color-coded risk levels
- **Automated narrative briefings** generated from live data

---

## ☁️ Deploy Live — One Click

<p align="center">
  <a href="https://render.com/deploy?repo=https://github.com/twomathematicians-code/inside-airbnb-amsterdam-dashboard">
    <img src="https://render.com/images/deploy-to-render-button.svg" alt="Deploy to Render" height="40"/>
  </a>
</p>

Click the button above → sign in with GitHub → Render auto-detects `render.yaml` → deploys in ~3 minutes.

**Or manually:**
1. Fork → [github.com/twomathematicians-code/inside-airbnb-amsterdam-dashboard](https://github.com/twomathematicians-code/inside-airbnb-amsterdam-dashboard)
2. Go to [dashboard.render.com](https://dashboard.render.com) → **New Web Service**
3. Connect repo → Render auto-detects `render.yaml` → **Deploy**
4. Live at `https://airbnb-amsterdam-dashboard.onrender.com`

### Docker (Any Cloud)
```bash
docker compose up -d
# → http://localhost:8051
```

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| Framework | Dash 3.x + Flask + Gunicorn |
| Charts | Plotly Express, Graph Objects, Sunburst |
| Data | Pandas, NumPy, GeoJSON |
| UI | Dash Bootstrap Components (MINTY) |
| Analytics | Z-score anomaly detection, HHI, CV%, composite risk scoring |
| Deployment | Docker, Render, Railway, Fly.io |

---

## 🚀 Quick Start

```bash
git clone https://github.com/twomathematicians-code/inside-airbnb-amsterdam-dashboard.git
cd inside-airbnb-amsterdam-dashboard/src
pip install -r requirements.txt
python app.py
# → http://localhost:8051
```

---

## 📁 Structure

```
├── README.md · TECHNICAL_SOP.md · LICENSE
├── Dockerfile · docker-compose.yml · render.yaml
├── assets/ (14 chart screenshots)
└── src/
    ├── app.py            # Entry point + WSGI server
    ├── layout.py         # 7-tab DOM composition
    ├── charts.py         # 25+ chart/analytics functions
    ├── callbacks.py      # 20+ reactive callbacks
    └── data/
        ├── listings.csv           # 16,770 Amsterdam listings
        └── neighbourhoods.geojson # 22 neighbourhoods
```

## 📊 Data

Amsterdam listings (June 2026) from [Inside Airbnb](http://insideairbnb.com/get-the-data.html), CC BY 4.0. Independent analysis — not affiliated with Airbnb Inc.

## 🔒 License

MIT — see [LICENSE](LICENSE)
