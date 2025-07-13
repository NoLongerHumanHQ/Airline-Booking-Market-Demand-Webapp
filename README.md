# Airline Booking Market Demand Webapp 🛫

A comprehensive Streamlit web application that analyzes airline booking market demand data for hostel business groups across Australian cities. This application provides actionable insights and visualizations to help make data-driven decisions for hostel placement, pricing, and marketing strategies.

## 🚀 Features

### 📊 Market Analysis
- **Market Demand Analysis**: Visualize flight patterns and demand trends across Australian cities
- **Price Trend Analysis**: Track pricing fluctuations over time to identify optimal pricing windows
- **Seasonal Patterns**: Identify peak travel periods for strategic planning
- **Route Analysis**: Analyze popular flight routes and their demand patterns

### 🧠 Business Intelligence
- **AI-Powered Recommendations**: Get intelligent suggestions for hostel operations
- **Interactive Maps**: View route popularity and demand visually
- **Data Export**: Download data and reports for offline analysis
- **Customizable Filters**: Focus on specific market segments and criteria

### 🇦🇺 Australian Market Focus
- Specialized analysis for major Australian cities
- Tailored insights for the Australian tourism and hospitality market
- Local market trends and patterns

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Internet connection for API data fetching

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/NoLongerHumanHQ/Airline-Booking-Market-Demand-Webapp.git
   cd Airline-Booking-Market-Demand-Webapp
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up API keys (Optional)**
   
   Create a `.env` file in the project root directory with your API keys:
   ```env
   OPENSKY_USERNAME=your_username
   OPENSKY_PASSWORD=your_password
   AVIATIONSTACK_API_KEY=your_api_key
   AMADEUS_API_KEY=your_api_key
   AMADEUS_API_SECRET=your_api_secret
   OPENAI_API_KEY=your_api_key
   GOOGLE_API_KEY=your_api_key
   WEATHER_API_KEY=your_api_key
   ```

   > **Note**: The application will use mock data when API keys are not available, so you can still explore the functionality without setting up all APIs.

## 🚀 Usage

1. **Start the application**
   ```bash
   streamlit run app.py
   ```

2. **Access the webapp**
   
   The application will open in your default web browser at `http://localhost:8501`

3. **Navigate the interface**
   - Select a city from the dropdown menu in the sidebar
   - Set your desired analysis period using the slider
   - Click "Load Data" to fetch and analyze flight data
   - Use filters to narrow down data by route type and price range

4. **Explore the analysis tabs**
   - **Market Overview**: General market trends and statistics
   - **Route Analysis**: Detailed route performance and popularity
   - **Price Analysis**: Pricing trends and forecasts
   - **Business Insights**: AI-powered recommendations and insights

5. **Export data**
   
   Use the export buttons in the sidebar to download data or reports for offline analysis.

## 🌐 Deployment

### Streamlit Cloud Deployment

1. Create an account at [streamlit.io](https://streamlit.io/)
2. Connect your GitHub repository
3. Deploy with these settings:
   - **Main file path**: `app.py`
   - **Python version**: 3.8+
4. Set up your API keys in the Streamlit Cloud secrets management section

### Local Development

For local development, ensure you have all dependencies installed and API keys configured in your `.env` file.

## 📁 Project Structure

```
airline_demand_app/
├── app.py                 # Main Streamlit application
├── config.py              # Configuration settings and API keys
├── data_collector.py      # API calls and data fetching
├── data_processor.py      # Data cleaning and analysis
├── visualizations.py      # Chart generation functions
├── utils.py              # Helper functions
├── requirements.txt      # Python dependencies
├── .env                  # Environment variables (create this)
└── README.md            # This file
```

## 📊 Data Sources

The application integrates with multiple data sources:

- **Aviationstack API**: Real-time flight data (free tier available)
- **OpenSky Network API**: Free flight tracking data
- **Amadeus for Developers**: Flight offers and analytics (free sandbox available)
- **Mock Data**: Generated when API keys are not available for testing

## 🎯 Target Audience

This application is designed for:
- Hostel business owners and operators
- Tourism industry analysts
- Travel market researchers
- Business intelligence professionals
- Data analysts in the hospitality sector

## 🔧 Customization

To customize the application for your specific needs:

1. **Add new cities**: Edit `config.py` to include additional cities
2. **Modify analysis methods**: Update `data_processor.py` to include custom metrics
3. **Create new visualizations**: Add charts and graphs in `visualizations.py`
4. **Extend functionality**: Add new tabs or features to `app.py`

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/NoLongerHumanHQ/Airline-Booking-Market-Demand-Webapp/issues) section
2. Create a new issue if your problem isn't already reported
3. Provide detailed information about your environment and the issue

## 🙏 Acknowledgments

- Streamlit for the excellent web framework
- Various aviation APIs for providing flight data
- Australian tourism data providers
- Open source community for inspiration and support

---

**Made with ❤️ by [NoLongerHumanHQ](https://github.com/NoLongerHumanHQ)**
