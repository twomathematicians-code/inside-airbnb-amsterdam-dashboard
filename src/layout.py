# layout.py
"""
Dashboard DOM composition — multi-tab business intelligence layout.
Uses Dash Bootstrap Components for responsive grid.
"""

from dash import dcc, html
import dash_bootstrap_components as dbc
import charts
from datetime import datetime


# ═══════════════════════════════════════════════════════
#  SHARED COMPONENTS
# ═══════════════════════════════════════════════════════

def get_kpi_header():
    """Live KPI summary row at top of dashboard."""
    kpi = charts.get_kpi_metrics()
    if not kpi:
        return html.Div()

    return dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H4(kpi['total_listings'], className="card-title text-center mb-0"),
                html.P("Total Listings", className="text-muted text-center small mb-0")
            ])
        ], color="light", outline=True), width=2),

        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H4(kpi['avg_price'], className="card-title text-center mb-0"),
                html.P("Avg. Nightly Price", className="text-muted text-center small mb-0")
            ])
        ], color="light", outline=True), width=2),

        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H4(kpi['avg_occupancy'], className="card-title text-center mb-0"),
                html.P("Avg. Occupancy", className="text-muted text-center small mb-0")
            ])
        ], color="light", outline=True), width=2),

        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H4(kpi['total_est_revenue'], className="card-title text-center mb-0"),
                html.P("Est. Annual Revenue", className="text-muted text-center small mb-0")
            ])
        ], color="light", outline=True), width=2),

        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H4(kpi['entire_home_pct'], className="card-title text-center mb-0"),
                html.P("Entire Home Share", className="text-muted text-center small mb-0")
            ])
        ], color="warning", outline=True), width=2),

        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H4(kpi['licensed_pct'], className="card-title text-center mb-0"),
                html.P("License Compliance", className="text-muted text-center small mb-0")
            ])
        ], color="success" if float(kpi['licensed_pct'].replace('%', '')) > 50 else "danger",
           outline=True), width=2),
    ], className="g-2 mb-3", id="kpi-header-row")


def get_data_freshness_badge():
    """Shows last refresh timestamp and live indicator."""
    return html.Div([
        html.Span("🟢 LIVE ", className="badge bg-success me-2"),
        html.Small(f"Last refreshed: {datetime.now().strftime('%H:%M:%S')} | "
                   f"Auto-refresh every 5 min", className="text-muted"),
    ], className="text-end mb-2", id="freshness-badge")


def get_neighbourhood_filter(filter_id, label="Filter by Neighbourhood"):
    """Reusable neighbourhood dropdown filter."""
    listings = charts.LISTINGS_DF
    options = [{'label': 'All Neighbourhoods', 'value': 'All'}]
    if not listings.empty:
        options.extend([{'label': n, 'value': n}
                        for n in sorted(listings['neighbourhood'].unique())])

    return dbc.Row(dbc.Col([
        html.Label(label, className="fw-bold"),
        dcc.Dropdown(id=filter_id, options=options, value='All', clearable=False)
    ], width=4), className="mb-3", justify="start")


# ═══════════════════════════════════════════════════════
#  TAB 1 — MARKET OVERVIEW
# ═══════════════════════════════════════════════════════

def tab_market_overview():
    return dbc.Tab(label="📍 Market Overview", tab_id="tab-market", children=[
        html.Br(),
        html.H3("Master Filter: Neighbourhood Selector", className="mt-2"),
        html.P("This filter drives the Room Type chart and Map simultaneously.",
               className="text-muted"),
        get_neighbourhood_filter("master-filter-neighbourhood"),

        # Price slider + charts
        dbc.Row(dbc.Col([
            html.Label("Price Range Filter for Histogram (€):", className="fw-bold"),
            dcc.RangeSlider(
                id='price-range-slider', min=0, max=500, step=10, value=[0, 250],
                marks={i: f'€{i}' for i in range(0, 501, 50)},
                tooltip={"placement": "bottom", "always_visible": True}
            ),
        ]), className="mb-3"),

        dbc.Row([
            dbc.Col(charts.get_basic_chart_A(), width=6),
            dbc.Col(charts.get_basic_chart_B(), width=6),
        ], className="mb-4"),

        dbc.Row(dbc.Col(charts.get_map_component()), className="mb-4"),
    ])


# ═══════════════════════════════════════════════════════
#  TAB 2 — BUSINESS INTELLIGENCE
# ═══════════════════════════════════════════════════════

def tab_business_intelligence():
    return dbc.Tab(label="💼 Business Intelligence", tab_id="tab-bi", children=[
        html.Br(),
        html.H3("Revenue, Occupancy & Market Dynamics", className="mt-2"),
        get_neighbourhood_filter("bi-neighbourhood-filter"),

        # Row 1: Occupancy + Revenue Boxplot
        dbc.Row([
            dbc.Col(charts.get_occupancy_component(), width=6),
            dbc.Col(charts.get_revenue_box_component(), width=6),
        ], className="mb-4"),

        # Row 2: Demand-Supply Matrix + Host Concentration
        dbc.Row([
            dbc.Col(charts.get_demand_supply_component(), width=6),
            dbc.Col(charts.get_host_concentration_component(), width=6),
        ], className="mb-4"),

        # Row 3: Pricing Position Guide + Value Matrix
        dbc.Row([
            dbc.Col(charts.get_pricing_position_component(), width=6),
            dbc.Col(charts.get_rating_price_component(), width=6),
        ], className="mb-4"),

        # Row 4: Revenue Treemap
        dbc.Row(dbc.Col(charts.get_revenue_treemap_component()), className="mb-4"),
    ])


