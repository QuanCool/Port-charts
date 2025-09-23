<<<<<<< HEAD
import pandas as pd
import datetime

# Read the Excel file
print("Reading Excel file...")
df = pd.read_excel('Monthly container volume -  Quarterly sales and NPATMI_Jul 2025.xlsx', 
                   sheet_name='Monthly container volume')
print("File read successfully.")

# Convert date to datetime if it's not already
df['Date'] = pd.to_datetime(df['Date'])

# Add 1 month to fix the date misalignment
df['Date'] = df['Date'] + pd.DateOffset(months=1)

# Companies to check
companies = ['SNP', 'GMD', 'PHP', 'VSC', 'CDN']

# Get the date range we should have
start_date = df['Date'].min()
end_date = df['Date'].max()

# Create a complete date range at monthly frequency
expected_dates = pd.date_range(start=start_date, end=end_date, freq='MS')

print(f"\nOverall Date Range:")
print(f"Start Date: {start_date.strftime('%B %Y')}")
print(f"End Date: {end_date.strftime('%B %Y')}")
print(f"Expected number of months per company: {len(expected_dates)}")

# First check overall data presence
all_data = df.pivot_table(
    index='Date',
    columns='Company',
    values='Total throughput',
    aggfunc='sum'
).reset_index()

print("\nChecking data presence for all companies...")

for company in companies:
    print(f"\n{'-'*20}")
    print(f"Analyzing {company}:")
    company_data = df[df['Company'] == company]
    
    if company_data.empty:
        print(f"WARNING: No data found for {company}")
        continue
        
    company_dates = company_data['Date'].unique()
    company_dates = pd.DatetimeIndex(sorted(company_dates))
    
    # Find missing months for this company
    missing_months = expected_dates.difference(company_dates)
    
    print(f"Number of months with data: {len(company_dates)} out of {len(expected_dates)}")
    
    if len(missing_months) > 0:
        print(f"Missing months for {company}:")
        for date in sorted(missing_months):
            print(f"- {date.strftime('%B %Y')}")
    else:
        print("✓ Complete data - No missing months")
        
    # Check for zero or null values
    zero_months = company_data[company_data['Total throughput'] == 0]['Date']
    null_months = company_data[company_data['Total throughput'].isnull()]['Date']
    
    if len(zero_months) > 0:
        print("\nMonths with zero throughput:")
        for date in sorted(zero_months):
            print(f"- {date.strftime('%B %Y')}")
            
    if len(null_months) > 0:
        print("\nMonths with null throughput:")
        for date in sorted(null_months):
            print(f"- {date.strftime('%B %Y')}")

# Convert date to datetime if it's not already
df['Date'] = pd.to_datetime(df['Date'])

# Add 1 month to fix the date misalignment
df['Date'] = df['Date'] + pd.DateOffset(months=1)

# Companies to check
companies = ['SNP', 'GMD', 'PHP', 'VSC', 'CDN']

# Get the date range we should have
start_date = df['Date'].min()
end_date = df['Date'].max()

# Create a complete date range at monthly frequency
expected_dates = pd.date_range(start=start_date, end=end_date, freq='MS')  # MS is month start frequency

print("\nAnalyzing data completeness for each company:")
print("-" * 50)

for company in companies:
    company_data = df[df['Company'] == company]
    company_dates = company_data['Date'].unique()
    company_dates = pd.DatetimeIndex(sorted(company_dates))

print(f"\nOverall Date Range:")
print(f"Start Date: {start_date.strftime('%B %Y')}")
print(f"End Date: {end_date.strftime('%B %Y')}")
print(f"Expected number of months per company: {len(expected_dates)}")

for company in companies:
    print(f"\nChecking {company}:")
    company_data = df[df['Company'] == company]
    company_dates = company_data['Date'].unique()
    company_dates = pd.DatetimeIndex(sorted(company_dates))
    
    # Find missing months for this company
    missing_months = expected_dates.difference(company_dates)
    
    print(f"Number of available months: {len(company_dates)}")
    
    if len(missing_months) > 0:
        print(f"Missing months for {company}:")
        for date in missing_months:
            print(f"- {date.strftime('%B %Y')}")
    else:
        print("No missing months found for this company.")
