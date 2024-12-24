import polars as pl
from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import json

app = Dash(
    external_stylesheets=["https://codepen.io/chriddyp/pen/bWLwgP.css"]
)

mapbox_access_token = "pk.eyJ1Ijoiam9uYXN1bnJ1aCIsImEiOiJjbHhhajBxczYxdHZpMmtzYWt6OWp3NGtoIn0._QenClOEROqOMq2h-9kLog"

state_summary = pl.read_parquet("./assets/data/state_level.parquet")

state_summary = state_summary.select(
    pl.col("State"),
    pl.col("accidents").cast(pl.Int32),
    pl.col("avg_severity").cast(pl.Float64)
)

severity_summary = pl.read_parquet("./assets/data/severity_level.parquet")

severity_summary = severity_summary.select(
    pl.col("State"),
    pl.col("Severity").cast(pl.Int32),
    pl.col("len").cast(pl.Int32)
)

monthly_accidents = pl.read_parquet("./assets/data/monthly_accidents.parquet")

monthly_accidents = monthly_accidents.select(
    pl.col("State"),
    pl.col("Month").cast(pl.Date),
    pl.col("accidents").cast(pl.Int32)
)

with open("./assets/data/us-states.json", "r") as f:
    geojson = json.loads(f.read())

# Create the choropleth map to show accidents by state
def create_choropleth_map():
    # Plotly Choropleth map
    fig = px.choropleth_mapbox(
        state_summary, 
        geojson=geojson, 
        featureidkey="id",  # Use the USA-states mode for locations
        locations="State",
        color='accidents',  # The number of accidents
        color_continuous_scale="Viridis",  # Color scale for the choropleth
        opacity=0.3
    )

    fig.update_layout(
        margin={"r":35,"t":0,"l":0,"b":0},
        autosize=True,
        mapbox_accesstoken=mapbox_access_token,
        mapbox_style="dark",
        mapbox_zoom=3,
        mapbox_center={"lat": 38.000000, "lon": -90.000000}
    )

    return fig


# Create the bar chart for severity levels
def create_severity_bar_chart():
    fig = px.bar(severity_summary.filter(pl.col("State") == "All States"), x='Severity', y='len',
                 title='Accidents by Severity',
                 labels={'len': 'Number of Accidents'},
                 template='plotly_dark',
                 color_discrete_sequence=['orange'])
    return fig 


# Create the line graph for accidents over time (aggregated by month)
def create_accidents_over_month_line_graph():
    # Plot the line graph
    fig = px.line(monthly_accidents.filter(pl.col("State") == "All States"), x='Month', y='accidents',
                  title='Accidents Over Time (Monthly)',
                  labels={'accidents': 'Number of Accidents', 'Month': 'Month'},
                  template='plotly_dark')
    fig.update_traces(line=dict(color='orange'))  # Set line color to orange
    fig.update_xaxes(title_text='Month', tickangle=45)  # Rotate x-axis labels for readability
    fig.update_yaxes(title_text='Number of Accidents')  # Update y-axis label
    return fig


app.layout = [
    html.Div(
        children=[
            html.Div(
                className='row',
                children=[
                    # User Controls
                    html.Div(
                        className="four columns div-user-controls",
                        children=[
                            html.H2("Realtime Vis Project"),
                            html.P("Jacopo Rafaeli, Jonas Unruh"),
                            html.Div(
                                className="div-dropdown",
                                children=[
                                    dcc.Dropdown(
                                        id='chart-type-dropdown',
                                        options=[
                                            {'label': 'Severity Bar Chart', 'value': 'severity_bar'},
                                            {'label': 'Accidents Over Time Line Graph', 'value': 'time_line'}
                                        ],
                                        value='severity_bar',  # Default value
                                    )
                                ]
                            )
                        ]
                    ),
                    # Charts
                    html.Div(
                        className="eight columns div-for-charts bg-grey",
                        children=[
                            dcc.Graph(
                                id='accidents-choropleth-map',
                                figure=create_choropleth_map()  # Create the choropleth map when the app starts
                            ),
                            html.Div(
                                className="text-padding",
                                children=[

                                ]
                            ),
                            dcc.Graph(id='chart-display')  # Placeholder for the selected chart
                        ]
                    )
                ]
            )
        ]
    )
]


@app.callback(
    Output('chart-display', 'figure'),
    Input('chart-type-dropdown', 'value')
)
def update_chart(chart_type):
    if chart_type == 'severity_bar':
        return create_severity_bar_chart()
    elif chart_type == 'time_line':
        return create_accidents_over_month_line_graph()  


if __name__ == '__main__':
    app.run_server(debug=True)