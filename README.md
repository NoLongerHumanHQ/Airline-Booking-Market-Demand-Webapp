# Airline Booking Market Demand Analysis

A Streamlit web application that analyzes airline booking market demand data for hostel business groups across Australian cities. The application provides insights and visualizations to help make data-driven decisions for hostel placement, pricing, and marketing strategies.

![Application Screenshot](https://storage.googleapis.com/gweb-cloudblog-publish/images/travel_predictions.max-1000x1000.jpg)

## Features

- **Market Demand Analysis**: Visualize flight patterns and demand trends
- **Price Trend Analysis**: Track pricing fluctuations over time
- **Seasonal Patterns**: Identify peak travel periods
- **Business Intelligence**: Get AI-powered recommendations for hostel operations
- **Interactive Maps**: View route popularity visually
- **Data Export**: Download data and reports for offline analysis
- **Customizable Filters**: Focus on specific market segments
- **Australian Market Focus**: Specialized for major Australian cities

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Setup

1. Clone this repository or download the source code

2. Navigate to the project directory
```bash
cd airline_demand_app
```

3. Install required dependencies
```bash
pip install -r requirements.txt
```

4. (Optional) Set up API keys for real data

Create a `.env` file in the project root directory with your API keys:
```
OPENSKY_USERNAME=your_username
OPENSKY_PASSWORD=your_password
AVIATIONSTACK_API_KEY=your_api_key
AMADEUS_API_KEY=your_api_key
AMADEUS_API_SECRET=your_api_secret
OPENAI_API_KEY=your_api_key
GOOGLE_API_KEY=your_api_key
WEATHER_API_KEY=your_api_key
```

## Usage

1. Run the Streamlit application:
```bash
streamlit run app.py
```

2. The application will open in your default web browser at `localhost:8501`

3. Select a city from the dropdown menu in the sidebar

4. Set your desired analysis period using the slider

5. Click "Load Data" to fetch and analyze flight data

6. Use the filters to narrow down the data by route type and price range

7. Navigate through the tabs to explore different aspects of the data:
   - Market Overview
   - Route Analysis
   - Price Analysis
   - Business Insights

8. Export data or reports using the buttons in the sidebar

## Deployment

### Deploying to Streamlit Cloud

1. Create an account at [streamlit.io](https://streamlit.io/)

2. Connect your GitHub repository

3. Deploy the app with these settings:
   - Main file path: `app.py`

4. Set up your API keys in the Streamlit Cloud secrets management section

## Data Sources

The application uses data from various sources:

- **Aviationstack API**: Real-time flight data (free tier available)
- **OpenSky Network API**: Free flight tracking data
- **Amadeus for Developers**: Flight offers and analytics (free sandbox available)
- **Mock data**: Generated when API keys are not available

## Project Structure

```
airline_demand_app/
├── app.py                   # Main Streamlit application
├── config.py                # Configuration settings and API keys
├── data_collector.py        # API calls and data fetching
├── data_processor.py        # Data cleaning and analysis
├── visualizations.py        # Chart generation functions
├── utils.py                 # Helper functions
├── requirements.txt         # Python dependencies
└── README.md                # This file
```

## Customization

To customize the application for your specific needs:

1. Edit `config.py` to adjust settings and add additional cities
2. Modify the analysis methods in `data_processor.py` to include your own metrics
3. Create additional visualizations in `visualizations.py`
4. Add new tabs or features to `app.py`

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- [Streamlit](https://streamlit.io/) for the web application framework
- [Plotly](https://plotly.com/) for interactive visualizations
- [Folium](https://python-visualization.github.io/folium/) for map visualizations
- Various data providers and APIs 