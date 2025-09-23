import pandas as pd

# Read the Excel file
df = pd.read_excel('Monthly container volume -  Quarterly sales and NPATMI_Jul 2025.xlsx', 
                   sheet_name='Monthly container volume')

# Print detailed information about the DataFrame
print("Data loaded successfully!")
print("\nColumns:", df.columns.tolist())
print("\nColumn names with exact formatting:")
for col in df.columns:
    print(f"'{col}'")
print("\nFirst 5 rows:\n", df.head())
