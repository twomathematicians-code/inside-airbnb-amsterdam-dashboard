# layout.py
"""
Industrial-grade dashboard DOM with dark sidebar navigation.
Design System: Dark theme, glass cards, 6-KPI grid, alert panels.
"""

from dash import dcc, html, dash_table
import dash_bootstrap_components as dbc
import charts
from datetime import datetime


# ═══════════════════════════════════════════════════════
#  DESIGN SYSTEM COMPONENTS
# ═══════════════════════════════════════════════════════

def kpi_card(value, label, variant="info"):
    return html.Div([
        html.Div(value, className="kpi-value"),
        html.Div(label, className="kpi-label"),
    ], className=f"kpi-card {variant}")


def content_card(title, children, badge=None, badge_class="badge-live"):
    header = html.Div([
        html.H3(title),
        html.Span(badge, className=f"badge {badge_class}") if badge else None,
    ], className="content-card-header")
    return html.Div([header, children], className="content-card")


def filter_dropdown(id, label, options, value='All', width="200px"):
    return html.Div([
        html.Label(label, className="filter-group-label"),
        dcc.Dropdown(id=id, options=options, value=value, clearable=False,
                     style={"minWidth": width}),
    ], className="filter-group")


def neighbourhood_filter(id, label="Neighbourhood"):
    listings = charts.LISTINGS_DF
    opts = [{'label': 'All Neighbourhoods', 'value': 'All'}]
    if not listings.empty:
        opts.extend([{'label': n, 'value': n} for n in sorted(listings['neighbourhood'].unique())])
    return filter_dropdown(id, label, opts)


# ═══════════════════════════════════════════════════════
#  SIDEBAR NAVIGATION
# ═══════════════════════════════════════════════════════

def sidebar():
    nav_items = [
        ("🏢", "Executive View", "page-exec"),
        ("📍", "Market Overview", "page-market"),
        ("💰", "Revenue Optimization", "page-revenue"),
        ("🌱", "Host Growth", "page-hosts"),
        ("🛡️", "Trust & Safety", "page-trust"),
        ("📋", "Policy & Compliance", "page-policy"),
        ("💼", "Business Intelligence", "page-bi"),
        ("🧠", "Strategic Intel", "page-strategic"),
        ("🔍", "Data Explorer", "page-explorer"),
        ("🧮", "ROI Calculator", "page-roi"),
        ("ℹ️", "About", "page-about"),
    ]

    return html.Div([
        html.Div([
            html.H2("Airbnb Intel"),
            html.Span("Amsterdam · NL"),
        ], className="sidebar-brand"),

        html.Div([
            html.Button(
                [html.Span(icon, className="nav-icon"), html.Span(label)],
                id=f"nav-{page_id}", className="nav-item active" if page_id == "page-exec" else "nav-item",
            )
            for icon, label, page_id in nav_items
        ], className="sidebar-nav", id="sidebar-nav-container"),

        html.Div([
            html.Div([html.Div(className="live-dot"), "System Live"], className="live-indicator"),
            html.Div(id="sidebar-refresh-time", children=f"Updated: {datetime.now().strftime('%H:%M')}"),
            html.Div("v5.1 · MIT License", style={"marginTop": "4px"}),
        ], className="sidebar-footer"),
    ], className="sidebar")


# ═══════════════════════════════════════════════════════
#  KPI HEADER
# ═══════════════════════════════════════════════════════

def kpi_header():
    kpi = charts.get_kpi_metrics()
    if not kpi: return html.Div()
    license_val = float(kpi['licensed_pct'].replace('%', ''))
    entire_val = float(kpi['entire_home_pct'].replace('%', ''))

    return html.Div([
        kpi_card(kpi['total_listings'], "Total Listings", "info"),
        kpi_card(kpi['avg_price'], "Avg Nightly Price", "info"),
        kpi_card(kpi['avg_occupancy'], "Avg Occupancy", "info"),
        kpi_card(kpi['total_est_revenue'], "Est Annual Revenue", "info"),
        kpi_card(kpi['entire_home_pct'], "Entire Home Share", "warning" if entire_val > 60 else "info"),
        kpi_card(kpi['licensed_pct'], "License Compliance", "success" if license_val > 50 else "danger"),
    ], className="kpi-grid", id="kpi-header-row")


