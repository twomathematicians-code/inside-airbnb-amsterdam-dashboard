# app.py
"""
Inside Airbnb Amsterdam — Business Intelligence Dashboard
Run with: python app.py
Open: http://localhost:8051
"""

import os
import dash
from dash import html
import dash_bootstrap_components as dbc
from layout import get_app_layout
from callbacks import register_callbacks

# ── Configuration ─────────────────────────────────────
PORT = int(os.environ.get("PORT", 8051))
DEBUG = os.environ.get("DEBUG", "false").lower() == "true"
HOST = os.environ.get("HOST", "127.0.0.1")

# ── App Initialization ────────────────────────────────
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.MINTY, dbc.icons.BOOTSTRAP],
    title="Airbnb Amsterdam — Business Intelligence",
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
    suppress_callback_exceptions=True,
)

# Expose Flask server for Gunicorn
server = app.server

# ── Layout & Callbacks ────────────────────────────────
app.layout = html.Div(get_app_layout())
register_callbacks(app)

# ── Main ─────────────────────────────────────────────
if __name__ == "__main__":
    print(f"\n{'='*60}")
    print(f"  🏠 Inside Airbnb Amsterdam — Business Intelligence Dashboard")
    print(f"  🌐 Starting on http://{HOST}:{PORT}")
    print(f"  📊 Tabs: Market Overview | Business Intelligence | Policy & Compliance")
    print(f"  🔄 Live refresh: every 5 minutes")
    print(f"{'='*60}\n")
    app.run(
        debug=DEBUG,
        host=HOST,
        port=PORT,
        dev_tools_hot_reload=False,
        use_reloader=False,
    )
