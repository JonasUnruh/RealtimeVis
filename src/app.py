import polars as pl
from dash import Dash, dcc, html, Input, Output
import plotly.graph_objects as go
import plotly.express as px
import json
import csv

app = Dash(
    external_stylesheets=["https://codepen.io/chriddyp/pen/bWLwgP.css"]
)

mapbox_access_token = "pk.eyJ1Ijoiam9uYXN1bnJ1aCIsImEiOiJjbHhhajBxczYxdHZpMmtzYWt6OWp3NGtoIn0._QenClOEROqOMq2h-9kLog"

df = pl.read_parquet("./src/assets/data/summary_data.parquet")

df = df.select(
    pl.col("State"),
    pl.col("Year").cast(pl.Int32),
    pl.col("Month").cast(pl.Int32),
    pl.col("accidents").cast(pl.Int32),
    pl.col("avg_severity").cast(pl.Float64),
    pl.col("Severity").cast(pl.Int32),
    pl.col("severity_count").cast(pl.Int32),
    pl.col("Weather_Condition"),
    pl.col("weather_count").cast(pl.Int32)
)

with open("./src/assets/data/us-states.json", "r") as f:
    geojson = json.loads(f.read())

with open("./src/assets/data/counties.geojson", "r") as f:
    county_geojson = json.loads(f.read())

state_lon_lat_dict = {}
with open("./src/assets/data/lat_lon_data.txt", "r") as f:
    reader = csv.reader(f, delimiter=',')
    state_lon_lat_dict = {row[1].strip("'"): (float(row[6]), float(row[7])) for row in reader}

years = range(2016, 2024)
state_dict = {feature["id"]: feature["properties"]["name"] for feature in geojson["features"]}
state_dict.pop("AK")
state_dict.pop("HI")
indicator_dict = {"accidents": "Accidents", "severity_count": "Severity Distribution", "avg_severity": "Average Severity"}
aggregation_functions = {
    'accidents': pl.sum,
    'severity_count': pl.sum,
    'avg_severity': pl.mean,
}


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
                            html.H2("US Accidents Dashboard"),
                            html.P("Jacopo Rafaeli, Jonas Unruh"),
                            html.Div(
                                className="div-dropdown",
                                children=[
                                    dcc.Dropdown(
                                        id="state-dropdown",
                                        options=[
                                            {"label": value, "value": key}
                                            for key, value in state_dict.items()
                                        ],
                                        placeholder="Select State",
                                        clearable=True
                                    )
                                ]
                            ),
                            html.Div(
                                className="div-dropdown",
                                children=[
                                    dcc.Dropdown(
                                        id="year-dropdown",
                                        options=[
                                            {"label": str(year), "value": year}
                                            for year in years
                                        ],
                                        value=2020,
                                        clearable=False
                                    )
                                ]
                            ),
                            html.Div(
                                className="div-dropdown",
                                children=[
                                    dcc.Dropdown(
                                        id='value-selector',
                                        options=[
                                            {"label": value, "value": key}
                                            for key, value in indicator_dict.items()
                                        ],
                                        value='accidents',
                                        clearable=False
                                    )
                                ]
                            ),
                            html.Div(
                                className="div-dropdown",
                                children=[
                                    dcc.Dropdown(
                                        id='severity-selector',
                                        options=[
                                            {"label": value, "value": value}
                                            for value in range(1, 5)
                                        ],
                                        placeholder = "Select a Severity Level",
                                        clearable=True
                                    )
                                ]
                            ),
                        ]
                    ),
                    # Charts
                    html.Div(
                        className="eight columns div-for-charts bg-grey",
                        children=[
                            dcc.Graph(
                                id='accidents-choropleth-map'
                            ),
                            html.Div(
                                className="text-padding",
                                children=[

                                ]
                            ),
                            dcc.Graph(id='chart-display') 
                        ]
                    )
                ]
            )
        ]
    )
]


@app.callback(
    Output("chart-display", "figure"),
    [
        Input("state-dropdown", "value"),
        Input("year-dropdown", "value"),
        Input("value-selector", "value"),
        Input("severity-selector", "value")
    ]
)
def choose_graph_type(selected_state, selected_year, selected_indicator, selected_severity):
    if selected_indicator == 'severity_count':
        return update_bar(selected_state, selected_year, selected_indicator)
    else:
        return update_line(selected_state, selected_year, selected_indicator, selected_severity)


@app.callback(
        [
            Output("state-dropdown", "value"),
            Output("accidents-choropleth-map", "clickData")
        ],
        [
            Input("accidents-choropleth-map", "clickData"),
            Input("state-dropdown", "value")
        ]
)
def update_state_dropdown(clickData, selectedData):
    state = selectedData if selectedData else None
    
    if clickData:
        clicked_state = clickData["points"][0]["location"]
        if clicked_state in state_dict.keys():
            state = clicked_state
        else:
            state = None
            
    return state, None


@app.callback(
        [
            Output("severity-selector", "value"),
            Output("chart-display", "clickData")
        ],
        [
            Input("severity-selector", "value"),
            Input("chart-display", "clickData"),
            Input("value-selector", "value")
        ]
)
def update_severity_dropdown(selectedData, clickData, selected_indicator):
    severity = selectedData if selectedData else None
    
    if selected_indicator == "severity_count":
        if clickData:
            clicked_severity = clickData["points"][0]["label"]
            if clicked_severity == severity:
                severity = None
            else:
                severity = clicked_severity
            
    return severity, None
    