# ═══════════════════════════════════════════════════════
#  PAGE: Market Overview
# ═══════════════════════════════════════════════════════

def page_market_overview():
    return html.Div([
        html.Div([
            html.H1("Market Overview", className="top-bar-title"),
            html.Div([
                html.Span("🟢 Live", className="badge badge-live"),
            ], className="top-bar-actions"),
        ], className="top-bar"),

        kpi_header(),

        content_card("Neighbourhood Filter", neighbourhood_filter("master-filter-neighbourhood")),

        html.Div([
            html.Div([
                html.Label("Price Range (€):", style={"fontSize": "11px", "fontWeight": "600",
                           "color": "var(--text-muted)", "textTransform": "uppercase", "letterSpacing": "0.5px"}),
                dcc.RangeSlider(id='price-range-slider', min=0, max=500, step=10, value=[0, 250],
                                marks={i: f'€{i}' for i in range(0, 501, 100)},
                                tooltip={"placement": "bottom", "always_visible": True}),
            ], style={"marginBottom": "20px"}),
        ]),

        html.Div([
            html.Div(charts.get_basic_chart_A(), style={"flex": "1", "minWidth": "400px"}),
            html.Div(charts.get_basic_chart_B(), style={"flex": "1", "minWidth": "350px"}),
        ], style={"display": "flex", "gap": "16px", "flexWrap": "wrap", "marginBottom": "16px"}),

        content_card("Spatial Intelligence", charts.get_map_component()),
    ], id="page-market")


# ═══════════════════════════════════════════════════════
#  PAGE: Business Intelligence
# ═══════════════════════════════════════════════════════

def page_business_intelligence():
    return html.Div([
        html.Div([
            html.H1("Business Intelligence", className="top-bar-title"),
        ], className="top-bar"),

        kpi_header(),
        content_card("Filter", neighbourhood_filter("bi-neighbourhood-filter")),

        html.Div([
            html.Div(charts.get_occupancy_component(), style={"flex": "1", "minWidth": "400px"}),
            html.Div(charts.get_revenue_box_component(), style={"flex": "1", "minWidth": "400px"}),
        ], style={"display": "flex", "gap": "16px", "flexWrap": "wrap", "marginBottom": "16px"}),

        html.Div([
            html.Div(charts.get_demand_supply_component(), style={"flex": "1", "minWidth": "400px"}),
            html.Div(charts.get_host_concentration_component(), style={"flex": "1", "minWidth": "350px"}),
        ], style={"display": "flex", "gap": "16px", "flexWrap": "wrap", "marginBottom": "16px"}),

        html.Div([
            html.Div(charts.get_pricing_position_component(), style={"flex": "1", "minWidth": "400px"}),
            html.Div(charts.get_rating_price_component(), style={"flex": "1", "minWidth": "400px"}),
        ], style={"display": "flex", "gap": "16px", "flexWrap": "wrap", "marginBottom": "16px"}),

        content_card("Revenue Breakdown", charts.get_revenue_treemap_component()),
    ], id="page-bi")


# ═══════════════════════════════════════════════════════
#  PAGE: Policy & Compliance
# ═══════════════════════════════════════════════════════

def page_policy():
    return html.Div([
        html.Div([html.H1("Policy & Compliance", className="top-bar-title")], className="top-bar"),
        kpi_header(),
        content_card("Filter", neighbourhood_filter("policy-neighbourhood-filter")),

        html.Div([
            html.Div(charts.get_occupancy_timeline_component(), style={"flex": "1", "minWidth": "400px"}),
            html.Div(charts.get_min_nights_component(), style={"flex": "1", "minWidth": "400px"}),
        ], style={"display": "flex", "gap": "16px", "flexWrap": "wrap", "marginBottom": "16px"}),

        content_card("License Compliance", charts.get_license_compliance_component()),

        content_card("📌 Policy Recommendations", html.Ul([
            html.Li("Mandatory licensing with visible registry IDs — enforcement correlates with compliance."),
            html.Li("Cap entire-home listings in zones >60% entire-home share."),
            html.Li("Progressive minimum-night thresholds (3+ nights) in historic center."),
            html.Li("Dynamic pricing transparency — total cost including fees upfront."),
            html.Li("Incentivize private-room hosting over entire-home conversions."),
        ], style={"color": "var(--text-secondary)", "fontSize": "13px", "lineHeight": "1.8", "paddingLeft": "20px"})),
    ], id="page-policy")


