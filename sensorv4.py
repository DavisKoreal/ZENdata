import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import numpy as np

# Verify file exists
file_path = 'ZEN_sensor_data.xlsx'
if not os.path.exists(file_path):
    print(f"Error: File '{file_path}' not found in current directory: {os.getcwd()}")
    exit(1)

# Load the RAW DATA dataset
try:
    rawdatadf = pd.read_excel(file_path, sheet_name='RAW DATA')
except Exception as e:
    print(f"Error loading Excel file: {e}")
    exit(1)

# Data Cleaning
try:
    rawdatadf['binned_time'] = pd.to_datetime(rawdatadf['binned_time'])
except Exception as e:
    print(f"Error converting binned_time to datetime: {e}")
    exit(1)

# Remove rows with missing sensor data
rawdatadf = rawdatadf.dropna(subset=['pressure', 'temperature', 'co2'])

# Calculate initial y-axis range for pressure
pressure_min = rawdatadf['pressure'].min()
pressure_max = rawdatadf['pressure'].max()
pressure_range = pressure_max - pressure_min
initial_yaxis_range = [pressure_min - 0.1 * pressure_range, pressure_max + 0.1 * pressure_range]

# Create Dash app
app = dash.Dash(__name__)

# Create subplot with two y-axes
fig = make_subplots(specs=[[{"secondary_y": True}]])

# Add Pressure trace
fig.add_trace(
    go.Scatter(
        x=rawdatadf['binned_time'],
        y=rawdatadf['pressure'],
        name='Pressure',
        line=dict(color='blue'),
        mode='lines+markers',
        marker=dict(size=4)
    ),
    secondary_y=False
)

# Add Temperature trace
fig.add_trace(
    go.Scatter(
        x=rawdatadf['binned_time'],
        y=rawdatadf['temperature'],
        name='Temperature (°C)',
        line=dict(color='orange'),
        mode='lines+markers',
        marker=dict(size=4)
    ),
    secondary_y=True
)

# Add CO2 trace
fig.add_trace(
    go.Scatter(
        x=rawdatadf['binned_time'],
        y=rawdatadf['co2'],
        name='CO2',
        line=dict(color='green', dash='dash'),
        mode='lines+markers',
        marker=dict(size=4)
    ),
    secondary_y=True
)

# Update layout for interactivity
fig.update_layout(
    title='Interactive Time Series of Raw Data (Pressure, Temperature, CO2)',
    xaxis_title='Time',
    yaxis_title='Pressure',
    yaxis2_title='Temperature (°C) / CO2',
    hovermode='x unified',
    dragmode='zoom',
    xaxis=dict(
        rangeslider=dict(visible=True),  # Scrollable range slider for time window
        type='date',
        tickformat='%Y-%m-%d %H:%M:%S'
    ),
    yaxis=dict(
        range=initial_yaxis_range  # Initial range for pressure y-axis
    ),
    showlegend=True,
    template='plotly'
)

# Enable zoom and pan
fig.update_xaxes(
    showspikes=True,
    spikecolor="black",
    spikethickness=1,
    spikedash="dot",
    spikemode="across"
)

# Define app layout
app.layout = html.Div([
    html.H3("Sensor Data Dashboard"),
    dcc.Graph(id='sensor-graph', figure=fig),
    html.Label("Pressure Y-Axis Scale Factor:"),
    dcc.Slider(
        id='y-scale-slider',
        min=0.1,
        max=5,
        step=0.1,
        value=1,
        marks={i: f'{i}' for i in [0.1, 1, 2, 3, 4, 5]},
        tooltip={"placement": "bottom", "always_visible": True}
    ),
    html.Div(id='slider-output', style={'marginTop': 20})
])

# Callback to update y-axis range
@app.callback(
    [Output('sensor-graph', 'figure'), Output('slider-output', 'children')],
    [Input('y-scale-slider', 'value')]
)
def update_y_axis(scale):
    fig_new = go.Figure(fig)
    new_range = [initial_yaxis_range[0] / scale, initial_yaxis_range[1] / scale]
    fig_new.update_yaxes(range=new_range, secondary_y=False)
    return fig_new, f"Pressure Y-Axis Scale Factor: {scale}"

# Run the server
if __name__ == '__main__':
    print("Starting Dash server... Open your browser to http://127.0.0.1:8050/")
    app.run(debug=True)