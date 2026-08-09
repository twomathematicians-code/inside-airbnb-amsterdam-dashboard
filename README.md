# Inside Airbnb Gent Dashboard 🏠📊

**Interactive Data Visualization Lab — Lab 01**  
*Mahesh Pravinsinh Solanki & Furaha Chaula*

A Dash/Plotly web dashboard that analyzes **Airbnb listings in Ghent, Belgium** (2025) to investigate the impact of short-term rentals on housing availability and residential communities.

---

## 📸 Dashboard Overview

The dashboard provides three interactive visualizations:

1. **Price Distribution Histogram** — Frequency of daily rental prices with a range slider filter
2. **Room Type Pie Chart** — Proportion of housing unit types (Entire home, Private room, Shared room, Hotel room) filtered by neighbourhood
3. **Spatial Concentration Map** — Choropleth map of average prices per neighbourhood with individual listing scatter overlay

**Master Filter:** A neighbourhood dropdown that filters both the Room Type chart and the Map simultaneously.

---

## 🎯 Key Insights

- **Housing Displacement:** "Entire home/apt" dominates the market, directly removing housing units from the long-term rental pool
- **Pricing Structure:** Most listings cluster below €150/night — a high-volume, tourism-focused market
- **Spatial Inequality:** The historic city center ("Binnenstad" area) shows disproportionately high listing density and prices (up to ~€250/night)

---

## 🛠 Tech Stack

| Technology | Purpose |
|---|---|
| [Dash](https://dash.plotly.com/) | Web application framework |
| [Plotly Express](https://plotly.com/python/plotly-express/) | Interactive charts & maps |
| [Dash Bootstrap Components](https://dash-bootstrap-components.opensource.faculty.ai/) | UI styling (MINTY theme) |
| [Pandas](https://pandas.pydata.org/) | Data manipulation |
| [GeoJSON](https://geojson.org/) | Neighbourhood boundary data |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- pip

### Installation

```bash
# Clone the repository
git clone https://github.com/twomathematicians-code/inside-airbnb-gent-dashboard.git
cd inside-airbnb-gent-dashboard

# Install dependencies
pip install -r src/requirements.txt

# Run the dashboard
cd src
python app.py
```

Open your browser to **http://localhost:8051**

---

## 📁 Project Structure

```
├── README.md
├── .gitignore
└── src/
    ├── app.py              # Main application entry point
    ├── layout.py           # UI layout components
    ├── charts.py           # Data loading & Plotly chart generation
    ├── callbacks.py        # Dash interactive callbacks
    ├── requirements.txt    # Python dependencies
    └── data/
        ├── listings.csv            # Airbnb listings data
        └── neighbourhoods.geojson  # Neighbourhood boundaries
```

---

## 📊 Data Source

Data from [Inside Airbnb](http://insideairbnb.com/get-the-data.html), licensed under [Creative Commons Attribution 4.0 International License](https://creativecommons.org/licenses/by/4.0/).

---

## 👨‍🎓 Authors

- **Mahesh Pravinsinh Solanki** — [GitHub](https://github.com/twomathematicians-code)
- **Furaha Chaula**

*Created for Interactive Data Visualizations Lab, Semester 02, 2025*
