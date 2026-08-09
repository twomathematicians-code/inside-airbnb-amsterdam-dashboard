# app.py
"""
Inside Airbnb Amsterdam — Industrial-Grade Strategic Intelligence Dashboard
Run: python app.py  →  http://localhost:8051
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

# ── App ───────────────────────────────────────────────
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.DARKLY, dbc.icons.BOOTSTRAP],
    title="Airbnb Amsterdam — Strategic Intelligence",
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
    suppress_callback_exceptions=True,
)

server = app.server

# ── Layout & Callbacks ────────────────────────────────
app.layout = html.Div(get_app_layout())
register_callbacks(app)

# ── Main ─────────────────────────────────────────────
if __name__ == "__main__":
    print(f"\n{'='*60}")
    print(f"  🏠 Airbnb Amsterdam — Strategic Intelligence Dashboard")
    print(f"  🌐 http://{HOST}:{PORT}")
    print(f"  📊 11 Pages | 30+ Charts | SWOT | Role-Based Dashboards")
    print(f"  🎨 Industrial Dark Theme | 🔄 Live Refresh 5min")
    print(f"{'='*60}\n")
    app.run(
        debug=DEBUG, host=HOST, port=PORT,
        dev_tools_hot_reload=False, use_reloader=False,
    )