# ═══════════════════════════════════════════════════════
#  TAB 3 — POLICY & COMPLIANCE
# ═══════════════════════════════════════════════════════

def tab_policy_compliance():
    return dbc.Tab(label="📋 Policy & Compliance", tab_id="tab-policy", children=[
        html.Br(),
        html.H3("Regulatory Impact & Housing Policy Analytics", className="mt-2"),
        get_neighbourhood_filter("policy-neighbourhood-filter"),

        # Row 1: Occupancy vs Price + Minimum Nights
        dbc.Row([
            dbc.Col(charts.get_occupancy_timeline_component(), width=6),
            dbc.Col(charts.get_min_nights_component(), width=6),
        ], className="mb-4"),

        # Row 2: License Compliance
        dbc.Row(dbc.Col(charts.get_license_compliance_component()), className="mb-4"),

        # Policy insights card
        dbc.Row(dbc.Col(dbc.Card([
            dbc.CardHeader(html.H4("📌 Policy Recommendations", className="mb-0")),
            dbc.CardBody([
                html.Ul([
                    html.Li("Introduce mandatory licensing with visible registry IDs — "
                            "enforcement correlates with higher compliance rates."),
                    html.Li("Cap entire-home listings in high-density zones (>60% entire-home share) "
                            "to protect long-term rental stock."),
                    html.Li("Set progressive minimum-night thresholds (3+ nights) in historic center "
                            "to discourage transient tourism overflow."),
                    html.Li("Implement dynamic pricing transparency — require hosts to display "
                            "total cost including all fees upfront."),
                    html.Li("Incentivize private-room hosting over entire-home conversions "
                            "through differentiated tax treatment."),
                ])
            ])
        ], color="info", outline=True)), className="mb-4"),
    ])


# ═══════════════════════════════════════════════════════
#  TAB 4 — ABOUT & METHODOLOGY
# ═══════════════════════════════════════════════════════

def tab_about():
    return dbc.Tab(label="ℹ️ About", tab_id="tab-about", children=[
        html.Br(),
        dbc.Row([
            dbc.Col(dbc.Card([
                dbc.CardHeader(html.H4("Data Sources", className="mb-0")),
                dbc.CardBody(dcc.Markdown("""
                - **Inside Airbnb** — [insideairbnb.com](http://insideairbnb.com/get-the-data.html)
                - Data licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
                - Ghent listings snapshot (2025)
                - Neighbourhood boundaries via GeoJSON
                """))
            ], className="mb-3"), width=6),

            dbc.Col(dbc.Card([
                dbc.CardHeader(html.H4("Methodology", className="mb-0")),
                dbc.CardBody(dcc.Markdown("""
                - **Occupancy** estimated as `(365 - availability_365) / 365`
                - **Revenue** projected as `price × booked_days`
                - **Demand proxy** derived from `reviews_per_month`
                - **Host category** based on `calculated_host_listings_count`
                - All currency in Euros (€)
                """))
            ], className="mb-3"), width=6),
        ]),

        dbc.Row(dbc.Col(dbc.Card([
            dbc.CardHeader(html.H4("Business Use Cases", className="mb-0")),
            dbc.CardBody(dcc.Markdown("""
            | Stakeholder | Use Case |
            |---|---|
            | **Property Owners / Hosts** | Competitive pricing, occupancy benchmarking, revenue optimization |
            | **Real Estate Investors** | Neighbourhood ROI analysis, demand hotspot identification |
            | **Tourism Boards** | Visitor distribution, capacity planning, seasonal trend analysis |
            | **City Planners & Regulators** | Housing displacement quantification, compliance monitoring, policy impact assessment |
            | **Researchers & Analysts** | Market structure analysis, spatial inequality measurement |
            """))
        ], color="light")), className="mb-4"),

        html.Hr(),
        html.Footer(html.Small(
            "Data from Inside Airbnb, licensed under Creative Commons Attribution 4.0. "
            "This is an independent analysis not affiliated with Airbnb Inc.",
            className="text-muted"
        ), className="text-center mb-4"),
    ])


# ═══════════════════════════════════════════════════════
#  MAIN LAYOUT COMPOSITION
# ═══════════════════════════════════════════════════════

def get_app_layout():
    return dbc.Container([
        # Hidden interval for live refresh
        dcc.Interval(id='live-refresh-interval', interval=5 * 60 * 1000, n_intervals=0),

        # Hidden div for storing refresh timestamp
        html.Div(id='refresh-timestamp-store', style={'display': 'none'}),

        # Header
        dbc.Row(dbc.Col(html.H1(
            "Inside Airbnb Gent — Business Intelligence Dashboard",
            className="mt-3 mb-1"
        ))),

        dbc.Row(dbc.Col(
            html.P("Real-time housing market analytics for data-driven decisions",
                   className="text-muted mb-2")
        )),

        # Live freshness badge
        get_data_freshness_badge(),

        # KPI Cards
        get_kpi_header(),

        # Tabs
        dbc.Tabs([
            tab_market_overview(),
            tab_business_intelligence(),
            tab_policy_compliance(),
            tab_about(),
        ], id="dashboard-tabs", active_tab="tab-market", className="mb-4"),

    ], fluid=True, style={"max-width": "1400px"})