def update_line(selected_state, selected_year, selected_indicator, selected_severity):
    y = selected_indicator
    data = df.filter(
        [pl.col("Year") == selected_year, pl.col("Severity") == selected_severity] if selected_severity else pl.col("Year") == selected_year
    ).unique(
        subset=["State", "Month"]
    ).sort("Month")

    if selected_state:
        data = data.filter(pl.col("State") == selected_state)
    else:
        data = data.filter(pl.col("State") == "USA")

    if selected_severity and selected_indicator == "accidents":
        y = "severity_count"

    fig = px.line(
        data, 
        x='Month', 
        y=y, 
        color='State', 
        markers=True,
        title= indicator_dict[selected_indicator] + " over the year " + str(selected_year) + " in the USA",
        custom_data=["State", selected_indicator]
    )

    fig.update_layout(
        margin=go.layout.Margin(l=10, r=0, t=50, b=50),
        showlegend=False,
        plot_bgcolor="#323130",
        paper_bgcolor="#323130",
        dragmode="select",
        font=dict(color="white"),
        yaxis_title=indicator_dict[selected_indicator],
        xaxis_title="Month"
    )

    fig.update_traces(
        mode = "lines+markers",
        hovertemplate = "State: %{customdata[0]} <br>" + indicator_dict[selected_indicator] + ": %{customdata[1]:.2f} </br><extra></extra>"
    )

    return fig


def update_bar(selected_state, selected_year, selected_indicator):
    data = df.filter(
        pl.col("Year") == selected_year
    ).unique(
        subset=["State", "Severity"]
    ).sort("Severity")

    if selected_state:
        data = data.filter(pl.col("State") == selected_state)
    else:
        data = data.filter(pl.col("State") == "USA")

    fig = px.bar(
        data, 
        x='Severity', 
        y=selected_indicator, 
        title=indicator_dict[selected_indicator] + " over the year " + str(selected_year) + " in the USA",
        custom_data=["State", selected_indicator]
    )

    fig.update_layout(
        margin=go.layout.Margin(l=10, r=0, t=50, b=50),
        showlegend=False,
        plot_bgcolor="#323130",
        paper_bgcolor="#323130",
        font=dict(color="white"),
        yaxis_title=indicator_dict[selected_indicator],
        xaxis_title="Severity"
    )

    return fig


@app.callback(
    Output("accidents-choropleth-map", "figure"),
    [
        Input("state-dropdown", "value"),
        Input("year-dropdown", "value"),
        Input("value-selector", "value"),
        Input("severity-selector", "value")
    ]
)
def update_map(selected_state, selected_year, selected_indicator, selected_severity):
    if selected_indicator == "severity_count":
        selected_indicator = "accidents"

    agg_func = aggregation_functions[selected_indicator]

    if selected_state:        
        df = pl.read_parquet(f"./src/assets/data/{selected_state}_summary_data.parquet")

        df = df.select(
            pl.col("County"),
            pl.col("GEO_ID"),
            pl.col("Year").cast(pl.Int32),
            pl.col("Month").cast(pl.Int32),
            pl.col("accidents").cast(pl.Int32),
            pl.col("avg_severity").cast(pl.Float64),
            pl.col("Severity").cast(pl.Int32),
            pl.col("severity_count").cast(pl.Int32)
        )

        data = df.filter(
            [pl.col("Year") == selected_year, pl.col("Severity") == selected_severity] if selected_severity else pl.col("Year") == selected_year
        ).unique(
            subset=["County", "GEO_ID", "Month"]
        ).group_by(["County", "GEO_ID"]).agg(agg_func(selected_indicator))
    else:
        df = pl.read_parquet("./src/assets/data/summary_data.parquet")

        df = df.select(
            pl.col("State"),
            pl.col("Year").cast(pl.Int32),
            pl.col("Month").cast(pl.Int32),
            pl.col("accidents").cast(pl.Int32),
            pl.col("avg_severity").cast(pl.Float64),
            pl.col("Severity").cast(pl.Int32),
            pl.col("severity_count").cast(pl.Int32),
            pl.col("Weather_Condition"),
            pl.col("weather_count").cast(pl.Int32)
        )
        data = df.filter(pl.col("State") != "USA")
        data = data.filter(
            [pl.col("Year") == selected_year, pl.col("Severity") == selected_severity] if selected_severity else pl.col("Year") == selected_year
        ).unique(
            subset=["State", "Month"]
        ).group_by(["State"]).agg(agg_func(selected_indicator))

    fig = px.choropleth_mapbox(
        data,
        geojson=county_geojson if selected_state else geojson,
        featureidkey="properties.GEOID" if selected_state else "id",
        locations="GEO_ID" if selected_state else "State",
        color=selected_indicator,
        color_continuous_scale="Viridis",
        opacity=0.3,
        custom_data=["County" if selected_state else "State", selected_indicator]
    )

    fig.update_layout(
            margin={"r":35,"t":0,"l":0,"b":0},
            autosize=True,
            mapbox_accesstoken=mapbox_access_token,
            mapbox_style="dark",
            font=dict(
                color="white"
            )
    )

    fig.update_traces(
        hovertemplate = "State: %{customdata[0]} <br>" + indicator_dict[selected_indicator] + ": %{customdata[1]:.2f} </br>"
    )

    if selected_state:
        center = state_lon_lat_dict[selected_state]

        fig.update_layout( 
            mapbox_zoom=4.3,
            mapbox_center={"lat": center[0], "lon": center[1]}
        )

    else:
        fig.update_layout(
            mapbox_zoom=3,
            mapbox_center={"lat": 38.000000, "lon": -90.000000}     
        )

    return fig


if __name__ == '__main__':
    app.run_server(debug=False)
