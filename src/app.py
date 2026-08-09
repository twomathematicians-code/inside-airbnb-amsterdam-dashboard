# app.py
"""
Main application file for the Dash Dashboard.
Run with: python app.py
"""

import dash
from dash import html
import dash_bootstrap_components as dbc
from layout import get_app_layout
from callbacks import register_callbacks

# choose your own theme here: https://bootswatch.com/default/
app = dash.Dash(external_stylesheets=[dbc.themes.MINTY])
app.title = "Inside Airbnb Gent"
app.layout = html.Div(get_app_layout())
register_callbacks(app)


if __name__ == "__main__":
    app.run(
        debug=True, port=8051, dev_tools_hot_reload=False, use_reloader=False
    )