# ═══════════════════════════════════════════════════════
#  PAGE: Data Explorer
# ═══════════════════════════════════════════════════════

def page_data_explorer():
    listings = charts.LISTINGS_DF
    neighbourhoods = sorted(listings['neighbourhood'].unique()) if not listings.empty else []
    room_types = sorted(listings['room_type'].unique()) if not listings.empty else []

    return html.Div([
        html.Div([html.H1("Data Explorer", className="top-bar-title")], className="top-bar"),

        html.Div([
            html.Div([
                html.Label("SEARCH", style={"fontSize": "11px", "fontWeight": "600", "color": "var(--text-muted)",
                           "textTransform": "uppercase", "letterSpacing": "0.5px"}),
                dbc.Input(id="explorer-search", type="text", placeholder="Host or listing name...", debounce=True,
                         style={"background": "var(--bg-card)", "border": "1px solid var(--border-medium)",
                                "color": "var(--text-primary)", "borderRadius": "8px", "padding": "8px 12px"}),
            ], className="filter-group"),
            filter_dropdown("explorer-neighbourhood", "NEIGHBOURHOOD",
                          [{'label': 'All', 'value': 'All'}] + [{'label': n, 'value': n} for n in neighbourhoods]),
            filter_dropdown("explorer-room-type", "ROOM TYPE",
                          [{'label': 'All', 'value': 'All'}] + [{'label': r, 'value': r} for r in room_types]),
            html.Div([
                html.Label("PRICE RANGE (€)", style={"fontSize": "11px", "fontWeight": "600", "color": "var(--text-muted)",
                           "textTransform": "uppercase", "letterSpacing": "0.5px"}),
                dcc.RangeSlider(id="explorer-price-range", min=0, max=500, step=10, value=[0, 500],
                               marks={i: f'€{i}' for i in range(0, 501, 100)},
                               tooltip={"placement": "bottom", "always_visible": True}),
            ], style={"minWidth": "250px", "flex": "1"}),
            html.Div([
                html.Label("EXPORT", style={"fontSize": "11px", "fontWeight": "600", "color": "var(--text-muted)",
                           "textTransform": "uppercase", "letterSpacing": "0.5px"}),
                html.Button("⬇ Download CSV", id="btn-download-csv", className="btn-primary"),
                dcc.Download(id="download-dataframe-csv"),
            ], className="filter-group"),
        ], className="filter-bar"),

        html.Div(id="explorer-row-count", style={"fontSize": "12px", "color": "var(--text-muted)", "marginBottom": "8px"}),
        html.Div(id="explorer-table-container", style={"maxHeight": "550px", "overflowY": "auto"}),
    ], id="page-explorer")


# ═══════════════════════════════════════════════════════
#  PAGE: ROI Calculator + Comparison
# ═══════════════════════════════════════════════════════

