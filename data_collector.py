"""
Data collection module for the Airline Booking Market Demand application.
Handles API requests and data retrieval from various sources.
"""
import requests
import json
import time
import random
import pandas as pd
from datetime import datetime, timedelta
import config
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class APIRateLimitError(Exception):
    """Exception raised when API rate limit is exceeded."""
    pass

def handle_api_error(response, service_name):
    """Handle API errors and provide appropriate logging."""
    try:
        error_msg = f"{service_name} API Error: {response.status_code}"
        response_json = response.json()
        if 'errors' in response_json:
            error_msg += f" - {response_json['errors']}"
        elif 'error' in response_json:
            error_msg += f" - {response_json['error']}"
    except:
        error_msg = f"{service_name} API Error: {response.status_code} - {response.text}"
    
    logger.error(error_msg)
    
    if response.status_code == 429:
        raise APIRateLimitError(f"{service_name} rate limit exceeded")
    return None

class OpenSkyAPI:
    """OpenSky Network API client for flight data retrieval."""
    
    def __init__(self):
        self.base_url = config.OPENSKY_API_URL
        self.auth = None
        if config.OPENSKY_USERNAME and config.OPENSKY_PASSWORD:
            self.auth = (config.OPENSKY_USERNAME, config.OPENSKY_PASSWORD)
    
    def get_flights_by_airport(self, airport_code, begin=None, end=None):
        """Get flights for a specific airport within a time range."""
        if not begin:
            begin = int((datetime.now() - timedelta(days=7)).timestamp())
        if not end:
            end = int(datetime.now().timestamp())
        
        # Convert airport code to ICAO format if needed
        airport = airport_code
        
        params = {
            'airport': airport,
            'begin': begin,
            'end': end
        }
        
        for attempt in range(config.MAX_API_RETRIES):
            try:
                response = requests.get(
                    f"{self.base_url}/flights/arrival",
                    params=params,
                    auth=self.auth,
                    timeout=config.REQUEST_TIMEOUT
                )
                
                if response.status_code == 200:
                    return response.json()
                
                # Handle rate limiting
                if response.status_code == 429:
                    wait_time = min(2 ** attempt, 60)
                    logger.warning(f"Rate limited, waiting {wait_time}s before retry")
                    time.sleep(wait_time)
                    continue
                
                return handle_api_error(response, "OpenSky")
                
            except requests.exceptions.RequestException as e:
                logger.error(f"OpenSky API request failed: {str(e)}")
                time.sleep(1)
        
        # If all retries failed
        return None
    
    def get_all_flights(self):
        """Get all current flights (for demo purposes with sample data)."""
        try:
            response = requests.get(
                f"{self.base_url}/states/all",
                auth=self.auth,
                timeout=config.REQUEST_TIMEOUT
            )
            
            if response.status_code == 200:
                return response.json()
            return handle_api_error(response, "OpenSky")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"OpenSky API request failed: {str(e)}")
            return None

class AviationStackAPI:
    """AviationStack API client for real-time flight data."""
    
    def __init__(self):
        self.base_url = config.AVIATIONSTACK_API_URL
        self.api_key = config.AVIATIONSTACK_API_KEY
    
    def get_flights(self, dep_iata=None, arr_iata=None, limit=100):
        """Get real-time flights with optional departure/arrival filtering."""
        params = {
            'access_key': self.api_key,
            'limit': limit
        }
        
        if dep_iata:
            params['dep_iata'] = dep_iata
        if arr_iata:
            params['arr_iata'] = arr_iata
        
        for attempt in range(config.MAX_API_RETRIES):
            try:
                response = requests.get(
                    f"{self.base_url}/flights",
                    params=params,
                    timeout=config.REQUEST_TIMEOUT
                )
                
                if response.status_code == 200:
                    return response.json()
                
                # Handle rate limiting
                if response.status_code == 429:
                    wait_time = min(2 ** attempt, 60)
                    logger.warning(f"Rate limited, waiting {wait_time}s before retry")
                    time.sleep(wait_time)
                    continue
                
                return handle_api_error(response, "AviationStack")
                
            except requests.exceptions.RequestException as e:
                logger.error(f"AviationStack API request failed: {str(e)}")
                time.sleep(1)
        
        return None
    
    def get_routes(self, dep_iata=None):
        """Get available airline routes from a specific airport."""
        params = {
            'access_key': self.api_key,
            'limit': 100
        }
        
        if dep_iata:
            params['dep_iata'] = dep_iata
        
        try:
            response = requests.get(
                f"{self.base_url}/routes",
                params=params,
                timeout=config.REQUEST_TIMEOUT
            )
            
            if response.status_code == 200:
                return response.json()
            return handle_api_error(response, "AviationStack")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"AviationStack API request failed: {str(e)}")
            return None

