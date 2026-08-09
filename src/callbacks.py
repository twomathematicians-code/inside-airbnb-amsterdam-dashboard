# callbacks.py
"""
Reactive event binding — all Dash callbacks registered here.
Single register_callbacks(app) entry point for app.py.
"""

from dash.dependencies import Input, Output, State
from dash import html
import charts
from datetime import datetime


def register_callbacks(app):
    """Wire all Input/Output bindings to the Dash app instance."""

    # ═══════════════════════════════════════════════════
    #  TAB 1 — MARKET OVERVIEW
    # ═══════════════════════════════════════════════════

    @app.callback(
        Output('ex1A-basic-chart-price-dist', 'figure'),
        Input('price-range-slider', 'value')
    )
    def update_price_histogram(price_range):
        return charts.get_price_distribution_chart(price_range)

    @app.callback(
        Output('ex1B-basic-chart-room-type', 'figure'),
        Input('master-filter-neighbourhood', 'value')
    )
    def update_room_type_pie(selected_neighbourhood):
        return charts.get_room_type_pie_chart(selected_neighbourhood)

    @app.callback(
        Output('ex3-map-visualization', 'figure'),
        Input('master-filter-neighbourhood', 'value')
    )
    def update_map(selected_neighbourhood):
        return charts.get_map(selected_neighbourhood)

    # ═══════════════════════════════════════════════════
    #  TAB 2 — BUSINESS INTELLIGENCE
    # ═══════════════════════════════════════════════════

    @app.callback(
        Output('bi-occupancy-chart', 'figure'),
        Input('bi-neighbourhood-filter', 'value')
    )
    def update_occupancy(selected_neighbourhood):
        return charts.get_occupancy_chart(selected_neighbourhood)

    @app.callback(
        Output('bi-revenue-box', 'figure'),
        Input('bi-neighbourhood-filter', 'value')
    )
    def update_revenue_box(selected_neighbourhood):
        return charts.get_revenue_boxplot(selected_neighbourhood)

    @app.callback(
        Output('bi-host-concentration', 'figure'),
        Input('bi-neighbourhood-filter', 'value')
    )
    def update_host_concentration(selected_neighbourhood):
        return charts.get_host_concentration_chart(selected_neighbourhood)

    @app.callback(
        Output('bi-revenue-treemap', 'figure'),
        Input('bi-neighbourhood-filter', 'value')
    )
    def update_revenue_treemap(selected_neighbourhood):
        return charts.get_revenue_treemap(selected_neighbourhood)

    # Static BI charts (no filter dependency)
    @app.callback(
        Output('bi-demand-supply', 'figure'),
        Input('bi-neighbourhood-filter', 'value')  # Dummy input for refresh
    )
    def update_demand_supply(_):
        return charts.get_demand_supply_chart()

    @app.callback(
        Output('bi-pricing-position', 'figure'),
        Input('bi-neighbourhood-filter', 'value')  # Dummy input for refresh
    )
    def update_pricing_position(_):
        return charts.get_pricing_position_chart()

    @app.callback(
        Output('bi-rating-price', 'figure'),
        Input('bi-neighbourhood-filter', 'value')  # Dummy input for refresh
    )
    def update_rating_price(_):
        return charts.get_rating_price_matrix()

    # ═══════════════════════════════════════════════════
    #  TAB 3 — POLICY & COMPLIANCE
    # ═══════════════════════════════════════════════════

    @app.callback(
        Output('policy-min-nights', 'figure'),
        Input('policy-neighbourhood-filter', 'value')
    )
    def update_min_nights(selected_neighbourhood):
        return charts.get_minimum_nights_chart(selected_neighbourhood)

    # Static policy charts
    @app.callback(
        Output('policy-license', 'figure'),
        Input('policy-neighbourhood-filter', 'value')
    )
    def update_license(_):
        return charts.get_license_compliance_chart()

    @app.callback(
        Output('policy-occupancy-timeline', 'figure'),
        Input('policy-neighbourhood-filter', 'value')
    )
    def update_occupancy_timeline(_):
        return charts.get_occupancy_timeline()

    # ═══════════════════════════════════════════════════
    #  LIVE REFRESH
    # ═══════════════════════════════════════════════════

    @app.callback(
        Output('freshness-badge', 'children'),
        Output('kpi-header-row', 'children'),
        Input('live-refresh-interval', 'n_intervals')
    )
    def live_refresh(n):
        """Periodic refresh: update timestamp badge and KPI cards."""
        kpi = charts.get_kpi_metrics()
        now_str = datetime.now().strftime('%H:%M:%S')

        freshness = [
            html.Span("🟢 LIVE ", className="badge bg-success me-2"),
            html.Small(f"Last refreshed: {now_str} | "
                       f"Auto-refresh every 5 min", className="text-muted"),
        ]

        if not kpi:
            return freshness, []

        import dash_bootstrap_components as dbc

        kpi_cards = [
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
        ]

        return freshness, kpi_cards

    pass
