import os
import pandas as pd

# Set the working directory to the location of the current script (app.py)
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)


import dash
from dash import dcc, html, Input, Output
import plotly.express as px

# Create a Dash app instance
app = dash.Dash(__name__)

# Load the CSV data once (using a store component)
df_sampled = pd.read_csv('./data/US_Accidents_March23_sampled_500k.csv')

# Preprocess data for choropleth hover text
state_severity_summary = df_sampled.groupby(['State', 'Severity']).size().reset_index(name='Count')
state_summary = df_sampled.groupby('State').size().reset_index(name='Total_Accidents')

# Merge the summaries for detailed hover text
state_severity_hover = pd.merge(state_summary, state_severity_summary, on='State', how='left')

# Create the choropleth map to show accidents by state
def create_choropleth_map():
    # Prepare hover text
    hover_text = state_severity_hover.groupby('State').apply(
        lambda x: f"State: {x['State'].iloc[0]}<br>"
                  f"Total Accidents: {x['Total_Accidents'].iloc[0]}<br>"
                  + "<br>".join([f"Severity {row['Severity']}: {row['Count']}" for _, row in x.iterrows()])
    ).reset_index(name='Hover_Text')

    # Add hover text to the state summary
    state_summary_with_hover = pd.merge(state_summary, hover_text, on='State', how='left')

    # Plotly Choropleth map
    fig = px.choropleth(state_summary_with_hover, 
                        locations='State',  # The states
                        locationmode="USA-states",  # Use the USA-states mode for locations
                        color='Total_Accidents',  # The number of accidents
                        hover_name='State',  # Display state name on hover
                        hover_data={'Hover_Text': True, 'Total_Accidents': False, 'State': False},
                        color_continuous_scale="Oranges",  # Color scale for the choropleth
                        title="Accidents by State",
                        template='plotly_dark',
                        scope = 'usa')
    fig.update_traces(hovertemplate='%{customdata[0]}')  # Use custom hover template
    return fig

# Create the bar chart for severity levels
def create_severity_bar_chart():
    severity_counts = df_sampled['Severity'].value_counts().reset_index()
    severity_counts.columns = ['Severity', 'Accident_Count']
    severity_counts = severity_counts.sort_values('Severity')  # Ensure proper order
    fig = px.bar(severity_counts, x='Severity', y='Accident_Count',
                 title='Accidents by Severity',
                 labels={'Accident_Count': 'Number of Accidents'},
                 template='plotly_dark',
                 color_discrete_sequence=['orange'])
    return fig

# Create the line graph for accidents over time (aggregated by month)
def create_accidents_over_month_line_graph():
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
    return fig


app.layout = html.Div([
    html.H1("Simple Dashboard", style={'textAlign': 'center', 'color': 'white'}),  # Title of the dashboard

    # Store the data in the app (this could be used in future callbacks)
    dcc.Store(id='data-store', data=df_sampled.to_dict('records')),  # Storing data

    # Display the choropleth map
    html.Div([
        html.H3("Accidents by State (Choropleth Map)", style={'textAlign': 'center', 'color': 'white'}),
        dcc.Graph(
            id='accidents-choropleth-map',
            figure=create_choropleth_map()  # Create the choropleth map when the app starts
        )
    ], style={'padding': '20px'}),

    # Dropdown to select the chart type
    html.Div([
        html.H3("Choose Chart Type", style={'textAlign': 'center', 'color': 'white'}),
        dcc.Dropdown(
            id='chart-type-dropdown',
            options=[
                {'label': 'Severity Bar Chart', 'value': 'severity_bar'},
                {'label': 'Accidents Over Time Line Graph', 'value': 'time_line'}
            ],
            value='severity_bar',  # Default value
            style={'width': '50%', 'margin': 'auto'}
        ),
        dcc.Graph(id='chart-display')  # Placeholder for the selected chart
    ], style={'padding': '20px'})
], style={'backgroundColor': '#111111'})  # Set overall background to dark theme color



# Define the callback for the dropdown
@app.callback(
    Output('chart-display', 'figure'),
    Input('chart-type-dropdown', 'value')
)
def update_chart(chart_type):
    if chart_type == 'severity_bar':
        return create_severity_bar_chart()
    elif chart_type == 'time_line':
        return create_accidents_over_month_line_graph()  # Use the updated function

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)