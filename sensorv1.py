import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
import plotly.io as pio

# Verify environment and dependencies
try:
    import nbformat
    print("nbformat is installed:", nbformat.__version__)
except ImportError:
    print("Error: nbformat is not installed. Please run 'pip install nbformat'.")
    exit(1)

# Set Plotly renderer to ensure compatibility
pio.renderers.default = 'jupyterlab'  # Try 'notebook' or 'browser' if 'jupyterlab' fails

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

# 1. Data Cleaning
# Ensure binned_time is datetime
try:
    rawdatadf['binned_time'] = pd.to_datetime(rawdatadf['binned_time'])
except Exception as e:
    print(f"Error converting binned_time to datetime: {e}")
    exit(1)

# Remove rows with missing sensor data
rawdatadf = rawdatadf.dropna(subset=['pressure', 'temperature'])

# 2. Create Interactive Time Series Plot
# Create a subplot with two y-axes
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

# Add CO2 trace (on same axis as temperature)
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
        rangeslider=dict(visible=True),  # Scrollable range slider
        type='date',
        tickformat='%Y-%m-%d %H:%M:%S'
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

# Show the plot
try:
    fig.show()
    print("Interactive plot displayed successfully.")
except Exception as e:
    print(f"Error displaying plot: {e}")
    print("Falling back to HTML output.")

# Save as HTML for standalone viewing
try:
    fig.write_html('raw_data_timeseries.html')
    print("Interactive plot saved as 'raw_data_timeseries.html' in", os.getcwd())
except Exception as e:
    print(f"Error saving HTML file: {e}")