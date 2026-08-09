# charts.py
"""
Data pipeline & Plotly figure factory for Inside Airbnb Amsterdam Dashboard.
All data loads once at module import (singleton pattern).
Every chart function returns a Plotly figure dict.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dash import dcc
import json
import numpy as np

# ── Paths ──────────────────────────────────────────────
LISTINGS_PATH = "data/listings.csv"
NEIGHBOURHOODS_PATH = "data/neighbourhoods.geojson"

# ── Global Data Load (singleton) ───────────────────────
def _load_listings_data(path=LISTINGS_PATH):
    try:
        df = pd.read_csv(path)
        df['price'] = df['price'].replace({r'\$': '', ',': ''}, regex=True).astype(float)
        # Normalize neighbourhood column (some cities use 'neighbourhood_cleansed')
        if 'neighbourhood_cleansed' in df.columns and df['neighbourhood'].isna().all():
            df['neighbourhood'] = df['neighbourhood_cleansed']
        # Derived business metrics
        df['booked_days'] = 365 - df['availability_365']
        df['occupancy_pct'] = (df['booked_days'] / 365 * 100).round(1)
        df['est_annual_revenue'] = (df['price'] * df['booked_days']).round(2)
        df['host_category'] = pd.cut(
            df['calculated_host_listings_count'],
            bins=[0, 1, 5, float('inf')],
            labels=['Individual (1)', 'Small (2-5)', 'Professional (6+)']
        )
        df['license_status'] = df['license'].notna().map({True: 'Licensed', False: 'Unlicensed'})
        return df
    except Exception as e:
        print(f"❌ CRITICAL ERROR reading data at {path}: {e}")
        return pd.DataFrame()


def _load_geojson(path=NEIGHBOURHOODS_PATH):
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ CRITICAL ERROR reading GeoJSON at {path}: {e}")
        return None


LISTINGS_DF = _load_listings_data()
NEIGHBOURHOODS_GEOJSON = _load_geojson()

# ── Color Palettes ─────────────────────────────────────
ROOM_TYPE_COLORS = {
    'Entire home/apt': '#1f77b4',
    'Private room': '#ff7f0e',
    'Shared room': '#2ca02c',
    'Hotel room': '#d62728'
}

HOST_CATEGORY_COLORS = {
    'Individual (1)': '#2ca02c',
    'Small (2-5)': '#ff7f0e',
    'Professional (6+)': '#d62728'
}

BI_COLOR = px.colors.sequential.Teal
ACCENT = '#1f77b4'
WARN = '#d62728'


# ═══════════════════════════════════════════════════════
#  TAB 1 — MARKET OVERVIEW (existing + enhanced)
# ═══════════════════════════════════════════════════════

def get_price_distribution_chart(price_range):
    listings = LISTINGS_DF
    if listings.empty: return {}
    min_price, max_price = price_range
    df_filtered = listings[(listings['price'] >= min_price) & (listings['price'] <= max_price)]

    fig = px.histogram(
        df_filtered, x="price", nbins=50,
        title=f"Frequency Distribution of Daily Rental Prices (€{min_price} – €{max_price})",
        labels={'price': 'Daily Price (€)'},
        color_discrete_sequence=[BI_COLOR[4]]
    )
    fig.update_layout(
        bargap=0.05, xaxis_title="Daily Price (€)", yaxis_title="Number of Listings",
        margin=dict(l=20, r=20, t=40, b=50), height=350,
        font=dict(size=11), title_font_size=16
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
        color='Room Type', color_discrete_map=ROOM_TYPE_COLORS
    )
    fig.update_traces(
        textinfo='percent+label', marker=dict(line=dict(color='#000000', width=1)),
        textposition='outside', insidetextfont=dict(color='white')
    )
    fig.update_layout(
        margin=dict(l=20, r=20, t=60, b=20), height=350,
        font=dict(size=11), title_font_size=16,
        uniformtext_minsize=9, uniformtext_mode='hide'
    )
    return fig


def get_map(selected_neighbourhood=None):
    listings = LISTINGS_DF
    geojson_data = NEIGHBOURHOODS_GEOJSON
    if listings.empty or geojson_data is None: return {}

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

    df_scatter = listings.copy()
    title_suffix = ""
    if selected_neighbourhood and selected_neighbourhood != 'All':
        df_scatter = listings[listings['neighbourhood'] == selected_neighbourhood]
        title_suffix = f" (Filtered: {selected_neighbourhood})"

    scatter_fig = px.scatter_mapbox(
        df_scatter, lat="latitude", lon="longitude", hover_name="host_name",
        hover_data={'price': True, 'room_type': True, 'latitude': False, 'longitude': False},
        color="room_type", color_discrete_map=ROOM_TYPE_COLORS,
        zoom=10.5,
        center={"lat": listings['latitude'].mean(), "lon": listings['longitude'].mean()},
        opacity=0.8, size_max=10,
    )

    for trace in scatter_fig.data:
        choropleth_fig.add_trace(trace)

    choropleth_fig.update_layout(
        title=f"Spatial Concentration of Listings & Average Price by Neighbourhood{title_suffix}",
        mapbox_style="carto-positron", margin={"r": 0, "t": 50, "l": 0, "b": 0},
        height=500, font=dict(size=11), title_font_size=16, title_y=0.98,
        legend=dict(title_text="Room Type", orientation="h", yanchor="top", y=0.95,
                    xanchor="left", x=0.01, bgcolor='rgba(255,255,255,0.7)'),
        coloraxis_colorbar=dict(title="Avg. Price (€)", orientation="h", yanchor="bottom",
                                y=0.01, xanchor="left", x=0.01, len=0.5)
    )
    return choropleth_fig


# ═══════════════════════════════════════════════════════
#  TAB 2 — BUSINESS INTELLIGENCE
# ═══════════════════════════════════════════════════════

def get_occupancy_chart(selected_neighbourhood=None):
    """Occupancy rate by neighbourhood — bar chart."""
    listings = LISTINGS_DF
    if listings.empty: return {}
    df = listings.copy()
    title_suffix = " — All Neighbourhoods"
    if selected_neighbourhood and selected_neighbourhood != 'All':
        df = df[df['neighbourhood'] == selected_neighbourhood]
        title_suffix = f" — {selected_neighbourhood}"

    occ_by_area = df.groupby('neighbourhood')['occupancy_pct'].mean().sort_values(ascending=True).reset_index()
    occ_by_area.columns = ['Neighbourhood', 'Avg. Occupancy %']

    fig = px.bar(
        occ_by_area, y='Neighbourhood', x='Avg. Occupancy %',
        title=f'Occupancy Rate by Neighbourhood{title_suffix}',
        color='Avg. Occupancy %', color_continuous_scale='RdYlGn',
        text=occ_by_area['Avg. Occupancy %'].round(1)
    )
    fig.update_traces(textposition='outside')
    fig.update_layout(
        height=max(400, len(occ_by_area) * 25), margin=dict(l=20, r=20, t=50, b=20),
        xaxis_title="Average Occupancy (%)", yaxis_title="", font=dict(size=11),
        title_font_size=16, coloraxis_showscale=False
    )
    return fig


def get_revenue_boxplot(selected_neighbourhood=None):
    """Estimated annual revenue distribution by room type."""
    listings = LISTINGS_DF
    if listings.empty: return {}
    df = listings.copy()
    title_suffix = " — All Neighbourhoods"
    if selected_neighbourhood and selected_neighbourhood != 'All':
        df = df[df['neighbourhood'] == selected_neighbourhood]
        title_suffix = f" — {selected_neighbourhood}"

    # Cap outliers for readability
    cap = df['est_annual_revenue'].quantile(0.95)
    df_plot = df[df['est_annual_revenue'] <= cap]

    fig = px.box(
        df_plot, x='room_type', y='est_annual_revenue', color='room_type',
        title=f'Estimated Annual Revenue Distribution by Room Type{title_suffix}',
        color_discrete_map=ROOM_TYPE_COLORS,
        labels={'est_annual_revenue': 'Est. Annual Revenue (€)', 'room_type': 'Room Type'}
    )
    fig.update_layout(
        height=400, margin=dict(l=20, r=20, t=50, b=20),
        font=dict(size=11), title_font_size=16, showlegend=False,
        yaxis_tickprefix='€'
    )
    return fig


def get_demand_supply_chart():
    """Reviews per month (demand proxy) vs listing count (supply) by neighbourhood."""
    listings = LISTINGS_DF
    if listings.empty: return {}

    demand_supply = listings.groupby('neighbourhood').agg(
        avg_reviews_per_month=('reviews_per_month', 'mean'),
        total_listings=('id', 'count'),
        avg_price=('price', 'mean'),
        avg_occupancy=('occupancy_pct', 'mean')
    ).reset_index()

    fig = px.scatter(
        demand_supply, x='total_listings', y='avg_reviews_per_month',
        size='avg_price', color='avg_occupancy',
        hover_name='neighbourhood', text='neighbourhood',
        title='Demand–Supply Matrix: Reviews/Month vs Total Listings by Neighbourhood',
        labels={
            'total_listings': 'Total Listings (Supply)',
            'avg_reviews_per_month': 'Avg. Reviews/Month (Demand Proxy)',
            'avg_price': 'Avg. Price (€)',
            'avg_occupancy': 'Avg. Occupancy %'
        },
        color_continuous_scale='Viridis', size_max=40
    )
    fig.update_traces(textposition='top center', textfont=dict(size=9))
    fig.update_layout(
        height=500, margin=dict(l=20, r=20, t=50, b=20),
        font=dict(size=11), title_font_size=16
    )
    # Add quadrant lines
    median_x = demand_supply['total_listings'].median()
    median_y = demand_supply['avg_reviews_per_month'].median()
    fig.add_hline(y=median_y, line_dash="dash", line_color="gray", opacity=0.5,
                  annotation_text="Median Demand")
    fig.add_vline(x=median_x, line_dash="dash", line_color="gray", opacity=0.5,
                  annotation_text="Median Supply")
    return fig


def get_host_concentration_chart(selected_neighbourhood=None):
    """Multi-listing hosts vs individuals — market professionalization."""
    listings = LISTINGS_DF
    if listings.empty: return {}
    df = listings.copy()
    title_suffix = " — All Neighbourhoods"
    if selected_neighbourhood and selected_neighbourhood != 'All':
        df = df[df['neighbourhood'] == selected_neighbourhood]
        title_suffix = f" — {selected_neighbourhood}"

    host_counts = df['host_category'].value_counts().reset_index()
    host_counts.columns = ['Host Category', 'Number of Listings']

    fig = px.pie(
        host_counts, values='Number of Listings', names='Host Category',
        title=f'Host Concentration: Market Professionalization{title_suffix}',
        color='Host Category', color_discrete_map=HOST_CATEGORY_COLORS,
        hole=0.4
    )
    fig.update_traces(textinfo='percent+label+value', textposition='outside')
    fig.update_layout(
        height=400, margin=dict(l=20, r=20, t=60, b=20),
        font=dict(size=11), title_font_size=16,
        annotations=[dict(text='Host Types', x=0.5, y=0.5, font_size=14, showarrow=False)]
    )
    return fig


def get_pricing_position_chart():
    """Percentile pricing guide — where does a given price sit in the market?"""
    listings = LISTINGS_DF
    if listings.empty: return {}

    percentiles = {}
    for room in listings['room_type'].unique():
        subset = listings[listings['room_type'] == room]['price']
        percentiles[room] = {
            'P25': subset.quantile(0.25),
            'P50': subset.quantile(0.50),
            'P75': subset.quantile(0.75),
            'P90': subset.quantile(0.90),
            'Mean': subset.mean()
        }

    rooms = list(percentiles.keys())
    fig = go.Figure()
    for i, room in enumerate(rooms):
        p = percentiles[room]
        fig.add_trace(go.Bar(
            name=room,
            x=['25th (Budget)', '50th (Median)', '75th (Premium)', '90th (Luxury)', 'Mean'],
            y=[p['P25'], p['P50'], p['P75'], p['P90'], p['Mean']],
            marker_color=list(ROOM_TYPE_COLORS.values())[i % len(ROOM_TYPE_COLORS)],
            text=[f'€{v:.0f}' for v in [p['P25'], p['P50'], p['P75'], p['P90'], p['Mean']]],
            textposition='outside'
        ))

    fig.update_layout(
        title='Pricing Position Guide: Market Percentiles by Room Type',
        barmode='group', height=450, margin=dict(l=20, r=20, t=50, b=20),
        yaxis_title='Price per Night (€)', yaxis_tickprefix='€',
        font=dict(size=11), title_font_size=16,
        legend=dict(title_text="Room Type", orientation="h", y=1.12)
    )
    return fig


def get_rating_price_matrix():
    """Scatter: Review score rating vs price — value hotspots."""
    listings = LISTINGS_DF
    if listings.empty: return {}

    # Note: review_scores_rating not in this dataset; use reviews_per_month as quality proxy
    df = listings[listings['reviews_per_month'] > 0].copy()
    if df.empty: return {}

    fig = px.scatter(
        df, x='price', y='reviews_per_month', color='room_type',
        size='booked_days', hover_name='host_name',
        color_discrete_map=ROOM_TYPE_COLORS,
        title='Value Matrix: Demand Intensity (Reviews/Month) vs Price',
        labels={
            'price': 'Daily Price (€)',
            'reviews_per_month': 'Reviews/Month (Demand Proxy)',
            'booked_days': 'Booked Days/Year'
        },
        opacity=0.7
    )
    # Sweet spot annotation
    fig.add_hline(y=df['reviews_per_month'].quantile(0.75), line_dash="dash",
                  line_color="green", opacity=0.5, annotation_text="High Demand")
    fig.add_vline(x=df['price'].median(), line_dash="dash",
                  line_color="blue", opacity=0.5, annotation_text="Median Price")
    fig.update_layout(
        height=450, margin=dict(l=20, r=20, t=50, b=20),
        font=dict(size=11), title_font_size=16, xaxis_tickprefix='€'
    )
    return fig


def get_revenue_treemap(selected_neighbourhood=None):
    """Treemap: Revenue breakdown by neighbourhood × room type."""
    listings = LISTINGS_DF
    if listings.empty: return {}
    df = listings.copy()
    title_suffix = " — All Neighbourhoods"
    if selected_neighbourhood and selected_neighbourhood != 'All':
        df = df[df['neighbourhood'] == selected_neighbourhood]
        title_suffix = f" — {selected_neighbourhood}"

    revenue_tree = df.groupby(['neighbourhood', 'room_type']).agg(
        total_revenue=('est_annual_revenue', 'sum'),
        listing_count=('id', 'count')
    ).reset_index()

    fig = px.treemap(
        revenue_tree, path=['neighbourhood', 'room_type'],
        values='total_revenue', color='total_revenue',
        color_continuous_scale='Teal',
        hover_data={'listing_count': True, 'total_revenue': ':.0f'},
        title=f'Revenue Share: Neighbourhood × Room Type{title_suffix}'
    )
    fig.update_layout(
        height=500, margin=dict(l=20, r=20, t=50, b=20),
        font=dict(size=11), title_font_size=16
    )
    return fig


# ═══════════════════════════════════════════════════════
#  BUSINESS UTILITIES — Data Export, ROI, Comparison
# ═══════════════════════════════════════════════════════

def get_export_dataframe(selected_neighbourhood=None, room_type_filter=None,
                         min_price=None, max_price=None, search_term=None):
    """Return filtered DataFrame for DataTable display and CSV export."""
    df = LISTINGS_DF.copy()
    if df.empty:
        return df

    if selected_neighbourhood and selected_neighbourhood != 'All':
        df = df[df['neighbourhood'] == selected_neighbourhood]
    if room_type_filter and room_type_filter != 'All':
        df = df[df['room_type'] == room_type_filter]
    if min_price is not None:
        df = df[df['price'] >= min_price]
    if max_price is not None:
        df = df[df['price'] <= max_price]
    if search_term:
        mask = df['host_name'].str.contains(search_term, case=False, na=False)
        if 'name' in df.columns:
            mask |= df['name'].str.contains(search_term, case=False, na=False)
        df = df[mask]

    cols = ['name', 'host_name', 'neighbourhood', 'room_type', 'price',
            'minimum_nights', 'occupancy_pct', 'est_annual_revenue',
            'number_of_reviews', 'reviews_per_month', 'license_status']
    available = [c for c in cols if c in df.columns]
    return df[available]


def get_neighbourhood_comparison(nb1, nb2):
    """Side-by-side KPI comparison for two neighbourhoods."""
    listings = LISTINGS_DF
    if listings.empty: return {}

    def stats_for(nb):
        sub = listings[listings['neighbourhood'] == nb]
        if sub.empty: return None
        return {
            'listings': len(sub),
            'avg_price': sub['price'].mean(),
            'median_price': sub['price'].median(),
            'avg_occupancy': sub['occupancy_pct'].mean(),
            'est_total_revenue': sub['est_annual_revenue'].sum(),
            'entire_home_pct': (sub['room_type'] == 'Entire home/apt').mean() * 100,
            'licensed_pct': (sub['license_status'] == 'Licensed').mean() * 100,
            'avg_min_nights': sub['minimum_nights'].mean(),
            'top_host_category': sub['host_category'].mode().iloc[0] if not sub['host_category'].mode().empty else 'N/A',
            'avg_reviews_per_month': sub['reviews_per_month'].mean(),
        }

    return {'nb1': stats_for(nb1), 'nb2': stats_for(nb2),
            'nb1_name': nb1, 'nb2_name': nb2}


def calculate_roi(price_per_night, occupancy_pct, num_listings=1, room_type='Entire home/apt'):
    """ROI projection calculator."""
    listings = LISTINGS_DF
    if listings.empty: return {}

    booked_days = 365 * (occupancy_pct / 100)
    annual_revenue = price_per_night * booked_days * num_listings
    monthly_revenue = annual_revenue / 12

    # Market benchmarks
    market = listings[listings['room_type'] == room_type]
    market_avg_price = market['price'].mean() if not market.empty else 0
    market_avg_occupancy = market['occupancy_pct'].mean() if not market.empty else 0
    market_avg_revenue = market['est_annual_revenue'].mean() if not market.empty else 0

    price_vs_market = ((price_per_night - market_avg_price) / market_avg_price * 100) if market_avg_price else 0
    revenue_vs_market = ((annual_revenue - market_avg_revenue) / market_avg_revenue * 100) if market_avg_revenue else 0

    return {
        'annual_revenue': annual_revenue,
        'monthly_revenue': monthly_revenue,
        'booked_days': booked_days,
        'market_avg_price': market_avg_price,
        'market_avg_occupancy': market_avg_occupancy,
        'market_avg_revenue': market_avg_revenue,
        'price_vs_market_pct': price_vs_market,
        'revenue_vs_market_pct': revenue_vs_market,
    }


# ═══════════════════════════════════════════════════════
#  PLACEHOLDER GRAPH COMPONENTS (for layout.py)
# ═══════════════════════════════════════════════════════

def get_minimum_nights_chart(selected_neighbourhood=None):
    """Histogram of minimum nights — policy barrier analysis."""
    listings = LISTINGS_DF
    if listings.empty: return {}
    df = listings.copy()
    title_suffix = " — All Listings"
    if selected_neighbourhood and selected_neighbourhood != 'All':
        df = df[df['neighbourhood'] == selected_neighbourhood]
        title_suffix = f" — {selected_neighbourhood}"

    # Cap at 30 for readability
    df_plot = df[df['minimum_nights'] <= 30]

    fig = px.histogram(
        df_plot, x='minimum_nights', nbins=30, color='room_type',
        color_discrete_map=ROOM_TYPE_COLORS,
        title=f'Minimum Nights Policy Distribution{title_suffix}',
        labels={'minimum_nights': 'Minimum Nights Required', 'count': 'Number of Listings'},
        barmode='stack'
    )
    fig.update_layout(
        height=400, margin=dict(l=20, r=20, t=50, b=20),
        font=dict(size=11), title_font_size=16,
        legend=dict(title_text="Room Type", orientation="h", y=1.12)
    )
    return fig


def get_license_compliance_chart():
    """License compliance rate by neighbourhood."""
    listings = LISTINGS_DF
    if listings.empty: return {}

    license_by_area = listings.groupby('neighbourhood', observed=False)['license_status'].value_counts().unstack(fill_value=0)
    license_by_area['compliance_pct'] = (
        license_by_area.get('Licensed', 0) /
        (license_by_area.get('Licensed', 0) + license_by_area.get('Unlicensed', 0)) * 100
    ).round(1)
    license_by_area = license_by_area.sort_values('compliance_pct', ascending=True).reset_index()

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=license_by_area['neighbourhood'], x=license_by_area.get('Licensed', [0]*len(license_by_area)),
        name='Licensed', orientation='h', marker_color='#2ca02c',
        text=license_by_area.get('Licensed', [0]*len(license_by_area)),
        textposition='inside'
    ))
    fig.add_trace(go.Bar(
        y=license_by_area['neighbourhood'], x=license_by_area.get('Unlicensed', [0]*len(license_by_area)),
        name='Unlicensed', orientation='h', marker_color='#d62728',
        text=license_by_area.get('Unlicensed', [0]*len(license_by_area)),
        textposition='inside'
    ))
    fig.update_layout(
        title='License Compliance: Registered vs Unregistered Listings by Neighbourhood',
        barmode='stack', height=max(400, len(license_by_area) * 25),
        margin=dict(l=20, r=20, t=50, b=20),
        xaxis_title='Number of Listings', yaxis_title='',
        font=dict(size=11), title_font_size=16,
        legend=dict(title_text="Status", orientation="h", y=1.12)
    )
    return fig


def get_occupancy_timeline():
    """Simulated occupancy timeline — calendar heatmap concept."""
    listings = LISTINGS_DF
    if listings.empty: return {}

    # Create neighbourhood-level occupancy summary
    occ_summary = listings.groupby('neighbourhood').agg(
        avg_occupancy=('occupancy_pct', 'mean'),
        avg_price=('price', 'mean'),
        listing_count=('id', 'count'),
        avg_booked_days=('booked_days', 'mean')
    ).reset_index().sort_values('avg_occupancy', ascending=False)

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(
        go.Bar(
            x=occ_summary['neighbourhood'], y=occ_summary['avg_occupancy'],
            name='Avg. Occupancy %', marker_color=BI_COLOR[4],
            text=occ_summary['avg_occupancy'].round(1), textposition='outside'
        ),
        secondary_y=False
    )
    fig.add_trace(
        go.Scatter(
            x=occ_summary['neighbourhood'], y=occ_summary['avg_price'],
            name='Avg. Price (€)', mode='lines+markers',
            marker=dict(color=WARN, size=8), line=dict(width=2)
        ),
        secondary_y=True
    )

    fig.update_layout(
        title='Occupancy vs Price: Revenue Optimization Landscape',
        height=450, margin=dict(l=20, r=20, t=50, b=100),
        font=dict(size=11), title_font_size=16,
        legend=dict(orientation="h", y=1.12),
        xaxis_tickangle=-45
    )
    fig.update_yaxes(title_text="Avg. Occupancy (%)", secondary_y=False)
    fig.update_yaxes(title_text="Avg. Price (€)", secondary_y=True, tickprefix='€')
    return fig


def get_kpi_metrics():
    """Return KPI summary statistics for the BI dashboard header."""
    listings = LISTINGS_DF
    if listings.empty: return {}

    total_listings = len(listings)
    avg_price = listings['price'].mean()
    avg_occupancy = listings['occupancy_pct'].mean()
    total_est_revenue = listings['est_annual_revenue'].sum()
    entire_home_pct = (listings['room_type'] == 'Entire home/apt').mean() * 100
    licensed_pct = (listings['license_status'] == 'Licensed').mean() * 100

    return {
        'total_listings': f"{total_listings:,}",
        'avg_price': f"€{avg_price:.0f}",
        'avg_occupancy': f"{avg_occupancy:.1f}%",
        'total_est_revenue': f"€{total_est_revenue:,.0f}",
        'entire_home_pct': f"{entire_home_pct:.1f}%",
        'licensed_pct': f"{licensed_pct:.1f}%",
    }


# ═══════════════════════════════════════════════════════
#  STRATEGIC INTELLIGENCE LAYER
# ═══════════════════════════════════════════════════════

def get_market_surveillance():
    """Compute volatility, anomaly, and concentration metrics per neighbourhood."""
    listings = LISTINGS_DF
    if listings.empty: return pd.DataFrame()

    surv = listings.groupby('neighbourhood').agg(
        listing_count=('id', 'count'),
        avg_price=('price', 'mean'),
        price_std=('price', 'std'),
        price_cv=('price', lambda x: (x.std() / x.mean() * 100) if x.mean() > 0 else 0),
        avg_occupancy=('occupancy_pct', 'mean'),
        occupancy_std=('occupancy_pct', 'std'),
        avg_revenue=('est_annual_revenue', 'mean'),
        total_revenue=('est_annual_revenue', 'sum'),
        entire_home_pct=('room_type', lambda x: (x == 'Entire home/apt').mean() * 100),
        licensed_pct=('license_status', lambda x: (x == 'Licensed').mean() * 100),
        professional_host_pct=('host_category', lambda x: (x == 'Professional (6+)').mean() * 100),
        avg_reviews=('reviews_per_month', 'mean'),
        avg_min_nights=('minimum_nights', 'mean'),
    ).reset_index()

    surv['hhi'] = 0.0
    for nb in surv['neighbourhood']:
        sub = listings[listings['neighbourhood'] == nb]
        if not sub.empty:
            shares = sub['est_annual_revenue'] / sub['est_annual_revenue'].sum()
            surv.loc[surv['neighbourhood'] == nb, 'hhi'] = (shares ** 2).sum() * 10000

    surv['occupancy_z'] = (surv['avg_occupancy'] - surv['avg_occupancy'].mean()) / surv['avg_occupancy'].std()
    surv['price_z'] = (surv['avg_price'] - surv['avg_price'].mean()) / surv['avg_price'].std()

    surv['risk_score'] = (
        surv['entire_home_pct'].rank(pct=True) * 30 +
        (100 - surv['licensed_pct']).rank(pct=True) * 25 +
        surv['professional_host_pct'].rank(pct=True) * 20 +
        surv['price_cv'].rank(pct=True) * 15 +
        surv['avg_min_nights'].rank(pct=True) * 10
    ).round(0)

    surv['opportunity_score'] = (
        surv['avg_occupancy'].rank(pct=True) * 30 +
        surv['avg_reviews'].rank(pct=True) * 25 +
        surv['avg_revenue'].rank(pct=True) * 20 +
        surv['listing_count'].rank(pct=True) * 15 +
        surv['licensed_pct'].rank(pct=True) * 10
    ).round(0)

    surv['risk_category'] = pd.cut(surv['risk_score'], bins=[0, 30, 55, 75, 100],
                                    labels=['Low Risk', 'Moderate', 'Elevated', 'High Risk'])
    return surv


def get_risk_opportunity_matrix_chart():
    surv = get_market_surveillance()
    if surv.empty: return {}
    fig = px.scatter(
        surv, x='risk_score', y='opportunity_score', size='listing_count',
        color='risk_category', hover_name='neighbourhood', text='neighbourhood',
        title='Strategic Positioning Matrix: Risk vs Opportunity by Neighbourhood',
        color_discrete_map={'Low Risk': '#2ca02c', 'Moderate': '#ff7f0e',
                            'Elevated': '#d62728', 'High Risk': '#8b0000'},
        size_max=50,
    )
    fig.add_hline(y=50, line_dash="dash", line_color="gray", opacity=0.4)
    fig.add_vline(x=55, line_dash="dash", line_color="gray", opacity=0.4)
    fig.update_traces(textposition='top center', textfont=dict(size=9))
    fig.update_layout(height=550, margin=dict(l=20, r=20, t=50, b=20),
                      font=dict(size=11), title_font_size=16)
    return fig


def get_price_volatility_chart():
    surv = get_market_surveillance()
    if surv.empty: return {}
    df = surv.sort_values('price_cv', ascending=True)
    colors = ['#2ca02c' if v < 30 else '#ff7f0e' if v < 50 else '#d62728' for v in df['price_cv']]
    fig = go.Figure(go.Bar(y=df['neighbourhood'], x=df['price_cv'], orientation='h',
                            marker_color=colors, text=df['price_cv'].round(1), textposition='outside'))
    fig.update_layout(title='Price Volatility Index (CV%) — Lower = More Stable',
                      height=max(400, len(df)*25), margin=dict(l=20, r=50, t=50, b=20),
                      xaxis_title='Price CV (%)', font=dict(size=11), title_font_size=16)
    return fig


def get_market_concentration_chart():
    surv = get_market_surveillance()
    if surv.empty: return {}
    df = surv.sort_values('hhi', ascending=True)
    colors = ['#2ca02c' if v < 1500 else '#ff7f0e' if v < 2500 else '#d62728' for v in df['hhi']]
    fig = go.Figure(go.Bar(y=df['neighbourhood'], x=df['hhi'], orientation='h',
                            marker_color=colors, text=df['hhi'].round(0), textposition='outside'))
    fig.add_vline(x=1500, line_dash="dash", line_color="gray", opacity=0.5)
    fig.add_vline(x=2500, line_dash="dash", line_color="red", opacity=0.5)
    fig.update_layout(title='Market Concentration (HHI) — Higher = Revenue Controlled by Fewer Hosts',
                      height=max(400, len(df)*25), margin=dict(l=20, r=50, t=50, b=20),
                      xaxis_title='Herfindahl-Hirschman Index', font=dict(size=11), title_font_size=16)
    return fig


def get_early_warnings():
    surv = get_market_surveillance()
    if surv.empty: return []
    warnings = []
    for _, row in surv[surv['risk_score'] >= 75].iterrows():
        warnings.append({'level': '🔴 HIGH', 'neighbourhood': row['neighbourhood'],
                         'message': f"Risk {row['risk_score']:.0f}/100 — {row['entire_home_pct']:.0f}% entire homes, {row['licensed_pct']:.0f}% licensed"})
    for _, row in surv[(surv['occupancy_z'] < -0.8) & (surv['listing_count'] > surv['listing_count'].median())].iterrows():
        warnings.append({'level': '🟠 MEDIUM', 'neighbourhood': row['neighbourhood'],
                         'message': f"Occupancy {row['avg_occupancy']:.0f}% is {row['occupancy_z']:.1f}σ below avg — oversupply risk"})
    for _, row in surv[surv['price_z'] > 1.5].iterrows():
        warnings.append({'level': '🟡 INFO', 'neighbourhood': row['neighbourhood'],
                         'message': f"Price €{row['avg_price']:.0f} is {row['price_z']:.1f}σ above avg — potential overheating"})
    for _, row in surv[surv['licensed_pct'] < 40].iterrows():
        warnings.append({'level': '🔴 HIGH', 'neighbourhood': row['neighbourhood'],
                         'message': f"Only {row['licensed_pct']:.0f}% licensed — regulatory exposure"})
    return sorted(warnings, key=lambda w: {'🔴 HIGH':0,'🟠 MEDIUM':1,'🟡 INFO':2}[w['level']])[:12]


def generate_market_briefing():
    listings = LISTINGS_DF
    surv = get_market_surveillance()
    if listings.empty or surv.empty: return "Data unavailable."
    kpi = get_kpi_metrics()
    top_occ = surv.nlargest(3, 'avg_occupancy')
    top_risk = surv.nlargest(3, 'risk_score')
    top_opp = surv.nlargest(3, 'opportunity_score')
    low_c = surv.nsmallest(3, 'licensed_pct')
    return f"""
