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
print(state_summary.filter(pl.col("State") == "CA"))

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
        mapbox_center={"lat": 38.000000, "lon": -90.000000},
        font=dict(
            color="white"
        )
    )

    return fig


# Create the bar chart for severity levels
""" def create_severity_bar_chart():
    severity_counts = df_sampled['Severity'].value_counts().reset_index()
    severity_counts.columns = ['Severity', 'Accident_Count']
    severity_counts = severity_counts.sort_values('Severity')  # Ensure proper order
    fig = px.bar(severity_counts, x='Severity', y='Accident_Count',
                 title='Accidents by Severity',
                 labels={'Accident_Count': 'Number of Accidents'},
                 template='plotly_dark',
                 color_discrete_sequence=['orange'])
    return fig """


# Create the line graph for accidents over time (aggregated by month)
""" def create_accidents_over_month_line_graph():
    # Convert 'Start_Time' to datetime and extract the month
    df_sampled['Month'] = pd.to_datetime(df_sampled['Start_Time'], format='mixed', errors='coerce').dt.to_period('M')
    accidents_over_month = df_sampled.groupby('Month').size().reset_index(name='Accident_Count')

    # Convert 'Month' Period objects to strings for JSON serialization
    accidents_over_month['Month'] = accidents_over_month['Month'].astype(str)

    # Plot the line graph
    fig = px.line(accidents_over_month, x='Month', y='Accident_Count',
                  title='Accidents Over Time (Monthly)',
                  labels={'Accident_Count': 'Number of Accidents', 'Month': 'Month'},
                  template='plotly_dark')
    fig.update_traces(line=dict(color='orange'))  # Set line color to orange
    fig.update_xaxes(title_text='Month', tickangle=45)  # Rotate x-axis labels for readability
    fig.update_yaxes(title_text='Number of Accidents')  # Update y-axis label
    return fig """


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
                                    dcc.Dropdown()
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


""" @app.callback(
    Output('chart-display', 'figure'),
    Input('chart-type-dropdown', 'value')
)
def update_chart(chart_type):
    if chart_type == 'severity_bar':
        return create_severity_bar_chart()
    elif chart_type == 'time_line':
        return create_accidents_over_month_line_graph()  
 """

if __name__ == '__main__':
    app.run_server(debug=True)