import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
import plotly.io as pio
import uuid

# Set Plotly renderer to browser
pio.renderers.default = 'browser'

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

# Add custom HTML and JavaScript for y-axis scale slider
html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Interactive Sensor Data Plot</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .slider-container {{ margin: 20px 0; }}
        #plot {{ width: 100%; height: 600px; }}
    </style>
</head>
<body>
    <div id="plot"></div>
    <div class="slider-container">
        <label for="yScaleSlider">Pressure Y-Axis Scale Multiplier: </label>
        <input type="range" min="0.1" max="10" step="0.1" value="1" id="yScaleSlider">
        <span id="yScaleValue">1.0</span>
    </div>
    <script>
        // Plotly plot
        var plotDiv = document.getElementById('plot');
        var plotlyData = {fig.to_json()};
        
        // Initial plot
        Plotly.newPlot(plotDiv, plotlyData.data, plotlyData.layout);

        // Y-axis scale slider functionality
        var slider = document.getElementById('yScaleSlider');
        var output = document.getElementById('yScaleValue');
        output.innerHTML = slider.value;

        slider.oninput = function() {{
            output.innerHTML = this.value;
            var scale = parseFloat(this.value);
            var newData = JSON.parse(JSON.stringify(plotlyData.data));
            // Scale the y-values of the pressure trace (index 0)
            newData[0].y = newData[0].y.map(y => y * scale);
            Plotly.update(plotDiv, {{data: newData}}, {{'yaxis.range': null}});
        }};
    </script>
</body>
</html>
"""

# Generate unique output filename to avoid overwriting
output_file = f'raw_data_timeseries_{uuid.uuid4().hex[:8]}.html'
try:
    with open(output_file, 'w') as f:
        f.write(html_content)
    print(f"Interactive plot saved as '{output_file}' and launched in browser from {os.getcwd()}")
except Exception as e:
    print(f"Error saving HTML file: {e}")

# Display in browser
try:
    fig.write_html(output_file, include_plotlyjs='cdn', post_script='''
        var slider = document.createElement('input');
        slider.type = 'range';
        slider.min = '0.1';
        slider.max = '10';
        slider.step = '0.1';
        slider.value = '1';
        slider.id = 'yScaleSlider';
        var label = document.createElement('label');
        label.for = 'yScaleSlider';
        label.innerHTML = 'Pressure Y-Axis Scale Multiplier: ';
        var output = document.createElement('span');
        output.id = 'yScaleValue';
        output.innerHTML = '1.0';
        var container = document.createElement('div');
        container.className = 'slider-container';
        container.appendChild(label);
        container.appendChild(slider);
        container.appendChild(output);
        document.body.insertBefore(container, document.getElementById('plotly'));
        slider.oninput = function() {
            document.getElementById('yScaleValue').innerHTML = this.value;
            var scale = parseFloat(this.value);
            var newData = JSON.parse(JSON.stringify(Plotly.d3.select('#plotly').datum().data));
            newData[0].y = newData[0].y.map(y => y * scale);
            Plotly.update('plotly', {data: newData}, {'yaxis.range': null});
        };
    ''')
    import webbrowser
    webbrowser.open(f'file://{os.path.abspath(output_file)}')
except Exception as e:
    print(f"Error launching browser: {e}")