### 📊 Amsterdam Market Intelligence Briefing

**Market Snapshot:** {kpi.get('total_listings','N/A')} active listings across {len(surv)} neighbourhoods,
avg. nightly rate {kpi.get('avg_price','N/A')}, {kpi.get('avg_occupancy','N/A')} occupancy.

#### 🔥 Demand Hotspots
**{top_occ.iloc[0]['neighbourhood']}** ({top_occ.iloc[0]['avg_occupancy']:.0f}% occ.),
**{top_occ.iloc[1]['neighbourhood']}** ({top_occ.iloc[1]['avg_occupancy']:.0f}%),
**{top_occ.iloc[2]['neighbourhood']}** ({top_occ.iloc[2]['avg_occupancy']:.0f}%) —
monitor for supply saturation.

#### ⚠️ Regulatory Risk
**{low_c.iloc[0]['neighbourhood']}** has only **{low_c.iloc[0]['licensed_pct']:.0f}%** compliance —
highest intervention probability. Top risk: **{top_risk.iloc[0]['neighbourhood']}**
({top_risk.iloc[0]['risk_score']:.0f}/100), **{top_risk.iloc[1]['neighbourhood']}**
({top_risk.iloc[1]['risk_score']:.0f}/100), **{top_risk.iloc[2]['neighbourhood']}**
({top_risk.iloc[2]['risk_score']:.0f}/100).

