import pandas as pd

# Read the Excel file
rawdatadf = pd.read_excel('ZEN_sensor_data.xlsx', sheet_name='RAW DATA')
# Display the columns of the dataframe
print("collumns of rawdata: ",rawdatadf.columns)
# Display the shape of the dataframe
print("shape of rawdata: ", rawdatadf.shape)
# Display the first few rows of the dataframe
print(rawdatadf.head())

categorizeddf = pd.read_excel('ZEN_sensor_data.xlsx', sheet_name='CATEGORIZED')
# Display the columns of the categorized dataframe
print("collumns of categorized: ",categorizeddf.columns)
# Display the shape of the categorized dataframe
print("shape of categorized: ",categorizeddf.shape)
# Display the first few rows of the categorized dataframe
print(categorizeddf.head(30))