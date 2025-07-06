import pandas as pd
import os
import json

# Verify file exists
file_path = 'ZEN_sensor_data.xlsx'
if not os.path.exists(file_path):
    print(f"Error: File '{file_path}' not found in current directory: {os.getcwd()}")
    exit(1)

# Load the RAW DATA dataset
try:
    df = pd.read_excel(file_path, sheet_name='RAW DATA')
except Exception as e:
    print(f"Error loading Excel file: {e}")
    exit(1)

# Data Cleaning
try:
    df['binned_time'] = pd.to_datetime(df['binned_time'])
except Exception as e:
    print(f"Error converting binned_time to datetime: {e}")
    exit(1)

# Remove rows with missing sensor data or pressure > 150
df = df.dropna(subset=['pressure', 'temperature'])
df = df[df['pressure'] <= 150]

# Convert to Lightweight Charts format (timestamp in seconds, value)
data = {
    'pressure': [
        {'time': int(row['binned_time'].timestamp()), 'value': row['pressure']}
        for _, row in df.iterrows()
    ],
    'temperature': [
        {'time': int(row['binned_time'].timestamp()), 'value': row['temperature']}
        for _, row in df.iterrows()
    ],
    'co2': [
        {'time': int(row['binned_time'].timestamp()), 'value': row['co2']}
        for _, row in df.iterrows() if pd.notna(row['co2'])
    ]
}

# Save to JSON
try:
    with open('sensor_data.json', 'w') as f:
        json.dump(data, f)
    print("Data saved as 'sensor_data.json' in", os.getcwd())
except Exception as e:
    print(f"Error saving JSON file: {e}")