#### 💡 Opportunities
Prime entry: **{top_opp.iloc[0]['neighbourhood']}** (Score: {top_opp.iloc[0]['opportunity_score']:.0f}/100),
**{top_opp.iloc[1]['neighbourhood']}** ({top_opp.iloc[1]['opportunity_score']:.0f}/100),
**{top_opp.iloc[2]['neighbourhood']}** ({top_opp.iloc[2]['opportunity_score']:.0f}/100).

#### 🎯 Recommended Actions
1. **Immediate:** Audit {low_c.iloc[0]['neighbourhood']} for license gaps
2. **Short-term:** Reposition pricing in {top_occ.iloc[0]['neighbourhood']} as occupancy peaks
3. **Strategic:** Evaluate entry into {top_opp.iloc[0]['neighbourhood']}
"""


def get_stakeholder_network_chart():
    listings = LISTINGS_DF
    if listings.empty: return {}
    tree = listings.groupby(['host_category', 'neighbourhood'], observed=False).agg(
        total_revenue=('est_annual_revenue', 'sum'),
        listing_count=('id', 'count'), avg_price=('price', 'mean'),
    ).reset_index()
    fig = px.sunburst(tree, path=['host_category', 'neighbourhood'], values='total_revenue',
                      color='avg_price', color_continuous_scale='RdYlGn',
                      hover_data={'listing_count': True, 'total_revenue': ':.0f', 'avg_price': ':.0f'},
                      title='Stakeholder Influence: Host Type → Neighbourhood → Revenue Share')
    fig.update_layout(height=550, margin=dict(l=20, r=20, t=50, b=20),
                      font=dict(size=11), title_font_size=16)
    return fig


def get_professionalization_chart():
    listings = LISTINGS_DF
    if listings.empty: return {}
    prof = listings.groupby('neighbourhood', observed=False)['host_category'].value_counts().unstack(fill_value=0)
    prof_pct = prof.div(prof.sum(axis=1), axis=0) * 100
    prof_pct = prof_pct.sort_values('Professional (6+)', ascending=True)
    fig = go.Figure()
    for cat, color in HOST_CATEGORY_COLORS.items():
        if cat in prof_pct.columns:
            fig.add_trace(go.Bar(y=prof_pct.index, x=prof_pct[cat], name=cat,
                                 orientation='h', marker_color=color,
                                 text=prof_pct[cat].round(0).astype(str)+'%'))
    fig.update_layout(title='Host Professionalization by Neighbourhood (% of Listings)',
                      barmode='stack', height=max(400, len(prof_pct)*25),
                      margin=dict(l=20, r=20, t=50, b=20),
                      xaxis_title='Share of Listings (%)', font=dict(size=11), title_font_size=16,
                      legend=dict(title_text="Host Category", orientation="h", y=1.12))
    return fig


# ── Strategic Intelligence Placeholders ────────────────
def get_risk_opportunity_component():
    return dcc.Graph(id="strat-risk-opportunity", figure=get_risk_opportunity_matrix_chart(), style={'height':'570px'})
def get_price_volatility_component():
    return dcc.Graph(id="strat-volatility", figure=get_price_volatility_chart(), style={'height':'450px'})
def get_market_concentration_component():
    return dcc.Graph(id="strat-concentration", figure=get_market_concentration_chart(), style={'height':'450px'})
def get_stakeholder_network_component():
    return dcc.Graph(id="strat-stakeholder-network", figure=get_stakeholder_network_chart(), style={'height':'570px'})
def get_professionalization_component():
    return dcc.Graph(id="strat-professionalization", figure=get_professionalization_chart(), style={'height':'450px'})


# ═══════════════════════════════════════════════════════
#  SWOT ANALYSIS ENGINE
# ═══════════════════════════════════════════════════════

def get_swot_analysis():
    """Compute data-driven SWOT: Strengths, Weaknesses, Opportunities, Threats."""
    listings = LISTINGS_DF
    surv = get_market_surveillance()
    if listings.empty or surv.empty: return {}

    kpi = get_kpi_metrics()
    avg_occ = listings['occupancy_pct'].mean()
    avg_rev = listings['est_annual_revenue'].mean()
    entire_pct = (listings['room_type'] == 'Entire home/apt').mean() * 100
    licensed_pct = (listings['license_status'] == 'Licensed').mean() * 100

    # Top/bottom performers
    top_occ_nb = surv.nlargest(1, 'avg_occupancy').iloc[0]
    top_rev_nb = surv.nlargest(1, 'avg_revenue').iloc[0]
    low_compliance_nb = surv.nsmallest(1, 'licensed_pct').iloc[0]
    high_risk_nb = surv.nlargest(1, 'risk_score').iloc[0]
    top_opp_nb = surv.nlargest(1, 'opportunity_score').iloc[0]

    # Professional host share
    pro_pct = (listings['host_category'] == 'Professional (6+)').mean() * 100

    return {
        'strengths': [
            f"High average occupancy ({avg_occ:.0f}%) across all neighbourhoods — strong demand fundamentals",
            f"Dominant entire-home segment ({entire_pct:.0f}%) — premium positioning attracts high-value guests",
            f"Top neighbourhood {top_occ_nb['neighbourhood']} achieves {top_occ_nb['avg_occupancy']:.0f}% occupancy — proven revenue engine",
            f"Professional hosts ({pro_pct:.0f}% of listings) drive operational excellence at scale",
        ],
        'weaknesses': [
            f"License compliance at only {licensed_pct:.0f}% — significant regulatory vulnerability",
            f"{low_compliance_nb['neighbourhood']} has just {low_compliance_nb['licensed_pct']:.0f}% compliance — concentrated enforcement risk",
            f"High entire-home share ({entire_pct:.0f}%) creates housing displacement narrative — reputational exposure",
            f"Price volatility (CV) exceeds 40% in {(surv['price_cv'] > 40).sum()} neighbourhoods — inconsistent guest experience",
        ],
        'opportunities': [
            f"Prime expansion zone: {top_opp_nb['neighbourhood']} (Opportunity Score {top_opp_nb['opportunity_score']:.0f}/100)",
            f"License gap represents {100-licensed_pct:.0f}% unlockable inventory through compliance programs",
            f"Growing demand in {(surv['avg_reviews'] > surv['avg_reviews'].median()).sum()} neighbourhoods — first-mover advantage",
            f"Private room segment underrepresented — differentiation opportunity vs. entire-home saturation",
        ],
        'threats': [
            f"Amsterdam 30-night annual cap threatens {(listings['minimum_nights'] < 3).sum()} short-stay listings",
            f"Professional operators ({pro_pct:.0f}%) face increased regulatory scrutiny — EU Digital Services Act",
            f"High-risk neighbourhoods: {high_risk_nb['neighbourhood']} (Risk Score {high_risk_nb['risk_score']:.0f}/100)",
            f"Market concentration (HHI > 2500) in {(surv['hhi'] > 2500).sum()} areas — antitrust exposure",
        ],
        'metrics': {
            'avg_occ': f"{avg_occ:.0f}%", 'avg_rev': f"€{avg_rev:,.0f}",
            'entire_pct': f"{entire_pct:.0f}%", 'licensed_pct': f"{licensed_pct:.0f}%",
            'risk_areas': f"{(surv['risk_score'] > 55).sum()}/{len(surv)}",
            'opp_areas': f"{(surv['opportunity_score'] > 55).sum()}/{len(surv)}",
        }
    }


# ═══════════════════════════════════════════════════════
#  EXECUTIVE DASHBOARD CHARTS
# ═══════════════════════════════════════════════════════

def get_revenue_waterfall_chart():
    """Waterfall: Revenue breakdown by room type with contribution %."""
    listings = LISTINGS_DF
    if listings.empty: return {}
    rev = listings.groupby('room_type', observed=False)['est_annual_revenue'].sum().sort_values(ascending=False)
    total = rev.sum()
    fig = go.Figure(go.Waterfall(
        name="Revenue", orientation="v",
        measure=["relative"] * len(rev) + ["total"],
        x=list(rev.index) + ["Total"],
        y=list(rev.values) + [0],
        text=[f"€{v:,.0f}<br>({v/total*100:.1f}%)" for v in rev.values] + [f"€{total:,.0f}"],
        connector={"line": {"color": "rgba(255,255,255,0.2)"}},
        decreasing={"marker": {"color": ROOM_TYPE_COLORS.get(list(rev.index)[-1], '#d62728')}},
    ))
    fig.update_layout(title='Revenue Waterfall by Room Type', height=400,
                      margin=dict(l=20, r=20, t=50, b=20), font=dict(size=11), title_font_size=16)
    return fig


def get_market_coverage_chart():
    """Market coverage: % of neighbourhoods where Airbnb has significant presence."""
    listings = LISTINGS_DF
    surv = get_market_surveillance()
    if listings.empty or surv.empty: return {}

    surv['coverage_tier'] = pd.cut(surv['listing_count'], bins=[0, 50, 200, 500, 9999],
                                    labels=['Low (<50)', 'Medium (50-200)', 'High (200-500)', 'Dominant (500+)'])
    coverage = surv['coverage_tier'].value_counts().reset_index()
    coverage.columns = ['Coverage Tier', 'Count']

    colors = {'Dominant (500+)': '#2ca02c', 'High (200-500)': '#1f77b4',
              'Medium (50-200)': '#ff7f0e', 'Low (<50)': '#d62728'}

    fig = px.pie(coverage, values='Count', names='Coverage Tier',
                 title='Market Coverage: Neighbourhood Penetration Tiers',
                 color='Coverage Tier', color_discrete_map=colors, hole=0.5)
    fig.update_traces(textinfo='percent+label')
    fig.update_layout(height=350, margin=dict(l=20, r=20, t=50, b=20),
                      font=dict(size=11), title_font_size=16)
    return fig


# ═══════════════════════════════════════════════════════
#  REVENUE OPTIMIZATION CHARTS
# ═══════════════════════════════════════════════════════

def get_revenue_leakage_chart():
    """Detect underpriced listings: listings priced below neighbourhood median."""
    listings = LISTINGS_DF
    if listings.empty: return {}
    medians = listings.groupby('neighbourhood', observed=False)['price'].median()
    listings_copy = listings.copy()
    listings_copy['area_median'] = listings_copy['neighbourhood'].map(medians)
    listings_copy['price_gap_pct'] = ((listings_copy['area_median'] - listings_copy['price']) /
                                       listings_copy['area_median'] * 100)
    leakage = listings_copy[listings_copy['price_gap_pct'] > 20].groupby('neighbourhood').agg(
        underpriced_count=('id', 'count'),
        avg_gap_pct=('price_gap_pct', 'mean'),
        potential_revenue=('price_gap_pct', lambda x: (x / 100 * listings_copy.loc[x.index, 'price'] * listings_copy.loc[x.index, 'booked_days']).sum())
    ).sort_values('potential_revenue', ascending=False).head(12).reset_index()

    if leakage.empty: return {}

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=leakage['neighbourhood'], x=leakage['underpriced_count'],
        name='Underpriced Listings', orientation='h', marker_color='#f87171',
        text=leakage['underpriced_count'], textposition='outside',
    ))
    fig.add_trace(go.Scatter(
        y=leakage['neighbourhood'], x=leakage['avg_gap_pct'],
        name='Avg Price Gap %', mode='lines+markers', marker=dict(color='#fbbf24', size=10),
        yaxis='y2', line=dict(width=2),
    ))
    fig.update_layout(
        title='Revenue Leakage Detection: Underpriced Listings by Neighbourhood',
        height=450, margin=dict(l=20, r=70, t=50, b=20), font=dict(size=11), title_font_size=16,
        xaxis=dict(title='Number of Underpriced Listings'),
        xaxis2=dict(title='Avg Price Gap (%)', overlaying='x', side='top', range=[0, 60]),
        legend=dict(orientation="h", y=1.12),
    )
    return fig


def get_pricing_optimization_chart():
    """Room-type pricing recommendations with ideal range."""
    listings = LISTINGS_DF
    if listings.empty: return {}
    room_types = listings['room_type'].unique()
    fig = go.Figure()
    for i, rt in enumerate(room_types):
        sub = listings[listings['room_type'] == rt]['price']
        if sub.empty: continue
        p25, p50, p75 = sub.quantile(0.25), sub.quantile(0.50), sub.quantile(0.75)
        fig.add_trace(go.Bar(
            name=rt, x=['Recommended Range'], y=[p75 - p25],
            base=p25, marker_color=list(ROOM_TYPE_COLORS.values())[i],
            text=[f"€{p25:.0f} – €{p75:.0f}"], textposition='inside',
            width=0.4,
        ))
        fig.add_trace(go.Scatter(
            name=f"{rt} Median", x=['Recommended Range'], y=[p50],
            mode='markers', marker=dict(color='white', size=14, symbol='diamond', line=dict(width=2)),
            showlegend=False,
        ))
    fig.update_layout(
        title='Optimal Pricing Ranges by Room Type (IQR Method)',
        height=350, barmode='stack', margin=dict(l=20, r=20, t=50, b=20),
        font=dict(size=11), title_font_size=16, yaxis_tickprefix='€',
        legend=dict(orientation="h", y=1.12),
    )
    return fig


# ═══════════════════════════════════════════════════════
#  HOST GROWTH CHARTS
# ═══════════════════════════════════════════════════════

def get_host_acquisition_targets_chart():
    """Neighbourhoods with high demand, low supply — acquisition priority."""
    surv = get_market_surveillance()
    if surv.empty: return {}
    surv['acquisition_score'] = (
        surv['avg_reviews'].rank(pct=True) * 0.4 +
        surv['avg_occupancy'].rank(pct=True) * 0.35 +
        (1 - surv['listing_count'].rank(pct=True)) * 0.25
    )
    targets = surv.nlargest(10, 'acquisition_score').sort_values('acquisition_score', ascending=True)

    fig = go.Figure(go.Bar(
        y=targets['neighbourhood'], x=targets['acquisition_score'],
        orientation='h', marker=dict(
            color=targets['acquisition_score'], colorscale='Teal', showscale=False
        ),
        text=targets['acquisition_score'].round(2), textposition='outside',
    ))
    fig.update_layout(
        title='Host Acquisition Priority: High Demand, Low Supply Areas',
        height=380, margin=dict(l=20, r=50, t=50, b=20),
        xaxis_title='Acquisition Score (higher = more urgent)', font=dict(size=11), title_font_size=16,
    )
    return fig


def get_host_quality_chart():
    """Host quality distribution: Superhost potential pipeline."""
    listings = LISTINGS_DF
    if listings.empty: return {}
    bins = [0, 1, 5, 20, 50, float('inf')]
    labels = ['New (0-1)', 'Rising (2-5)', 'Established (6-20)', 'Veteran (21-50)', 'Superhost (50+)']
    listings['review_bucket'] = pd.cut(listings['number_of_reviews'], bins=bins, labels=labels)

    quality = listings.groupby('review_bucket', observed=False).agg(
        count=('id', 'count'), avg_occupancy=('occupancy_pct', 'mean'),
        avg_price=('price', 'mean'),
    ).reset_index()

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(x=quality['review_bucket'], y=quality['count'],
                         name='Hosts', marker_color=BI_COLOR[4],
                         text=quality['count'], textposition='outside'), secondary_y=False)
    fig.add_trace(go.Scatter(x=quality['review_bucket'], y=quality['avg_occupancy'],
                             name='Avg Occupancy %', mode='lines+markers',
                             marker=dict(color=WARN, size=10), line=dict(width=3)), secondary_y=True)
    fig.update_layout(title='Host Quality Pipeline: Reviews → Occupancy Correlation',
                      height=380, margin=dict(l=20, r=20, t=50, b=20),
                      font=dict(size=11), title_font_size=16,
                      legend=dict(orientation="h", y=1.12))
    fig.update_yaxes(title_text="Number of Hosts", secondary_y=False)
    fig.update_yaxes(title_text="Avg Occupancy (%)", secondary_y=True)
    return fig


# ═══════════════════════════════════════════════════════
#  TRUST & SAFETY CHARTS
# ═══════════════════════════════════════════════════════

def get_trust_risk_matrix_chart():
    """Risk matrix: Unlicensed + Low reviews = trust risk."""
    listings = LISTINGS_DF
    surv = get_market_surveillance()
    if listings.empty or surv.empty: return {}

    risk_df = surv[['neighbourhood', 'licensed_pct', 'professional_host_pct', 'avg_reviews', 'listing_count']].copy()
    risk_df['trust_score'] = (
        risk_df['licensed_pct'].rank(pct=True) * 0.4 +
        (1 - risk_df['professional_host_pct'].rank(pct=True)) * 0.3 +
        risk_df['avg_reviews'].rank(pct=True) * 0.3
    ).round(0)

    fig = px.scatter(
        risk_df, x='licensed_pct', y='avg_reviews', size='listing_count',
        color='trust_score', hover_name='neighbourhood', text='neighbourhood',
        title='Trust & Safety Risk Matrix: License Compliance vs Guest Activity',
        labels={'licensed_pct': 'License Compliance (%)', 'avg_reviews': 'Avg Reviews/Month',
                'trust_score': 'Trust Score'},
        color_continuous_scale='RdYlGn', size_max=45,
    )
    fig.add_hline(y=risk_df['avg_reviews'].median(), line_dash="dash", line_color="gray", opacity=0.5)
    fig.add_vline(x=50, line_dash="dash", line_color="red", opacity=0.4)
    fig.update_traces(textposition='top center', textfont=dict(size=9))
    fig.update_layout(height=450, margin=dict(l=20, r=20, t=50, b=20),
                      font=dict(size=11), title_font_size=16)
    return fig


def get_guest_experience_chart():
    """Minimum nights + review velocity as guest satisfaction proxy."""
    listings = LISTINGS_DF
    if listings.empty: return {}
    df = listings[listings['minimum_nights'] <= 14].copy()
    exp = df.groupby('minimum_nights', observed=False).agg(
        listings=('id', 'count'), avg_reviews=('reviews_per_month', 'mean'),
        avg_price=('price', 'mean'),
    ).reset_index()

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(x=exp['minimum_nights'], y=exp['listings'],
                         name='Listings', marker_color=BI_COLOR[4]), secondary_y=False)
    fig.add_trace(go.Scatter(x=exp['minimum_nights'], y=exp['avg_reviews'],
                             name='Avg Reviews/Mo', mode='lines+markers',
                             marker=dict(size=8), line=dict(width=3, color=WARN)), secondary_y=True)
    fig.update_layout(title='Guest Experience: Minimum Nights vs Review Activity',
                      height=380, margin=dict(l=20, r=20, t=50, b=20),
                      font=dict(size=11), title_font_size=16,
                      legend=dict(orientation="h", y=1.12),
                      xaxis=dict(title='Minimum Nights', dtick=1))
    fig.update_yaxes(title_text="Number of Listings", secondary_y=False)
    fig.update_yaxes(title_text="Avg Reviews/Month", secondary_y=True)
    return fig


# ═══════════════════════════════════════════════════════
#  ROLE-BASED PLACEHOLDER COMPONENTS
# ═══════════════════════════════════════════════════════

def get_revenue_waterfall_component():
    return dcc.Graph(id="exec-waterfall", figure=get_revenue_waterfall_chart(), style={'height':'420px'})
def get_market_coverage_component():
    return dcc.Graph(id="exec-coverage", figure=get_market_coverage_chart(), style={'height':'370px'})
def get_revenue_leakage_component():
    return dcc.Graph(id="rev-leakage", figure=get_revenue_leakage_chart(), style={'height':'470px'})
def get_pricing_optimization_component():
    return dcc.Graph(id="rev-pricing-opt", figure=get_pricing_optimization_chart(), style={'height':'370px'})
def get_host_acquisition_component():
    return dcc.Graph(id="host-acquisition", figure=get_host_acquisition_targets_chart(), style={'height':'400px'})
def get_host_quality_component():
    return dcc.Graph(id="host-quality", figure=get_host_quality_chart(), style={'height':'400px'})
def get_trust_risk_component():
    return dcc.Graph(id="trust-risk", figure=get_trust_risk_matrix_chart(), style={'height':'470px'})
def get_guest_experience_component():
    return dcc.Graph(id="trust-guest-exp", figure=get_guest_experience_chart(), style={'height':'400px'})


# ═══════════════════════════════════════════════════════
#  PLACEHOLDER GRAPH COMPONENTS (for layout.py)
# ═══════════════════════════════════════════════════════

def _graph(id, figure, height='350px'):
    return dcc.Graph(id=id, figure=figure, style={'height': height})


# ── Tab 1 placeholders ─────────────────────────────────
def get_basic_chart_A():
    return dcc.Graph(id="ex1A-basic-chart-price-dist",
                     figure=get_price_distribution_chart([0, 250]),
                     style={'height': '350px'})

def get_basic_chart_B():
    return dcc.Graph(id="ex1B-basic-chart-room-type",
                     figure=get_room_type_pie_chart(None),
                     style={'height': '350px'})

def get_map_component():
    return dcc.Graph(id="ex3-map-visualization",
                     figure=get_map(None),
                     style={'height': '550px'})

# ── Tab 2 placeholders ─────────────────────────────────
def get_occupancy_component():
    return dcc.Graph(id="bi-occupancy-chart",
                     figure=get_occupancy_chart(None),
                     style={'height': '450px'})

def get_revenue_box_component():
    return dcc.Graph(id="bi-revenue-box",
                     figure=get_revenue_boxplot(None),
                     style={'height': '420px'})

def get_demand_supply_component():
    return dcc.Graph(id="bi-demand-supply",
                     figure=get_demand_supply_chart(),
                     style={'height': '520px'})

def get_host_concentration_component():
    return dcc.Graph(id="bi-host-concentration",
                     figure=get_host_concentration_chart(None),
                     style={'height': '420px'})

def get_pricing_position_component():
    return dcc.Graph(id="bi-pricing-position",
                     figure=get_pricing_position_chart(),
                     style={'height': '470px'})

def get_rating_price_component():
    return dcc.Graph(id="bi-rating-price",
                     figure=get_rating_price_matrix(),
                     style={'height': '470px'})

def get_revenue_treemap_component():
    return dcc.Graph(id="bi-revenue-treemap",
                     figure=get_revenue_treemap(None),
                     style={'height': '520px'})

# ── Tab 3 placeholders ─────────────────────────────────
def get_min_nights_component():
    return dcc.Graph(id="policy-min-nights",
                     figure=get_minimum_nights_chart(None),
                     style={'height': '420px'})

def get_license_compliance_component():
    return dcc.Graph(id="policy-license",
                     figure=get_license_compliance_chart(),
                     style={'height': '450px'})

def get_occupancy_timeline_component():
    return dcc.Graph(id="policy-occupancy-timeline",
                     figure=get_occupancy_timeline(),
                     style={'height': '470px'})
