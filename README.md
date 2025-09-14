Airline Booking Market Demand Webapp

This project is a Streamlit web application that analyzes airline booking market demand data tailored for hostel business groups across major Australian cities. The application provides data-driven insights and visualizations to support strategic decisions in hostel placement, pricing, and marketing.
Features
Market Analysis

    Visualize flight patterns and demand trends across Australian cities

    Track price fluctuations and identify optimal pricing periods

    Discover seasonal travel patterns

    Analyze popular flight routes

Business Intelligence

    AI-powered recommendations for hostel operations

    Interactive maps displaying route popularity and demand

    Export data and reports for offline use

    Customizable filters for detailed market segmentation

Australian Market Focus

    Specialized insights for major Australian cities

    Tailored analysis for the tourism and hospitality sectors

Prerequisites

    Python 3.8 or higher

    pip package installer

    Internet connection (for API data fetching)

Installation

    Clone the repository:

bash
git clone https://github.com/NoLongerHumanHQ/Airline-Booking-Market-Demand-Webapp.git
cd Airline-Booking-Market-Demand-Webapp

    Install dependencies:

bash
pip install -r requirements.txt

    (Optional) Set up API keys by creating a .env file in the project root:

text
OPENSKY_USERNAME=your_username
OPENSKY_PASSWORD=your_password
AVIATIONSTACK_API_KEY=your_api_key
AMADEUS_API_KEY=your_api_key
AMADEUS_API_SECRET=your_api_secret
OPENAI_API_KEY=your_api_key
GOOGLE_API_KEY=your_api_key
WEATHER_API_KEY=your_api_key

Note: The app uses mock data when API keys are not provided, enabling exploration without API setup.
Usage

    Start the app:

bash
streamlit run app.py

    Open http://localhost:8501 in your browser

    Use the sidebar to:

        Select a city

        Set analysis period

        Load data

        Apply filters by route type and price

    Explore different tabs:

        Market Overview

        Route Analysis

        Price Analysis

        Business Insights

    Export data or reports as needed

Deployment

    Deploy on Streamlit Cloud by connecting your GitHub repository

    Set main file to app.py and use Python 3.8+

    Configure API keys in Streamlit secrets management

Project Structure

text
airline_demand_app/
├── app.py               # Main Streamlit app
├── config.py            # Configuration & API keys
├── data_collector.py    # Fetch data from APIs
├── data_processor.py    # Clean & analyze data
├── visualizations.py    # Chart generation
├── utils.py             # Helper functions
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables
└── README.md            # Project details

Data Sources

    Aviationstack API (real-time flight data)

    OpenSky Network API (free flight tracking)

    Amadeus for Developers (flight offers & analytics)

    Mock data for testing without API keys

Target Audience

    Hostel business owners and operators

    Tourism analysts

    Travel market researchers

    Hospitality sector data analysts

    Business intelligence professionals

Customization

    Add more cities in config.py

    Modify analysis metrics in data_processor.py

    Extend visualizations in visualizations.py

    Add new features or tabs in app.py

Contribution

Fork the repo, create a feature branch, commit your changes, push the branch, and open a pull request.
License

MIT License
Support

For issues, check the Issues tab or open a new issue with details.
Acknowledgments

    Streamlit framework

    Aviation data providers

    Australian tourism data sources

    Open source community

Author

NoLongerHumanHQ
