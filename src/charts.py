# charts.py
import pandas as pd
import plotly.express as px
from dash import dcc
import json

LISTINGS_PATH = "data/listings.csv"
NEIGHBOURHOODS_PATH = "data/neighbourhoods.geojson"


# --- GLOBAL DATA LOAD (Happens ONCE for stability) ---
def _load_listings_data(path=LISTINGS_PATH):
    try:
        df = pd.read_csv(path)
        # Use a raw string for regex to correctly escape the '$'
        df['price'] = df['price'].replace({r'\$': '', ',': ''}, regex=True).astype(float)
        return df
    except Exception as e:
        print(f"❌ CRITICAL ERROR reading data at {path}: {e}")
        return pd.DataFrame()


def _load_geojson(path=NEIGHBOURHOODS_PATH):
    try:
        with open(path, 'r') as f:
            geojson = json.load(f)
        return geojson
    except Exception as e:
        print(f"❌ CRITICAL ERROR reading GeoJSON at {path}: {e}")
        return None


LISTINGS_DF = _load_listings_data()
NEIGHBOURHOODS_GEOJSON = _load_geojson()

ROOM_TYPE_COLORS = {
    'Entire home/apt': '#1f77b4',
    'Private room': '#ff7f0e',
    'Shared room': '#2ca02c',
    'Hotel room': '#d62728'
}


# --- Chart Generation Functions ---

def get_price_distribution_chart(price_range):
    listings = LISTINGS_DF
    if listings.empty: return {}
    min_price, max_price = price_range
    df_filtered = listings[
        (listings['price'] >= min_price) &
        (listings['price'] <= max_price)
        ]

    fig = px.histogram(
        df_filtered, x="price", nbins=50,
        title=f"Frequency Distribution of Daily Rental Prices (€{min_price} - €{max_price})",
        labels={'price': 'Price (€)'},
        color_discrete_sequence=[px.colors.sequential.Teal[4]]
    )

    fig.update_layout(
        bargap=0.05,
        xaxis_title="Daily Price (€)", yaxis_title="Number of Listings",
        margin=dict(l=20, r=20, t=40, b=50),
        height=300,
        font=dict(size=11),
        title_font_size=16
    )
    return fig


def get_room_type_pie_chart(selected_neighbourhood=None):
    listings = LISTINGS_DF
    if listings.empty: return {}
    df_filtered = listings.copy()
    title_suffix = " (All Listings)"

    if selected_neighbourhood and selected_neighbourhood != 'All':
        df_filtered = listings[listings['neighbourhood'] == selected_neighbourhood]
        title_suffix = f" in {selected_neighbourhood}"

    room_counts = df_filtered['room_type'].value_counts().reset_index()
    room_counts.columns = ['Room Type', 'Count']

    fig = px.pie(
        room_counts, values='Count', names='Room Type',
        title='Proportion of Housing Unit Types (Displacement Risk)' + title_suffix,
        color='Room Type',
        color_discrete_map=ROOM_TYPE_COLORS
    )

    fig.update_traces(
        textinfo='percent+label',
        marker=dict(line=dict(color='#000000', width=1)),
        textposition='outside',
        insidetextfont=dict(color='white')
    )
    fig.update_layout(
        margin=dict(l=20, r=20, t=60, b=20),
        height=300,
        font=dict(size=11),
        title_font_size=16,
        uniformtext_minsize=9,
        uniformtext_mode='hide'
    )
    return fig


def get_map(selected_neighbourhood=None):
    listings = LISTINGS_DF
    geojson_data = NEIGHBOURHOODS_GEOJSON

    if listings.empty or geojson_data is None: return {}

    # 1. Choropleth Data (Average Price)
    neighbourhood_data = listings.groupby('neighbourhood')['price'].mean().reset_index()
    neighbourhood_data.columns = ['neighbourhood', 'average_price']
    max_avg_price = neighbourhood_data['average_price'].quantile(0.95)

    choropleth_fig = px.choropleth_mapbox(
        neighbourhood_data, geojson=geojson_data, locations='neighbourhood',
        featureidkey="properties.neighbourhood", color='average_price',
        color_continuous_scale="Viridis",
        range_color=(neighbourhood_data['average_price'].min(), max_avg_price),
        mapbox_style="carto-positron", zoom=10.5,
        center={"lat": listings['latitude'].mean(), "lon": listings['longitude'].mean()},
        opacity=0.7, labels={'average_price': 'Avg. Price (€)'},
        hover_data={'neighbourhood': True, 'average_price': ':.2f'}
    )

    # 2. Scatter Data (Individual Listings)
    df_scatter = listings.copy()
    title_suffix = ""
    if selected_neighbourhood and selected_neighbourhood != 'All':
        df_scatter = listings[listings['neighbourhood'] == selected_neighbourhood]
        title_suffix = f" (Filtered: {selected_neighbourhood})"

    scatter_fig = px.scatter_mapbox(
        df_scatter, lat="latitude", lon="longitude", hover_name="host_name",
        hover_data={'price': True, 'room_type': True, 'latitude': False, 'longitude': False},
        color="room_type",
        color_discrete_map=ROOM_TYPE_COLORS,
        zoom=10.5,
        center={"lat": listings['latitude'].mean(), "lon": listings['longitude'].mean()},
        opacity=0.8, size_max=10,
    )

    # 3. Combine figures
    for trace in scatter_fig.data:
        choropleth_fig.add_trace(trace)

    # 4. Map Layout Adjustments to fix overlap
    choropleth_fig.update_layout(
        title=f"Spatial Concentration of Listings and Average Price by Neighbourhood{title_suffix}",
        mapbox_style="carto-positron",
        margin={"r": 0, "t": 50, "l": 0, "b": 0},
        height=500,
        font=dict(size=11),
        title_font_size=16,

        # --- TITLE POSITION FIX ---
        title_y=0.98,  # Push title slightly higher

        # --- LEGEND POSITION FIX (Scatter plot) ---
        legend=dict(
            title_text="Room Type",
            orientation="h",  # Horizontal legend
            yanchor="top",
            y=0.95,  # Position near the top of the map
            xanchor="left",
            x=0.01,  # Position in the top left corner
            bgcolor='rgba(255,255,255,0.7)'  # Add a white background for clarity
        ),

        # --- COLORBAR POSITION FIX (Choropleth) ---
        coloraxis_colorbar=dict(
            title="Avg. Price (€)",
            orientation="h",  # Horizontal colorbar
            yanchor="bottom",
            y=0.01,  # Position at the bottom of the map
            xanchor="left",
            x=0.01,  # Start position
            len=0.5  # Length (50% of plot width)
        )
    )

    return choropleth_fig


# --- Placeholder functions for layout.py to use for initial load ---

def get_basic_chart_A():
    return dcc.Graph(
        id="ex1A-basic-chart-price-dist",
        figure=get_price_distribution_chart([0, 250]),
        style={'height': '350px'}
    )


def get_basic_chart_B():
    return dcc.Graph(
        id="ex1B-basic-chart-room-type",
        figure=get_room_type_pie_chart(None),
        style={'height': '350px'}
    )


def get_map_component():
    return dcc.Graph(
        id="ex3-map-visualization",
        figure=get_map(None),
        style={'height': '550px'}
    )