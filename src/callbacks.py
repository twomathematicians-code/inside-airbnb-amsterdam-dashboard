# callbacks.py
"""
Reactive event binding — sidebar nav, charts, data explorer, ROI, comparison,
early warnings, briefing, live refresh, toast notifications.
"""

from dash.dependencies import Input, Output, State, ALL
from dash import html, dash_table, dcc
import dash_bootstrap_components as dbc
import charts
from datetime import datetime
import pandas as pd


def register_callbacks(app):

    # ═══════════════════════════════════════════════════
    #  SIDEBAR NAVIGATION — Page Switching (11 pages)
    # ═══════════════════════════════════════════════════

    ALL_PAGES = ["exec", "market", "revenue", "hosts", "trust", "policy", "bi", "strategic", "explorer", "roi", "about"]

    @app.callback(
        [Output(f"page-{pid}", "style") for pid in ALL_PAGES] +
        [Output(f"nav-page-{pid}", "className") for pid in ALL_PAGES],
        [Input(f"nav-page-{pid}", "n_clicks") for pid in ALL_PAGES],
    )
    def switch_page(*args):
        ctx = dcc.callback_context
        if not ctx.triggered:
            styles = [{"display": "block"}] + [{"display": "none"}] * (len(ALL_PAGES) - 1)
            navs = ["nav-item active"] + ["nav-item"] * (len(ALL_PAGES) - 1)
            return styles + navs

        triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
        idx = 0
        for i, pid in enumerate(ALL_PAGES):
            if f'nav-page-{pid}' == triggered_id:
                idx = i
                break

        styles = [{"display": "block"} if i == idx else {"display": "none"} for i in range(len(ALL_PAGES))]
        navs = ["nav-item active" if i == idx else "nav-item" for i in range(len(ALL_PAGES))]
        return styles + navs

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
    def update_room_type_pie(nb):
        return charts.get_room_type_pie_chart(nb)

    @app.callback(
        Output('ex3-map-visualization', 'figure'),
        Input('master-filter-neighbourhood', 'value')
    )
    def update_map(nb):
        return charts.get_map(nb)

    # ═══════════════════════════════════════════════════
    #  TAB 2 — BUSINESS INTELLIGENCE
    # ═══════════════════════════════════════════════════

    @app.callback(Output('bi-occupancy-chart', 'figure'), Input('bi-neighbourhood-filter', 'value'))
    def update_occupancy(nb): return charts.get_occupancy_chart(nb)

    @app.callback(Output('bi-revenue-box', 'figure'), Input('bi-neighbourhood-filter', 'value'))
    def update_revenue_box(nb): return charts.get_revenue_boxplot(nb)

    @app.callback(Output('bi-host-concentration', 'figure'), Input('bi-neighbourhood-filter', 'value'))
    def update_host_conc(nb): return charts.get_host_concentration_chart(nb)

    @app.callback(Output('bi-revenue-treemap', 'figure'), Input('bi-neighbourhood-filter', 'value'))
    def update_treemap(nb): return charts.get_revenue_treemap(nb)

    @app.callback(Output('bi-demand-supply', 'figure'), Input('bi-neighbourhood-filter', 'value'))
    def update_demand(_): return charts.get_demand_supply_chart()

    @app.callback(Output('bi-pricing-position', 'figure'), Input('bi-neighbourhood-filter', 'value'))
    def update_pricing(_): return charts.get_pricing_position_chart()

    @app.callback(Output('bi-rating-price', 'figure'), Input('bi-neighbourhood-filter', 'value'))
    def update_value(_): return charts.get_rating_price_matrix()

    # ═══════════════════════════════════════════════════
    #  TAB 3 — POLICY & COMPLIANCE
    # ═══════════════════════════════════════════════════

    @app.callback(Output('policy-min-nights', 'figure'), Input('policy-neighbourhood-filter', 'value'))
    def update_min_nights(nb): return charts.get_minimum_nights_chart(nb)

    @app.callback(Output('policy-license', 'figure'), Input('policy-neighbourhood-filter', 'value'))
    def update_license(_): return charts.get_license_compliance_chart()

    @app.callback(Output('policy-occupancy-timeline', 'figure'), Input('policy-neighbourhood-filter', 'value'))
    def update_occ_time(_): return charts.get_occupancy_timeline()

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
        df = charts.get_export_dataframe(neighbourhood, room_type, min_p, max_p, search)
        if df.empty:
            return html.P("No listings match.", style={"color": "var(--text-muted)"}), ""

        row_count = f"Showing {len(df):,} of {len(charts.LISTINGS_DF):,} listings"
        display_df = df.copy()
        for col in ['price', 'est_annual_revenue']:
            if col in display_df.columns:
                display_df[col] = display_df[col].apply(lambda x: f"€{x:,.0f}" if pd.notna(x) else "")
        if 'occupancy_pct' in display_df.columns:
            display_df['occupancy_pct'] = display_df['occupancy_pct'].apply(lambda x: f"{x:.0f}%" if pd.notna(x) else "")
        if 'reviews_per_month' in display_df.columns:
            display_df['reviews_per_month'] = display_df['reviews_per_month'].apply(lambda x: f"{x:.1f}" if pd.notna(x) else "")

        table = dash_table.DataTable(
            data=display_df.to_dict('records'),
            columns=[{"name": c.replace('_', ' ').title(), "id": c} for c in display_df.columns],
            page_size=25, sort_action="native", filter_action="native",
            style_table={'minWidth': '100%'},
            style_cell={'textAlign': 'left', 'padding': '6px 10px', 'fontSize': '12px',
                       'fontFamily': 'Inter, sans-serif', 'whiteSpace': 'normal', 'height': 'auto',
                       'backgroundColor': 'var(--bg-card)', 'color': 'var(--text-primary)',
                       'borderBottom': '1px solid var(--border-subtle)'},
            style_header={'backgroundColor': 'var(--bg-secondary)', 'fontWeight': '600',
                         'fontSize': '11px', 'textTransform': 'uppercase', 'letterSpacing': '0.5px',
                         'color': 'var(--text-secondary)', 'borderBottom': '2px solid var(--border-medium)'},
            style_data_conditional=[
                {'if': {'row_index': 'odd'}, 'backgroundColor': 'rgba(255,255,255,0.02)'},
            ],
            style_filter={'backgroundColor': 'var(--bg-secondary)', 'border': '1px solid var(--border-medium)'},
        )
        return table, html.Small(f"🔍 {row_count}", style={"color": "var(--text-muted)", "fontSize": "12px"})

    @app.callback(
        Output('download-dataframe-csv', 'data'),
        Input('btn-download-csv', 'n_clicks'),
        State('explorer-neighbourhood', 'value'),
        State('explorer-room-type', 'value'),
        State('explorer-price-range', 'value'),
        State('explorer-search', 'value'),
        prevent_initial_call=True,
    )
    def download_csv(n, neighbourhood, room_type, price_range, search):
        min_p, max_p = price_range if price_range else (0, 9999)
        df = charts.get_export_dataframe(neighbourhood, room_type, min_p, max_p, search)
        return dcc.send_data_frame(df.to_csv, "airbnb_amsterdam_export.csv", index=False)

    # ═══════════════════════════════════════════════════
    #  TAB 6 — ROI CALCULATOR + COMPARISON
    # ═══════════════════════════════════════════════════

    @app.callback(
        Output('roi-results', 'children'),
        Input('roi-price', 'value'), Input('roi-occupancy', 'value'),
        Input('roi-num-listings', 'value'), Input('roi-room-type', 'value'),
    )
    def update_roi(price, occupancy, num, room_type):
        if None in (price, occupancy, num):
            return html.P("Adjust controls to see projections.", style={"color": "var(--text-muted)"})
        r = charts.calculate_roi(price, occupancy, num, room_type)
        arrow = "↑" if r['price_vs_market_pct'] > 0 else "↓"
        color = "var(--accent-green)" if r['revenue_vs_market_pct'] > 0 else "var(--accent-red)"

        def mini_card(val, label, color="var(--text-primary)"):
            return html.Div([
                html.Div(val, style={"fontSize": "20px", "fontWeight": "700", "color": color}),
                html.Div(label, style={"fontSize": "11px", "color": "var(--text-muted)", "marginTop": "2px"}),
            ], style={"flex": "1", "textAlign": "center"})

        return html.Div([
            html.Div([mini_card(f"€{r['annual_revenue']:,.0f}", "Annual Revenue", "var(--accent-blue)"),
                      mini_card(f"€{r['monthly_revenue']:,.0f}", "Monthly Revenue", "var(--accent-green)"),
                      mini_card(f"{r['booked_days']:.0f}d", "Booked Days"),
                      mini_card(f"{arrow}{abs(r['price_vs_market_pct']):.0f}%", "vs Market Price"),
                      mini_card(f"{abs(r['revenue_vs_market_pct']):.0f}%", "vs Market Revenue", color),
                      ], style={"display": "flex", "gap": "12px", "marginBottom": "12px"}),
            html.Hr(style={"borderColor": "var(--border-subtle)"}),
            html.Small(f"Benchmark: {room_type} — Avg €{r['market_avg_price']:.0f}/night, "
                       f"{r['market_avg_occupancy']:.0f}% occ., €{r['market_avg_revenue']:,.0f}/yr",
                       style={"color": "var(--text-muted)"}),
        ])

    @app.callback(
        Output('comparison-results', 'children'),
        Input('compare-nb1', 'value'), Input('compare-nb2', 'value'),
    )
    def update_comparison(nb1, nb2):
        if not nb1 or not nb2:
            return html.P("Select two areas to compare.", style={"color": "var(--text-muted)"})
        comp = charts.get_neighbourhood_comparison(nb1, nb2)
        s1, s2 = comp.get('nb1'), comp.get('nb2')
        if not s1 or not s2:
            return html.P("Could not compute comparison.", style={"color": "var(--accent-red)"})

        def row(label, key, fmt=",.0f", pre="", suf=""):
            v1, v2 = s1[key], s2[key]
            v1s = f"{pre}{v1:{fmt}}{suf}" if isinstance(v1, float) else str(v1)
            v2s = f"{pre}{v2:{fmt}}{suf}" if isinstance(v2, float) else str(v2)
            g1, g2 = "", ""
            if isinstance(v1, (int,float)) and isinstance(v2, (int,float)) and v1 != v2:
                if key in ('avg_price', 'avg_min_nights'):
                    g1, g2 = ("🟢 ","") if v1 < v2 else ("","🟢 ")
                else:
                    g1, g2 = ("🟢 ","") if v1 > v2 else ("","🟢 ")
            return html.Tr([html.Td(label), html.Td(f"{g1}{v1s}"), html.Td(f"{g2}{v2s}")])

        return html.Table([
            html.Thead(html.Tr([html.Th("Metric"), html.Th(comp['nb1_name']), html.Th(comp['nb2_name'])])),
            html.Tbody([
                row("Listings", "listings"), row("Avg Price", "avg_price", pre="€"),
                row("Median Price", "median_price", pre="€"),
                row("Occupancy", "avg_occupancy", suf="%"),
                row("Est Revenue", "est_total_revenue", pre="€"),
                row("Entire Home %", "entire_home_pct", suf="%"),
                row("Licensed %", "licensed_pct", suf="%"),
                row("Min Nights", "avg_min_nights"),
                row("Reviews/Mo", "avg_reviews_per_month"),
                row("Top Hosts", "top_host_category", fmt=""),
            ]),
        ], className="comparison-table")

    # ═══════════════════════════════════════════════════
    #  STRATEGIC INTELLIGENCE — Warnings + Briefing
    # ═══════════════════════════════════════════════════

    @app.callback(
        Output('strat-early-warnings', 'children'),
        Input('live-refresh-interval', 'n_intervals')
    )
    def update_warnings(_):
        warnings = charts.get_early_warnings()
        if not warnings:
            return html.P("✅ No active warnings — market conditions stable.",
                         style={"color": "var(--accent-green)", "fontSize": "14px"})

        level_map = {'🔴 HIGH': 'high', '🟠 MEDIUM': 'medium', '🟡 INFO': 'info'}
        cards = []
        for w in warnings:
            cards.append(html.Div([
                html.Div(w['level'], className="alert-level",
                        style={"color": "var(--accent-red)" if 'HIGH' in w['level']
                               else "var(--accent-amber)" if 'MEDIUM' in w['level']
                               else "var(--accent-blue)"}),
                html.Div(w['neighbourhood'], className="alert-title"),
                html.Div(w['message'], className="alert-msg"),
            ], className=f"alert-card {level_map.get(w['level'], 'info')}"))
        return html.Div(cards, style={"display": "grid", "gridTemplateColumns": "repeat(auto-fill, minmax(300px, 1fr))",
                                       "gap": "10px"})

    @app.callback(
        Output('strat-briefing', 'children'),
        Input('live-refresh-interval', 'n_intervals')
    )
    def update_briefing(_):
        return charts.generate_market_briefing()

    # ═══════════════════════════════════════════════════
    #  LIVE REFRESH — KPIs + Timestamp
    # ═══════════════════════════════════════════════════

    @app.callback(
        Output('kpi-header-row', 'children'),
        Output('sidebar-refresh-time', 'children'),
        Input('live-refresh-interval', 'n_intervals')
    )
    def live_refresh_kpis(_):
        kpi = charts.get_kpi_metrics()
        now = datetime.now().strftime('%H:%M')
        if not kpi:
            return [], f"Updated: {now}"

        license_val = float(kpi['licensed_pct'].replace('%', ''))
        entire_val = float(kpi['entire_home_pct'].replace('%', ''))

        cards = [
            html.Div([html.Div(kpi['total_listings'], className="kpi-value"),
                      html.Div("Total Listings", className="kpi-label")], className="kpi-card info"),
            html.Div([html.Div(kpi['avg_price'], className="kpi-value"),
                      html.Div("Avg Nightly Price", className="kpi-label")], className="kpi-card info"),
            html.Div([html.Div(kpi['avg_occupancy'], className="kpi-value"),
                      html.Div("Avg Occupancy", className="kpi-label")], className="kpi-card info"),
            html.Div([html.Div(kpi['total_est_revenue'], className="kpi-value"),
                      html.Div("Est Annual Revenue", className="kpi-label")], className="kpi-card info"),
            html.Div([html.Div(kpi['entire_home_pct'], className="kpi-value"),
                      html.Div("Entire Home Share", className="kpi-label")],
                     className="kpi-card warning" if entire_val > 60 else "kpi-card info"),
            html.Div([html.Div(kpi['licensed_pct'], className="kpi-value"),
                      html.Div("License Compliance", className="kpi-label")],
                     className="kpi-card success" if license_val > 50 else "kpi-card danger"),
        ]
        return cards, f"Updated: {now}"

    pass