def page_roi_calculator():
    listings = charts.LISTINGS_DF
    neighbourhoods = sorted(listings['neighbourhood'].unique()) if not listings.empty else []
    room_types = sorted(listings['room_type'].unique()) if not listings.empty else []

    return html.Div([
        html.Div([html.H1("ROI Calculator", className="top-bar-title")], className="top-bar"),

        html.Div([
            html.Div([
                content_card("📊 Revenue Projection", html.Div([
                    html.Div([
                        filter_dropdown("roi-room-type", "ROOM TYPE",
                                      [{'label': r, 'value': r} for r in room_types],
                                      value=room_types[0] if room_types else None),
                        html.Div([
                            html.Label("LISTINGS", style={"fontSize": "11px", "fontWeight": "600",
                                       "color": "var(--text-muted)", "textTransform": "uppercase"}),
                            dbc.Input(id="roi-num-listings", type="number", value=1, min=1, max=100, step=1,
                                     style={"background": "var(--bg-card)", "border": "1px solid var(--border-medium)",
                                            "color": "var(--text-primary)", "borderRadius": "8px", "padding": "8px"}),
                        ], className="filter-group"),
                    ], style={"display": "flex", "gap": "12px", "marginBottom": "16px"}),
                    html.Label("Nightly Price (€):", style={"fontSize": "11px", "fontWeight": "600",
                               "color": "var(--text-muted)", "textTransform": "uppercase"}),
                    dcc.Slider(id="roi-price", min=20, max=500, step=5, value=150,
                              marks={i: f'€{i}' for i in range(0, 501, 100)},
                              tooltip={"placement": "bottom", "always_visible": True}),
                    html.Div(style={"height": "12px"}),
                    html.Label("Expected Occupancy (%):", style={"fontSize": "11px", "fontWeight": "600",
                               "color": "var(--text-muted)", "textTransform": "uppercase"}),
                    dcc.Slider(id="roi-occupancy", min=10, max=100, step=5, value=70,
                              marks={i: f'{i}%' for i in range(0, 101, 20)},
                              tooltip={"placement": "bottom", "always_visible": True}),
                    html.Hr(style={"borderColor": "var(--border-subtle)", "marginTop": "16px"}),
                    html.Div(id="roi-results"),
                ])),
            ], style={"flex": "1", "minWidth": "380px"}),

            html.Div([
                content_card("⚖️ Neighbourhood Comparison", html.Div([
                    html.Div([
                        filter_dropdown("compare-nb1", "AREA A",
                                      [{'label': n, 'value': n} for n in neighbourhoods],
                                      value=neighbourhoods[0] if neighbourhoods else None),
                        filter_dropdown("compare-nb2", "AREA B",
                                      [{'label': n, 'value': n} for n in neighbourhoods],
                                      value=neighbourhoods[1] if len(neighbourhoods) > 1 else None),
                    ], style={"display": "flex", "gap": "12px", "marginBottom": "16px"}),
                    html.Div(id="comparison-results"),
                ])),
            ], style={"flex": "1.5", "minWidth": "450px"}),
        ], style={"display": "flex", "gap": "16px", "flexWrap": "wrap"}),
    ], id="page-roi")


# ═══════════════════════════════════════════════════════
#  PAGE: Strategic Intelligence
# ═══════════════════════════════════════════════════════

def page_strategic_intelligence():
    return html.Div([
        html.Div([
            html.H1("Strategic Intelligence", className="top-bar-title"),
            html.Span("⚠️ Live Monitoring", className="badge badge-warning"),
        ], className="top-bar"),

        content_card("🚨 Early Warning System", html.Div(id="strat-early-warnings"),
                    badge="AUTO", badge_class="badge-live"),

        html.Div([
            html.Div(charts.get_risk_opportunity_component(), style={"flex": "1.4", "minWidth": "500px"}),
            html.Div(charts.get_price_volatility_component(), style={"flex": "1", "minWidth": "350px"}),
        ], style={"display": "flex", "gap": "16px", "flexWrap": "wrap", "marginBottom": "16px"}),

        html.Div([
            html.Div(charts.get_market_concentration_component(), style={"flex": "1", "minWidth": "400px"}),
            html.Div(charts.get_stakeholder_network_component(), style={"flex": "1", "minWidth": "400px"}),
        ], style={"display": "flex", "gap": "16px", "flexWrap": "wrap", "marginBottom": "16px"}),

        html.Div([
            html.Div(charts.get_professionalization_component(), style={"flex": "1", "minWidth": "400px"}),
            html.Div(content_card("🤖 Automated Market Briefing",
                                  dcc.Markdown(id="strat-briefing", children=charts.generate_market_briefing(),
                                               className="briefing-text"),
                                  badge="AI", badge_class="badge-info"),
                     style={"flex": "1", "minWidth": "400px"}),
        ], style={"display": "flex", "gap": "16px", "flexWrap": "wrap", "marginBottom": "16px"}),
    ], id="page-strategic")