class AmadeusAPI:
    """Amadeus for Developers API client for flight offers and analytics."""
    
    def __init__(self):
        self.base_url = config.AMADEUS_API_URL
        self.api_key = config.AMADEUS_API_KEY
        self.api_secret = config.AMADEUS_API_SECRET
        self.token = None
        self.token_expires = 0
    
    def _get_access_token(self):
        """Get OAuth access token for Amadeus API."""
        if self.token and time.time() < self.token_expires:
            return self.token
        
        try:
            response = requests.post(
                "https://test.api.amadeus.com/v1/security/oauth2/token",
                data={
                    'grant_type': 'client_credentials',
                    'client_id': self.api_key,
                    'client_secret': self.api_secret
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data['access_token']
                self.token_expires = time.time() + data['expires_in'] - 30  # Buffer of 30 seconds
                return self.token
            
            logger.error(f"Amadeus authentication failed: {response.text}")
            return None
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Amadeus authentication request failed: {str(e)}")
            return None
    
    def search_flight_offers(self, origin, destination, departure_date):
        """Search for flight offers between two locations."""
        token = self._get_access_token()
        if not token:
            return None
        
        headers = {
            "Authorization": f"Bearer {token}"
        }
        
        params = {
            "originLocationCode": origin,
            "destinationLocationCode": destination,
            "departureDate": departure_date,
            "adults": 1,
            "max": 20
        }
        
        for attempt in range(config.MAX_API_RETRIES):
            try:
                response = requests.get(
                    f"{self.base_url}/shopping/flight-offers",
                    headers=headers,
                    params=params,
                    timeout=config.REQUEST_TIMEOUT
                )
                
                if response.status_code == 200:
                    return response.json()
                
                # Handle rate limiting
                if response.status_code == 429:
                    wait_time = min(2 ** attempt, 60)
                    logger.warning(f"Rate limited, waiting {wait_time}s before retry")
                    time.sleep(wait_time)
                    continue
                
                # Handle expired token
                if response.status_code == 401:
                    self.token = None
                    token = self._get_access_token()
                    if token:
                        headers["Authorization"] = f"Bearer {token}"
                        continue
                
                return handle_api_error(response, "Amadeus")
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Amadeus API request failed: {str(e)}")
                time.sleep(1)
        
        return None

def generate_mock_flight_data(origin=None, days=30):
    """Generate mock flight data for demonstration purposes."""
    today = datetime.now()
    flight_data = []
    
    # Define possible destination airports based on origin
    if origin:
        if origin in config.AUSTRALIAN_CITIES.values():
            # If Australian city, use mix of domestic and international
            possible_destinations = list(config.AUSTRALIAN_CITIES.values()) + list(config.POPULAR_INTERNATIONAL_DESTINATIONS.values())
            # Remove the origin from possible destinations
            if origin in possible_destinations:
                possible_destinations.remove(origin)
        else:
            # For international origin, focus on Australian destinations
            possible_destinations = list(config.AUSTRALIAN_CITIES.values())
    else:
        # Default to all destinations
        possible_destinations = list(config.AUSTRALIAN_CITIES.values()) + list(config.POPULAR_INTERNATIONAL_DESTINATIONS.values())
    
    # Generate random flight data
    for day in range(days):
        date = today + timedelta(days=day)
        # More flights during weekends
        num_flights = random.randint(15, 30) if date.weekday() >= 5 else random.randint(8, 20)
        
        # Seasonal adjustments
        month = date.month
        if month in [12, 1]:  # Summer holiday season in Australia
            num_flights = int(num_flights * 1.5)
        elif month in [6, 7]:  # Winter holiday season
            num_flights = int(num_flights * 1.3)
        
        for _ in range(num_flights):
            destination = random.choice(possible_destinations)
            
            # Determine if domestic or international flight
            is_domestic = (origin in config.AUSTRALIAN_CITIES.values() and 
                          destination in config.AUSTRALIAN_CITIES.values())
            
            # Price ranges differ for domestic vs international
            if is_domestic:
                base_price = random.randint(120, 500)
            else:
                base_price = random.randint(500, 2000)
            
            # Weekend and seasonal price adjustments
            if date.weekday() >= 5:  # Weekend
                base_price = int(base_price * 1.2)
            
            if month in [12, 1, 6, 7]:  # Peak seasons
                base_price = int(base_price * 1.3)
            
            # Add some randomness to the price
            final_price = base_price + random.randint(-50, 100)
            final_price = max(100, final_price)  # Ensure minimum price
            
            # Random flight duration (in minutes)
            if is_domestic:
                duration = random.randint(60, 180)
            else:
                duration = random.randint(180, 900)
            
            flight_time = datetime.combine(date.date(), 
                                          datetime.strptime(f"{random.randint(6, 22)}:{random.randint(0, 59):02d}", 
                                                           "%H:%M").time())
            
            flight_data.append({
                'flight_date': flight_time.strftime('%Y-%m-%d'),
                'flight_time': flight_time.strftime('%H:%M'),
                'origin': origin or random.choice(list(config.AUSTRALIAN_CITIES.values())),
                'destination': destination,
                'price': final_price,
                'airline': random.choice(['Qantas', 'Virgin Australia', 'Jetstar', 'Tiger Air', 'Emirates', 'Singapore Airlines']),
                'duration': duration,
                'is_domestic': is_domestic
            })
    
    return pd.DataFrame(flight_data)

def get_flight_data(city_code, days=30):
    """Get flight data for a specific city (real API or mock data)."""
    # Try to get real data from APIs if keys are available
    if config.AVIATIONSTACK_API_KEY:
        aviation_api = AviationStackAPI()
        data = aviation_api.get_flights(dep_iata=city_code, limit=100)
        if data and 'data' in data and len(data['data']) > 0:
            # Process and return the API data
            flights = []
            for flight in data['data']:
                flights.append({
                    'flight_date': flight.get('flight_date', ''),
                    'flight_time': flight.get('departure', {}).get('scheduled', '').split(' ')[-1] if flight.get('departure', {}).get('scheduled') else '',
                    'origin': flight.get('departure', {}).get('iata', ''),
                    'destination': flight.get('arrival', {}).get('iata', ''),
                    'price': None,  # Price not available from AviationStack
                    'airline': flight.get('airline', {}).get('name', ''),
                    'duration': None,  # Duration calculation would need additional processing
                    'is_domestic': flight.get('departure', {}).get('iata', '')[:2] == flight.get('arrival', {}).get('iata', '')[:2]
                })
            return pd.DataFrame(flights)
    
    # Fall back to mock data if API doesn't return valid data
    return generate_mock_flight_data(origin=city_code, days=days)

def get_weather_data(city, days=7):
    """Get weather forecast data for a city."""
    if not config.WEATHER_API_KEY:
        # Return mock weather data
        return generate_mock_weather_data(city, days)
    
    params = {
        'q': city,
        'units': 'metric',
        'appid': config.WEATHER_API_KEY
    }
    
    try:
        response = requests.get(
            f"{config.WEATHER_API_URL}/forecast",
            params=params,
            timeout=config.REQUEST_TIMEOUT
        )
        
        if response.status_code == 200:
            return response.json()
        return handle_api_error(response, "Weather API")
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Weather API request failed: {str(e)}")
        # Fall back to mock data
        return generate_mock_weather_data(city, days)

def generate_mock_weather_data(city, days=7):
    """Generate mock weather data for demonstration purposes."""
    today = datetime.now()
    weather_data = []
    
    # Set season based on current month (assuming Australian seasons)
    month = today.month
    if month in [12, 1, 2]:  # Summer in Australia
        temp_min, temp_max = 20, 35
    elif month in [3, 4, 5]:  # Fall
        temp_min, temp_max = 15, 25
    elif month in [6, 7, 8]:  # Winter
        temp_min, temp_max = 5, 18
    else:  # Spring
        temp_min, temp_max = 12, 22
    
    # Adjust temperature ranges by city
    if city in ["Darwin", "DRW"]:
        temp_min += 5
        temp_max += 5
    elif city in ["Hobart", "HBA"]:
        temp_min -= 5
        temp_max -= 5
    
    # Generate data for each day
    for day in range(days):
        date = today + timedelta(days=day)
        
        # Add some randomness to temperatures
        day_temp = random.uniform(temp_min, temp_max)
        night_temp = day_temp - random.uniform(5, 10)
        
        # Generate random weather condition
        conditions = ["Clear", "Partly Cloudy", "Cloudy", "Rain", "Thunderstorm", "Sunny"]
        weights = [0.2, 0.3, 0.2, 0.15, 0.05, 0.1]
        condition = random.choices(conditions, weights=weights, k=1)[0]
        
        weather_data.append({
            'date': date.strftime('%Y-%m-%d'),
            'city': city,
            'temp_day': round(day_temp, 1),
            'temp_night': round(night_temp, 1),
            'condition': condition
        })
    
    return pd.DataFrame(weather_data) 