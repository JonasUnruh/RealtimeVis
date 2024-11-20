from dash import Dash, html, dcc

app = Dash(
    external_stylesheets=["https://codepen.io/chriddyp/pen/bWLwgP.css"]
)

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
                    html.Div(
                        className="eight columns div-for-charts bg-grey",
                        children=[
                            dcc.Graph(id='map-graph')
                        ]
                    )
                ]
            )
        ]
    )
]


if __name__ == "__main__":
    app.run(debug = True)