# ═══════════════════════════════════════════════════════
#  PAGE: Executive Dashboard
# ═══════════════════════════════════════════════════════

def page_executive():
    swot = charts.get_swot_analysis()
    return html.Div([
        html.Div([html.H1("Executive Dashboard", className="top-bar-title"),
                  html.Span("👑 C-Suite", className="badge badge-info")], className="top-bar"),
        kpi_header(),

        # SWOT Matrix
        html.Div([
            html.Div(content_card("💪 Strengths", html.Ul([
                html.Li(s) for s in swot.get('strengths', [])
            ], style={"color": "var(--accent-green)", "fontSize": "13px", "lineHeight": "1.6", "paddingLeft": "18px"})),
                     style={"flex": "1"}),
            html.Div(content_card("⚠️ Weaknesses", html.Ul([
                html.Li(w) for w in swot.get('weaknesses', [])
            ], style={"color": "var(--accent-red)", "fontSize": "13px", "lineHeight": "1.6", "paddingLeft": "18px"})),
                     style={"flex": "1"}),
        ], style={"display": "flex", "gap": "16px", "flexWrap": "wrap", "marginBottom": "16px"}),

        html.Div([
            html.Div(content_card("🚀 Opportunities", html.Ul([
                html.Li(o) for o in swot.get('opportunities', [])
            ], style={"color": "var(--accent-blue)", "fontSize": "13px", "lineHeight": "1.6", "paddingLeft": "18px"})),
                     style={"flex": "1"}),
            html.Div(content_card("🔴 Threats", html.Ul([
                html.Li(t) for t in swot.get('threats', [])
            ], style={"color": "var(--accent-amber)", "fontSize": "13px", "lineHeight": "1.6", "paddingLeft": "18px"})),
                     style={"flex": "1"}),
        ], style={"display": "flex", "gap": "16px", "flexWrap": "wrap", "marginBottom": "16px"}),

        # SWOT Metrics
        html.Div([
            html.Div([html.Div(swot.get('metrics', {}).get('avg_occ', '-'), className="kpi-value"),
                      html.Div("Occupancy", className="kpi-label")], className="kpi-card info"),
            html.Div([html.Div(swot.get('metrics', {}).get('avg_rev', '-'), className="kpi-value"),
                      html.Div("Avg Revenue", className="kpi-label")], className="kpi-card info"),
            html.Div([html.Div(swot.get('metrics', {}).get('entire_pct', '-'), className="kpi-value"),
                      html.Div("Entire Home", className="kpi-label")], className="kpi-card warning"),
            html.Div([html.Div(swot.get('metrics', {}).get('licensed_pct', '-'), className="kpi-value"),
                      html.Div("Compliance", className="kpi-label")], className="kpi-card danger"),
            html.Div([html.Div(swot.get('metrics', {}).get('risk_areas', '-'), className="kpi-value"),
                      html.Div("Risk Areas", className="kpi-label")], className="kpi-card danger"),
            html.Div([html.Div(swot.get('metrics', {}).get('opp_areas', '-'), className="kpi-value"),
                      html.Div("Oppty Areas", className="kpi-label")], className="kpi-card success"),
        ], className="kpi-grid"),

        html.Div([
            html.Div(charts.get_revenue_waterfall_component(), style={"flex": "1", "minWidth": "400px"}),
            html.Div(charts.get_market_coverage_component(), style={"flex": "1", "minWidth": "350px"}),
        ], style={"display": "flex", "gap": "16px", "flexWrap": "wrap", "marginBottom": "16px"}),
    ], id="page-exec")


# ═══════════════════════════════════════════════════════
#  PAGE: Revenue Optimization
# ═══════════════════════════════════════════════════════

