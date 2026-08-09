# callbacks.py
"""
Reactive event binding — all Dash callbacks registered here.
Covers: charts, data explorer, ROI calculator, comparison, download, live refresh.
"""

from dash.dependencies import Input, Output, State
from dash import html, dash_table, dcc
import dash_bootstrap_components as dbc
import charts
from datetime import datetime
import pandas as pd
import io
import base64


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

    @app.callback(
        Output('bi-demand-supply', 'figure'),
        Input('bi-neighbourhood-filter', 'value')
    )
    def update_demand_supply(_):
        return charts.get_demand_supply_chart()

    @app.callback(
        Output('bi-pricing-position', 'figure'),
        Input('bi-neighbourhood-filter', 'value')
    )
    def update_pricing_position(_):
        return charts.get_pricing_position_chart()

    @app.callback(
        Output('bi-rating-price', 'figure'),
        Input('bi-neighbourhood-filter', 'value')
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
    #  TAB 5 — DATA EXPLORER
    # ═══════════════════════════════════════════════════

    @app.callback(
        Output('explorer-table-container', 'children'),
        Output('explorer-row-count', 'children'),
        Input('explorer-search', 'value'),
        Input('explorer-neighbourhood', 'value'),
        Input('explorer-room-type', 'value'),
        Input('explorer-price-range', 'value'),
    )
    def update_data_table(search, neighbourhood, room_type, price_range):
        min_p, max_p = price_range if price_range else (0, 9999)
        df = charts.get_export_dataframe(
            selected_neighbourhood=neighbourhood,
            room_type_filter=room_type,
            min_price=min_p,
            max_price=max_p,
            search_term=search,
        )
        if df.empty:
            return html.P("No listings match your filters.", className="text-muted"), ""

        row_count = f"Showing {len(df):,} of {len(charts.LISTINGS_DF):,} listings"

        # Format columns
        display_df = df.copy()
        for col in ['price', 'est_annual_revenue']:
            if col in display_df.columns:
                display_df[col] = display_df[col].apply(lambda x: f"€{x:,.0f}" if pd.notna(x) else "")
        if 'occupancy_pct' in display_df.columns:
            display_df['occupancy_pct'] = display_df['occupancy_pct'].apply(
                lambda x: f"{x:.0f}%" if pd.notna(x) else "")
        if 'reviews_per_month' in display_df.columns:
            display_df['reviews_per_month'] = display_df['reviews_per_month'].apply(
                lambda x: f"{x:.1f}" if pd.notna(x) else "")

        table = dash_table.DataTable(
            data=display_df.to_dict('records'),
            columns=[{"name": c.replace('_', ' ').title(), "id": c} for c in display_df.columns],
            page_size=25,
            sort_action="native",
            filter_action="native",
            style_table={'minWidth': '100%'},
            style_cell={
                'textAlign': 'left', 'padding': '6px 10px',
                'fontSize': '12px', 'fontFamily': 'sans-serif',
                'whiteSpace': 'normal', 'height': 'auto',
            },
            style_header={
                'backgroundColor': 'rgb(230, 230, 230)',
                'fontWeight': 'bold', 'fontSize': '12px',
            },
            style_data_conditional=[
                {'if': {'row_index': 'odd'}, 'backgroundColor': 'rgb(248, 248, 248)'},
                {'if': {'filter_query': '{license_status} = "Unlicensed"'},
                 'backgroundColor': '#fff3f3', 'color': '#d62728'},
            ],
            tooltip_data=[
                {col: {'value': str(val), 'type': 'markdown'}
                 for col, val in row.items()} for row in df.to_dict('records')
            ],
            tooltip_duration=None,
        )
        return table, html.Small(f"🔍 {row_count}", className="text-muted")

    # ── CSV Download ──────────────────────────────────
    @app.callback(
        Output('download-dataframe-csv', 'data'),
        Input('btn-download-csv', 'n_clicks'),
        State('explorer-neighbourhood', 'value'),
        State('explorer-room-type', 'value'),
        State('explorer-price-range', 'value'),
        State('explorer-search', 'value'),
        prevent_initial_call=True,
    )
    def download_csv(n_clicks, neighbourhood, room_type, price_range, search):
        min_p, max_p = price_range if price_range else (0, 9999)
        df = charts.get_export_dataframe(
            selected_neighbourhood=neighbourhood,
            room_type_filter=room_type,
            min_price=min_p,
            max_price=max_p,
            search_term=search,
        )
        return dcc.send_data_frame(df.to_csv, "airbnb_amsterdam_export.csv", index=False)

    # ═══════════════════════════════════════════════════
    #  TAB 6 — ROI CALCULATOR
    # ═══════════════════════════════════════════════════

    @app.callback(
        Output('roi-results', 'children'),
        Input('roi-price', 'value'),
        Input('roi-occupancy', 'value'),
        Input('roi-num-listings', 'value'),
        Input('roi-room-type', 'value'),
    )
    def update_roi(price, occupancy, num_listings, room_type):
        if None in (price, occupancy, num_listings):
            return html.P("Adjust the sliders to see projections.", className="text-muted")

        r = charts.calculate_roi(price, occupancy, num_listings, room_type)

        arrow_up = "↑" if r['price_vs_market_pct'] > 0 else "↓"
        color = "success" if r['revenue_vs_market_pct'] > 0 else "danger"

        return html.Div([
            dbc.Row([
                dbc.Col(dbc.Card([
                    dbc.CardBody([
                        html.H3(f"€{r['annual_revenue']:,.0f}", className="text-center text-primary mb-0"),
                        html.Small("Projected Annual Revenue", className="text-center d-block text-muted"),
                    ])
                ], color="light"), width=6),
                dbc.Col(dbc.Card([
                    dbc.CardBody([
                        html.H3(f"€{r['monthly_revenue']:,.0f}", className="text-center text-success mb-0"),
                        html.Small("Projected Monthly Revenue", className="text-center d-block text-muted"),
                    ])
                ], color="light"), width=6),
            ], className="mb-3 g-2"),
            dbc.Row([
                dbc.Col(dbc.Card([
                    dbc.CardBody([
                        html.H5(f"{r['booked_days']:.0f} days", className="text-center mb-0"),
                        html.Small("Booked Days / Year", className="text-center d-block text-muted"),
                    ])
                ], color="light"), width=4),
                dbc.Col(dbc.Card([
                    dbc.CardBody([
                        html.H5(f"{arrow_up} {abs(r['price_vs_market_pct']):.0f}%", className="text-center mb-0"),
                        html.Small("vs Market Avg Price", className="text-center d-block text-muted"),
                    ])
                ], color="light"), width=4),
                dbc.Col(dbc.Card([
                    dbc.CardBody([
                        html.H5(f"{abs(r['revenue_vs_market_pct']):.0f}%", className=f"text-center text-{color} mb-0"),
                        html.Small("vs Market Avg Revenue", className="text-center d-block text-muted"),
                    ])
                ], color="light"), width=4),
            ], className="mb-3 g-2"),
            html.Hr(),
            html.Small(f"Market benchmark: {room_type} — Avg price €{r['market_avg_price']:.0f}, "
                       f"Avg occupancy {r['market_avg_occupancy']:.0f}%, "
                       f"Avg annual revenue €{r['market_avg_revenue']:,.0f}",
                       className="text-muted"),
        ])

    # ═══════════════════════════════════════════════════
    #  NEIGHBOURHOOD COMPARISON
    # ═══════════════════════════════════════════════════

    @app.callback(
        Output('comparison-results', 'children'),
        Input('compare-nb1', 'value'),
        Input('compare-nb2', 'value'),
    )
    def update_comparison(nb1, nb2):
        if not nb1 or not nb2:
            return html.P("Select two neighbourhoods to compare.", className="text-muted")

        comp = charts.get_neighbourhood_comparison(nb1, nb2)
        s1, s2 = comp.get('nb1'), comp.get('nb2')

        if s1 is None or s2 is None:
            return html.P("Could not compute comparison.", className="text-danger")

        def make_comparison_row(label, key, fmt=",.0f", prefix="", suffix=""):
            v1 = s1[key]
            v2 = s2[key]
            if isinstance(v1, float):
                v1_str = f"{prefix}{v1:{fmt}}{suffix}"
                v2_str = f"{prefix}{v2:{fmt}}{suffix}"
            else:
                v1_str = str(v1)
                v2_str = str(v2)
            better = ""
            if isinstance(v1, (int, float)) and isinstance(v2, (int, float)):
                if key in ('avg_price', 'avg_min_nights'):
                    better = "🟢" if v1 < v2 else "🔴" if v1 > v2 else ""
                else:
                    better = "🟢" if v1 > v2 else "🔴" if v1 < v2 else ""

            return html.Tr([
                html.Td(label, className="fw-bold"),
                html.Td(f"{v1_str} {better if better and v1 != v2 else ''}"),
                html.Td(f"{v2_str} {better if better and v2 != v1 else ''}"),
            ])

        return dbc.Table([
            html.Thead(html.Tr([
                html.Th("Metric"),
                html.Th(comp['nb1_name']),
                html.Th(comp['nb2_name']),
            ])),
            html.Tbody([
                make_comparison_row("Total Listings", "listings"),
                make_comparison_row("Avg. Price", "avg_price", prefix="€"),
                make_comparison_row("Median Price", "median_price", prefix="€"),
                make_comparison_row("Avg. Occupancy", "avg_occupancy", suffix="%"),
                make_comparison_row("Est. Total Revenue", "est_total_revenue", prefix="€"),
                make_comparison_row("Entire Home Share", "entire_home_pct", suffix="%"),
                make_comparison_row("License Compliance", "licensed_pct", suffix="%"),
                make_comparison_row("Avg. Min Nights", "avg_min_nights"),
                make_comparison_row("Avg. Reviews/Month", "avg_reviews_per_month"),
                make_comparison_row("Top Host Category", "top_host_category", fmt=""),
            ])
        ], bordered=True, hover=True, size="sm", className="mb-0")

    # ═══════════════════════════════════════════════════
    #  LIVE REFRESH — KPI Header
    # ═══════════════════════════════════════════════════

    @app.callback(
        Output('freshness-badge', 'children'),
        Output('kpi-header-row', 'children'),
        Input('live-refresh-interval', 'n_intervals')
    )
    def live_refresh(n):
        kpi = charts.get_kpi_metrics()
        now_str = datetime.now().strftime('%H:%M:%S')

        freshness = [
            html.Span("🟢 LIVE ", className="badge bg-success me-2"),
            html.Small(f"Last refreshed: {now_str} | "
                       f"Auto-refresh every 5 min", className="text-muted"),
        ]

        if not kpi:
            return freshness, []

        kpi_cards = [
            dbc.Col(dbc.Card([dbc.CardBody([
                html.H4(kpi['total_listings'], className="card-title text-center mb-0"),
                html.P("Total Listings", className="text-muted text-center small mb-0")
            ])], color="light", outline=True), width=2),
            dbc.Col(dbc.Card([dbc.CardBody([
                html.H4(kpi['avg_price'], className="card-title text-center mb-0"),
                html.P("Avg. Nightly Price", className="text-muted text-center small mb-0")
            ])], color="light", outline=True), width=2),
            dbc.Col(dbc.Card([dbc.CardBody([
                html.H4(kpi['avg_occupancy'], className="card-title text-center mb-0"),
                html.P("Avg. Occupancy", className="text-muted text-center small mb-0")
            ])], color="light", outline=True), width=2),
            dbc.Col(dbc.Card([dbc.CardBody([
                html.H4(kpi['total_est_revenue'], className="card-title text-center mb-0"),
                html.P("Est. Annual Revenue", className="text-muted text-center small mb-0")
            ])], color="light", outline=True), width=2),
            dbc.Col(dbc.Card([dbc.CardBody([
                html.H4(kpi['entire_home_pct'], className="card-title text-center mb-0"),
                html.P("Entire Home Share", className="text-muted text-center small mb-0")
            ])], color="warning", outline=True), width=2),
            dbc.Col(dbc.Card([dbc.CardBody([
                html.H4(kpi['licensed_pct'], className="card-title text-center mb-0"),
                html.P("License Compliance", className="text-muted text-center small mb-0")
            ])], color="success" if float(kpi['licensed_pct'].replace('%', '')) > 50 else "danger",
               outline=True), width=2),
        ]

        return freshness, kpi_cards

    pass
