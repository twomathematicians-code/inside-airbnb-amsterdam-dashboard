# callbacks.py
from dash.dependencies import Input, Output, State
import charts
from dash import html, dcc
import dash_bootstrap_components as dbc


def register_callbacks(app):
    """Function to register all callbacks from within app.py"""

    # --- Interaction 1: Price Range Slider on Price Histogram ---
    @app.callback(
        Output('ex1A-basic-chart-price-dist', 'figure'),
        Input('price-range-slider', 'value')
    )
    def update_price_histogram(price_range):
        """Updates the Price Histogram figure based on the selected price range."""
        return charts.get_price_distribution_chart(price_range)

    # --- Interaction 2: Master Filter on Room Type Pie Chart ---
    @app.callback(
        Output('ex1B-basic-chart-room-type', 'figure'),
        # Uses the new single master filter ID
        Input('master-filter-neighbourhood', 'value')
    )
    def update_room_type_pie_chart(selected_neighbourhood):
        """Updates the Room Type Pie Chart figure based on the selected neighbourhood."""
        return charts.get_room_type_pie_chart(selected_neighbourhood)

    # --- Interaction 3: Master Filter on the Map ---
    @app.callback(
        Output('ex3-map-visualization', 'figure'),
        # Uses the new single master filter ID
        Input('master-filter-neighbourhood', 'value')
    )
    def update_map_by_neighbourhood(selected_neighbourhood):
        """Updates the Map figure, filtering the individual listings based on the selected neighbourhood."""
        return charts.get_map(selected_neighbourhood)

    pass