def page_revenue():
    return html.Div([
        html.Div([html.H1("Revenue Optimization", className="top-bar-title"),
                  html.Span("💰 Revenue Team", className="badge badge-live")], className="top-bar"),
        kpi_header(),

        html.Div([
            html.Div(charts.get_revenue_leakage_component(), style={"flex": "1", "minWidth": "450px"}),
            html.Div(charts.get_pricing_optimization_component(), style={"flex": "1", "minWidth": "400px"}),
        ], style={"display": "flex", "gap": "16px", "flexWrap": "wrap", "marginBottom": "16px"}),

        content_card("Revenue Optimization Actions", html.Ul([
            html.Li("Correct underpricing in top leakage areas — estimated millions in recoverable revenue"),
            html.Li("Align pricing to IQR ranges — price within 25th-75th percentile for each room type"),
            html.Li("Monitor occupancy daily — price drops of 5-10% in areas below 50% occupancy"),
            html.Li("Seasonal surge pricing: increase 15-25% during peak events (King's Day, IBC, ADE)"),
            html.Li("Minimum stay adjustments: 3+ nights during events to capture premium bookings"),
        ], style={"color": "var(--text-secondary)", "fontSize": "13px", "lineHeight": "1.8", "paddingLeft": "20px"})),
    ], id="page-revenue")


# ═══════════════════════════════════════════════════════
#  PAGE: Host Growth
# ═══════════════════════════════════════════════════════

def page_host_growth():
    return html.Div([
        html.Div([html.H1("Host Growth", className="top-bar-title"),
                  html.Span("🌱 Acquisition Team", className="badge badge-live")], className="top-bar"),
        kpi_header(),

        html.Div([
            html.Div(charts.get_host_acquisition_component(), style={"flex": "1", "minWidth": "400px"}),
            html.Div(charts.get_host_quality_component(), style={"flex": "1", "minWidth": "400px"}),
        ], style={"display": "flex", "gap": "16px", "flexWrap": "wrap", "marginBottom": "16px"}),

        content_card("Host Growth Strategy", html.Ul([
            html.Li("Priority acquisition: target top-5 neighbourhoods with high demand, low supply"),
            html.Li("Nurture 'Rising (2-5 reviews)' hosts — highest occupancy correlation with review growth"),
            html.Li("Superhost pipeline: identify hosts with 40+ reviews and 80%+ occupancy for fast-track"),
            html.Li("Onboarding incentive: offer reduced fees for first 3 months in high-demand underserved areas"),
            html.Li("Retention risk: monitor hosts with declining review velocity — early intervention trigger"),
        ], style={"color": "var(--text-secondary)", "fontSize": "13px", "lineHeight": "1.8", "paddingLeft": "20px"})),
    ], id="page-hosts")


# ═══════════════════════════════════════════════════════
#  PAGE: Trust & Safety
# ═══════════════════════════════════════════════════════

def page_trust_safety():
    return html.Div([
        html.Div([html.H1("Trust & Safety", className="top-bar-title"),
                  html.Span("🛡️ Compliance Team", className="badge badge-warning")], className="top-bar"),
        kpi_header(),

        html.Div([
            html.Div(charts.get_trust_risk_component(), style={"flex": "1", "minWidth": "450px"}),
            html.Div(charts.get_guest_experience_component(), style={"flex": "1", "minWidth": "400px"}),
        ], style={"display": "flex", "gap": "16px", "flexWrap": "wrap", "marginBottom": "16px"}),

        content_card("Trust & Safety Actions", html.Ul([
            html.Li("High-risk zones: neighbourhoods with <50% compliance + low review activity — priority audit"),
            html.Li("Guest experience: 1-night minimums correlate with high review velocity — promote flexibility"),
            html.Li("License verification: implement automated license validation for all new listings"),
            html.Li("Fraud indicators: flag listings with 0 reviews + low occupancy + high price volatility"),
            html.Li("Transparency: require government ID verification for hosts with 6+ listings"),
        ], style={"color": "var(--text-secondary)", "fontSize": "13px", "lineHeight": "1.8", "paddingLeft": "20px"})),
    ], id="page-trust")


