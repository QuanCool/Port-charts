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
streamlit run streamlit_container_volume.py
```

## Streamlit Cloud Deployment

1. Push your code to GitHub
2. Visit [Streamlit Cloud](https://streamlit.io/cloud)
3. Connect your GitHub repository
4. Deploy the app by selecting `streamlit_container_volume.py` as the main file

## Data Source
The app uses monthly container volume data from "Monthly container volume -  Quarterly sales and NPATMI_Jul 2025.xlsx"
