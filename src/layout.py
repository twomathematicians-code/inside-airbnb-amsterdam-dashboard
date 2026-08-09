# layout.py
from dash import dcc
import dash_bootstrap_components as dbc
from dash import html
import charts


def get_app_description():
    description_text = '''
        This dashboard utilizes **Inside Airbnb** data for Ghent (2025) to investigate the proliferation of short-term rentals and their potential impact on local housing availability and residential communities. The visualizations focus on **quantifying housing displacement**, analyzing pricing structures, and identifying the spatial concentration of these rentals across the city's neighborhoods.
        '''
    return dcc.Markdown(children=description_text)


def get_data_insights():
    insights = '''
        **Key Insights: Airbnb's Impact on Ghent's Housing Market**

        The analysis reveals critical structural characteristics of the Ghent short-term rental market:

        * **Housing Displacement:** The dominance of **'Entire home/apt'** listings (compared to 'Private room' or 'Shared room') is the most significant finding. These listings directly remove complete housing units from the long-term rental market, quantifying the acute pressure on the city's housing stock.
        * **Pricing Structure:** The majority of listings are priced below **€150 per night**, suggesting a high volume, tourism-focused market that competes directly with budget accommodation.
        * **Spatial Inequality:** The **historic city center** ('Binnenstad' and 'Elisabethbegijnhof - Papegaai') exhibits a vastly disproportionate concentration of listings and the highest average prices (up to ~€250/night). This indicates that the disruptive socio-economic and structural pressure on residential communities is highly localized to the tourist core.

        These findings support the project's mission by providing tangible evidence for targeted policy interventions aimed at protecting the local housing supply.
    '''
    return dcc.Markdown(children=insights)


def get_source_text():
    source_text = '''
    Data from [Inside Airbnb](http://insideairbnb.com/get-the-data.html),
    licensed under [Creative Commons Attribution 4.0 International License](https://creativecommons.org/licenses/by/4.0/).
    '''
    return dcc.Markdown(children=source_text)


def get_master_filter():
    listings = charts.LISTINGS_DF

    neighbourhood_options = [{'label': 'All Neighbourhoods', 'value': 'All'}]
    if not listings.empty:
        unique_neighbourhoods = [{'label': i, 'value': i} for i in sorted(listings['neighbourhood'].unique())]
        neighbourhood_options.extend(unique_neighbourhoods)

    return dbc.Row(
        dbc.Col(
            [
                html.H3("Master Filter: Select Neighbourhood", style={"margin-top": "1em"}),
                html.P(
                    "Use this filter to analyze the Room Type distribution and Map visualization for a specific neighbourhood."),
                dcc.Dropdown(
                    id='master-filter-neighbourhood',  # <-- ID definition is correct
                    options=neighbourhood_options,
                    value='All',  # Default value
                    clearable=False
                ),
                html.Hr()
            ],
            width=6,
        ),
        justify="center"
    )


def get_exercise1_charts():
    listings = charts.LISTINGS_DF
    max_price = int(listings['price'].max()) if not listings.empty and not listings['price'].empty else 500

    row = html.Div(
        [
            dbc.Row(
                dbc.Col(html.H2("Exploratory Data Analysis: Price Structure and Housing Type",
                                style={"margin-top": "1em"})),
            ),
            # Interaction 1 (Price Range Slider for Histogram)
            dbc.Row(
                dbc.Col([
                    html.P("Interaction 1: Filter Listing Price Range (€) for the Histogram:",
                           style={'margin-top': '10px'}),
                    dcc.RangeSlider(
                        id='price-range-slider',
                        min=0,
                        max=min(max_price, 500),
                        step=10,
                        value=[0, 250],
                        marks={i: f'€{i}' for i in range(0, min(max_price, 501), 50)},
                        tooltip={"placement": "bottom", "always_visible": True}
                    ),
                    html.Hr()
                ], width=12),
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            charts.get_basic_chart_A()
                        ],
                    ),
                    dbc.Col(
                        [
                            html.P("Room Type Distribution (Filtered by Master Dropdown):",
                                   style={'margin-top': '10px'}),
                            charts.get_basic_chart_B()
                        ],
                    ),
                ],
            ),
        ]
    )
    return row


def get_exercise3_map():
    return dbc.Row(
        dbc.Col(
            [
                html.H2("Spatial Concentration: Price Inequality and Density Map", style={"margin-top": "1em"}),
                html.P(
                    "Choropleth map visualizing the **Average Daily Price** per neighbourhood, with individual listings overlaid. Listings are filtered by the Master Filter."),

                html.Hr(),
                charts.get_map_component(),
            ],
        )
    )


def get_app_layout():
    return dbc.Container(
        [
            html.H1(children='Inside Airbnb Gent Dashboard: Quantifying Market Impact',
                    style={"margin-top": "1rem"}),
            get_app_description(),

            # --- CRITICAL: Master Filter component must be loaded here! ---
            get_master_filter(),

            get_exercise1_charts(),
            get_exercise3_map(),
            html.H2(children='Conclusion & Evidence for Policy Interventions',
                    style={"margin-top": "1rem"}),
            get_data_insights(),
            dbc.Row(
                [
                    dbc.Col(html.P("Created for the Interactive Data Visualizations Lab (2025)")),
                    dbc.Col(get_source_text(), width="auto")
                ],
                justify="between",
                style={"margin-top": "3rem"}),
        ],
        fluid=False
    )