# ═══════════════════════════════════════════════════════
#  PAGE: About
# ═══════════════════════════════════════════════════════

def page_about():
    return html.Div([
        html.Div([html.H1("About", className="top-bar-title")], className="top-bar"),

        html.Div([
            html.Div(content_card("Data Sources", dcc.Markdown("""
- **Inside Airbnb** — [insideairbnb.com](http://insideairbnb.com/get-the-data.html)
- **Amsterdam** listings snapshot (June 2026) — 16,770 listings, 22 neighbourhoods
- Data licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
- Independent analysis — not affiliated with Airbnb Inc.
""", style={"color": "var(--text-secondary)", "fontSize": "13px", "lineHeight": "1.7"})),
                     style={"flex": "1"}),

            html.Div(content_card("Methodology", dcc.Markdown("""
- **Occupancy** = `(365 - availability_365) / 365`
- **Revenue** = `price × booked_days`
- **Risk Score** = composite of entire-home%, compliance gaps, professionalization, price volatility, min-nights
- **Opportunity Score** = occupancy + demand velocity + revenue + market size + compliance
- **HHI** = Herfindahl-Hirschman Index for revenue concentration
- **Early Warnings** = Z-score anomaly detection (σ > 1.5)
""", style={"color": "var(--text-secondary)", "fontSize": "13px", "lineHeight": "1.7"})),
                     style={"flex": "1"}),
        ], style={"display": "flex", "gap": "16px", "flexWrap": "wrap", "marginBottom": "16px"}),

        content_card("Stakeholder Use Cases", dcc.Markdown("""
| Stakeholder | Use Case |
|---|---|
| **Property Owners / Hosts** | Competitive pricing, occupancy benchmarking, revenue optimization |
| **Real Estate Investors** | Neighbourhood ROI analysis, risk-opportunity scoring, concentration analysis |
| **Tourism Boards** | Visitor distribution, capacity planning, demand hotspot identification |
| **City Regulators** | Housing displacement quantification, compliance monitoring, policy impact assessment |
| **Policy Analysts** | Market structure analysis, stakeholder influence mapping, automated briefings |
""", style={"color": "var(--text-secondary)", "fontSize": "13px"})),

        html.Footer(html.Small("Data from Inside Airbnb (CC BY 4.0). Independent analysis.",
                              style={"color": "var(--text-muted)"}),
                   style={"textAlign": "center", "marginTop": "32px", "paddingTop": "16px",
                          "borderTop": "1px solid var(--border-subtle)"}),
    ], id="page-about")


# ═══════════════════════════════════════════════════════
#  APP SHELL
# ═══════════════════════════════════════════════════════

def get_app_layout():
    return html.Div([
        dcc.Interval(id='live-refresh-interval', interval=5 * 60 * 1000, n_intervals=0),
        dcc.Store(id='active-page', data='page-exec'),
        dcc.Store(id='refresh-data', data={'ts': datetime.now().isoformat()}),
        html.Div(id="toast-container", className="toast-container"),

        html.Div([
            sidebar(),
            html.Div([
                html.Div(page_executive(), id="page-exec", style={"display": "block"}),
                html.Div(page_market_overview(), id="page-market", style={"display": "none"}),
                html.Div(page_revenue(), id="page-revenue", style={"display": "none"}),
                html.Div(page_host_growth(), id="page-hosts", style={"display": "none"}),
                html.Div(page_trust_safety(), id="page-trust", style={"display": "none"}),
                html.Div(page_policy(), id="page-policy", style={"display": "none"}),
                html.Div(page_business_intelligence(), id="page-bi", style={"display": "none"}),
                html.Div(page_strategic_intelligence(), id="page-strategic", style={"display": "none"}),
                html.Div(page_data_explorer(), id="page-explorer", style={"display": "none"}),
                html.Div(page_roi_calculator(), id="page-roi", style={"display": "none"}),
                html.Div(page_about(), id="page-about", style={"display": "none"}),
            ], className="main-content"),
        ], className="app-shell"),
    ])
