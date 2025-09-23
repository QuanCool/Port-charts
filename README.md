# Port Container Volume Analysis

Interactive visualization of monthly container volumes for port operators.

## Local Development

1. Clone the repository:
```bash
git clone https://github.com/QuanCool/Port-charts.git
cd Port-charts
```

2. Create a virtual environment and install dependencies:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

3. Run the app locally:
```bash
streamlit run container_volume_dashboard.py
```

## Streamlit Cloud Deployment

1. Push your code to GitHub
2. Visit [Streamlit Cloud](https://streamlit.io/cloud)
3. Connect your GitHub repository
4. Deploy the app by selecting `container_volume_dashboard.py` as the main file

## Features

- Interactive stacked column charts showing container volume by company
- Time period controls (Monthly, Quarterly, Semi-annually, Year-to-date)
- Company selection filters
- Growth rate analysis (Year-on-Year and Period-on-Period)
- Top 5 companies highlighted with custom colors
- Light theme optimized interface

## Data Source
The app uses monthly container volume data from "Monthly container volume -  Quarterly sales and NPATMI_Jul 2025.xlsx"
