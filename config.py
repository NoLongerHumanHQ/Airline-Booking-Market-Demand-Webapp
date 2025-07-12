"""
Configuration settings for the Airline Booking Market Demand application.
Contains API keys, endpoints, and application settings.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Keys (loaded from environment variables or Streamlit secrets)
OPENSKY_USERNAME = os.getenv("OPENSKY_USERNAME", "")
OPENSKY_PASSWORD = os.getenv("OPENSKY_PASSWORD", "")
AVIATIONSTACK_API_KEY = os.getenv("AVIATIONSTACK_API_KEY", "")
AMADEUS_API_KEY = os.getenv("AMADEUS_API_KEY", "")
AMADEUS_API_SECRET = os.getenv("AMADEUS_API_SECRET", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "")

# API Endpoints
OPENSKY_API_URL = "https://opensky-network.org/api"
AVIATIONSTACK_API_URL = "http://api.aviationstack.com/v1"
AMADEUS_API_URL = "https://test.api.amadeus.com/v1"
WEATHER_API_URL = "https://api.openweathermap.org/data/2.5"

# Australian Cities and Airports
AUSTRALIAN_CITIES = {
    "Sydney": "SYD",
    "Melbourne": "MEL",
    "Brisbane": "BNE",
    "Perth": "PER",
    "Adelaide": "ADL",
    "Darwin": "DRW",
    "Gold Coast": "OOL",
    "Cairns": "CNS",
    "Canberra": "CBR",
    "Hobart": "HBA"
}

# International Popular Destinations from Australia
POPULAR_INTERNATIONAL_DESTINATIONS = {
    "Auckland": "AKL",
    "Singapore": "SIN",
    "Bali": "DPS",
    "Tokyo": "HND",
    "Hong Kong": "HKG",
    "Los Angeles": "LAX",
    "London": "LHR",
    "Dubai": "DXB",
    "Bangkok": "BKK",
    "Kuala Lumpur": "KUL"
}

# App Settings
DEFAULT_CITY = "Sydney"
DEFAULT_DATE_RANGE = 30  # days
DATA_CACHE_DURATION = 3600  # seconds
MAX_API_RETRIES = 3
REQUEST_TIMEOUT = 10  # seconds 