=======
import pandas as pd
import datetime

# Read the Excel file
print("Reading Excel file...")
df = pd.read_excel('Monthly container volume -  Quarterly sales and NPATMI_Jul 2025.xlsx', 
                   sheet_name='Monthly container volume')
print("File read successfully.")

# Convert date to datetime if it's not already
df['Date'] = pd.to_datetime(df['Date'])

# Add 1 month to fix the date misalignment
df['Date'] = df['Date'] + pd.DateOffset(months=1)

# Companies to check
companies = ['SNP', 'GMD', 'PHP', 'VSC', 'CDN']

# Get the date range we should have
start_date = df['Date'].min()
end_date = df['Date'].max()

# Create a complete date range at monthly frequency
expected_dates = pd.date_range(start=start_date, end=end_date, freq='MS')

print(f"\nOverall Date Range:")
print(f"Start Date: {start_date.strftime('%B %Y')}")
print(f"End Date: {end_date.strftime('%B %Y')}")
print(f"Expected number of months per company: {len(expected_dates)}")

# First check overall data presence
all_data = df.pivot_table(
    index='Date',
    columns='Company',
    values='Total throughput',
    aggfunc='sum'
).reset_index()

print("\nChecking data presence for all companies...")

for company in companies:
    print(f"\n{'-'*20}")
    print(f"Analyzing {company}:")
    company_data = df[df['Company'] == company]
    
    if company_data.empty:
        print(f"WARNING: No data found for {company}")
        continue
        
    company_dates = company_data['Date'].unique()
    company_dates = pd.DatetimeIndex(sorted(company_dates))
    
    # Find missing months for this company
    missing_months = expected_dates.difference(company_dates)
    
    print(f"Number of months with data: {len(company_dates)} out of {len(expected_dates)}")
    
    if len(missing_months) > 0:
        print(f"Missing months for {company}:")
        for date in sorted(missing_months):
            print(f"- {date.strftime('%B %Y')}")
    else:
        print("✓ Complete data - No missing months")
        
    # Check for zero or null values
    zero_months = company_data[company_data['Total throughput'] == 0]['Date']
    null_months = company_data[company_data['Total throughput'].isnull()]['Date']
    
    if len(zero_months) > 0:
        print("\nMonths with zero throughput:")
        for date in sorted(zero_months):
            print(f"- {date.strftime('%B %Y')}")
            
    if len(null_months) > 0:
        print("\nMonths with null throughput:")
        for date in sorted(null_months):
            print(f"- {date.strftime('%B %Y')}")

# Convert date to datetime if it's not already
df['Date'] = pd.to_datetime(df['Date'])

# Add 1 month to fix the date misalignment
df['Date'] = df['Date'] + pd.DateOffset(months=1)

# Companies to check
companies = ['SNP', 'GMD', 'PHP', 'VSC', 'CDN']

# Get the date range we should have
start_date = df['Date'].min()
end_date = df['Date'].max()

# Create a complete date range at monthly frequency
expected_dates = pd.date_range(start=start_date, end=end_date, freq='MS')  # MS is month start frequency

print("\nAnalyzing data completeness for each company:")
print("-" * 50)

for company in companies:
    company_data = df[df['Company'] == company]
    company_dates = company_data['Date'].unique()
    company_dates = pd.DatetimeIndex(sorted(company_dates))

print(f"\nOverall Date Range:")
print(f"Start Date: {start_date.strftime('%B %Y')}")
print(f"End Date: {end_date.strftime('%B %Y')}")
print(f"Expected number of months per company: {len(expected_dates)}")

for company in companies:
    print(f"\nChecking {company}:")
    company_data = df[df['Company'] == company]
    company_dates = company_data['Date'].unique()
    company_dates = pd.DatetimeIndex(sorted(company_dates))
    
    # Find missing months for this company
    missing_months = expected_dates.difference(company_dates)
    
    print(f"Number of available months: {len(company_dates)}")
    
    if len(missing_months) > 0:
        print(f"Missing months for {company}:")
        for date in missing_months:
            print(f"- {date.strftime('%B %Y')}")
    else:
        print("No missing months found for this company.")
>>>>>>> d4a3375b61336330aa3631cc2ff60ac968030890
