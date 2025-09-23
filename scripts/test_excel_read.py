<<<<<<< HEAD
import pandas as pd
import os

# Print current working directory
print("Current working directory:", os.getcwd())

# Print if file exists
file_path = 'Monthly container volume -  Quarterly sales and NPATMI_Jul 2025.xlsx'
print(f"\nFile exists: {os.path.exists(file_path)}")

try:
    # Try to read the Excel file
    print("\nAttempting to read Excel file...")
    df = pd.read_excel(file_path)
    
    # Display basic information about the DataFrame
    print("\nData read successfully!")
    print("\nColumns found:", df.columns.tolist())
    print("\nShape of data:", df.shape)
    print("\nFirst few rows:")
    print(df.head())
    
except Exception as e:
    print(f"\nError reading file: {str(e)}")
=======
import pandas as pd
import os

# Print current working directory
print("Current working directory:", os.getcwd())

# Print if file exists
file_path = 'Monthly container volume -  Quarterly sales and NPATMI_Jul 2025.xlsx'
print(f"\nFile exists: {os.path.exists(file_path)}")

try:
    # Try to read the Excel file
    print("\nAttempting to read Excel file...")
    df = pd.read_excel(file_path)
    
    # Display basic information about the DataFrame
    print("\nData read successfully!")
    print("\nColumns found:", df.columns.tolist())
    print("\nShape of data:", df.shape)
    print("\nFirst few rows:")
    print(df.head())
    
except Exception as e:
    print(f"\nError reading file: {str(e)}")
>>>>>>> d4a3375b61336330aa3631cc2ff60ac968030890
