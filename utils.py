"""
Utility functions for the Airline Booking Market Demand application.
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import os
import re
import logging
import base64
import streamlit as st
from fpdf import FPDF
import io

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def format_airport_code(code):
    """Format an airport code properly."""
    if not code:
        return ""
    
    # Convert to uppercase and strip any whitespace
    formatted = code.strip().upper()
    
    # Ensure it's a valid 3-letter IATA code
    if len(formatted) != 3 or not formatted.isalpha():
        logger.warning(f"Invalid airport code: {code}")
    
    return formatted

def format_currency(value):
    """Format a number as currency."""
    if pd.isna(value):
        return "N/A"
    
    try:
        return f"${float(value):,.2f}"
    except (ValueError, TypeError):
        return "N/A"

def generate_date_ranges(days=30):
    """Generate a range of dates from today."""
    today = datetime.now().date()
    dates = [(today + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(days)]
    return dates

def extract_city_name(airport_name):
    """Extract the city name from an airport name."""
    # Example: "Sydney Airport (SYD)" -> "Sydney"
    if not airport_name:
        return ""
    
    # Try to extract city name using common patterns
    patterns = [
        r'^([A-Za-z\s]+)(?:\sAirport|\sInternational|\sDomestic)',  # Sydney Airport -> Sydney
        r'^([A-Za-z\s]+)(?:\s\()'  # Sydney (SYD) -> Sydney
    ]
    
    for pattern in patterns:
        match = re.search(pattern, airport_name)
        if match:
            return match.group(1).strip()
    
    # Fallback: Remove common airport suffixes
    suffixes = [' Airport', ' International', ' Domestic', ' Regional']
    result = airport_name
    for suffix in suffixes:
        result = result.replace(suffix, '')
    
    # Remove anything in parentheses
    result = re.sub(r'\s*\([^)]*\)', '', result).strip()
    
    return result

def get_download_link(df, filename, text):
    """Generate a download link for a DataFrame."""
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{text}</a>'
    return href

def export_pdf_report(data, insights, city):
    """Generate a PDF report with flight data and insights."""
    pdf = FPDF()
    pdf.add_page()
    
    # Set up fonts
    pdf.set_font('Arial', 'B', 16)
    
    # Title
    pdf.cell(190, 10, f'Flight Market Analysis Report: {city}', 0, 1, 'C')
    pdf.ln(5)
    
    # Summary section
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(190, 10, 'Market Summary', 0, 1, 'L')
    pdf.set_font('Arial', '', 11)
    
    if 'summary' in insights:
        summary = insights['summary']
        
        summary_text = []
        if 'total_flights' in summary:
            summary_text.append(f"Total Flights Analyzed: {summary['total_flights']:,}")
        
        if 'domestic_percentage' in summary:
            summary_text.append(f"Domestic Flight Percentage: {summary['domestic_percentage']}%")
        
        if 'avg_price' in summary:
            summary_text.append(f"Average Flight Price: ${summary['avg_price']:,.2f}")
        
        if 'busiest_day' in summary and 'busiest_month' in summary:
            summary_text.append(f"Busiest Day: {summary['busiest_day']}")
            summary_text.append(f"Peak Month: {summary['busiest_month']}")
        
        for line in summary_text:
            pdf.cell(190, 7, line, 0, 1, 'L')
    
    pdf.ln(5)
    
    # AI Insights section
    if 'ai_insights' in insights and insights['ai_insights']:
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(190, 10, 'AI-Generated Insights', 0, 1, 'L')
        pdf.set_font('Arial', '', 11)
        
        ai_insights = insights['ai_insights']
        
        # Trend summary
        if 'trend_summary' in ai_insights and ai_insights['trend_summary']:
            pdf.multi_cell(190, 7, f"Trend Summary: {ai_insights['trend_summary']}")
            pdf.ln(3)
        
        # Market observations
        if 'market_observations' in ai_insights and ai_insights['market_observations']:
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(190, 7, 'Market Observations:', 0, 1, 'L')
            pdf.set_font('Arial', '', 11)
            
            for idx, obs in enumerate(ai_insights['market_observations'][:5], 1):
                pdf.multi_cell(190, 7, f"{idx}. {obs}")
            
            pdf.ln(3)
        
        # Hostel recommendations
        if 'hostel_recommendations' in ai_insights and ai_insights['hostel_recommendations']:
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(190, 7, 'Hostel Business Recommendations:', 0, 1, 'L')
            pdf.set_font('Arial', '', 11)
            
            for idx, rec in enumerate(ai_insights['hostel_recommendations'][:5], 1):
                pdf.multi_cell(190, 7, f"{idx}. {rec}")
            
            pdf.ln(3)
    
    # Popular Routes section
    if 'popular_routes' in insights and insights['popular_routes']:
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(190, 10, 'Top Flight Routes', 0, 1, 'L')
        pdf.set_font('Arial', '', 11)
        
        # Create simple table
        routes = insights['popular_routes'][:8]  # Limit to top 8 routes
        
        # Table header
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(40, 7, 'Origin', 1, 0, 'C')
        pdf.cell(40, 7, 'Destination', 1, 0, 'C')
        pdf.cell(30, 7, 'Frequency', 1, 0, 'C')
        pdf.cell(40, 7, 'Avg. Price', 1, 0, 'C')
        pdf.cell(40, 7, 'Type', 1, 1, 'C')
        
        # Table data
        pdf.set_font('Arial', '', 10)
        for route in routes:
            origin = route.get('origin', 'N/A')
            dest = route.get('destination', 'N/A')
            freq = route.get('frequency', 'N/A')
            price = f"${route.get('price', 0):,.2f}" if 'price' in route else 'N/A'
            route_type = 'Domestic' if route.get('is_domestic', False) else 'International'
            
            pdf.cell(40, 7, origin, 1, 0, 'C')
            pdf.cell(40, 7, dest, 1, 0, 'C')
            pdf.cell(30, 7, str(freq), 1, 0, 'C')
            pdf.cell(40, 7, price, 1, 0, 'C')
            pdf.cell(40, 7, route_type, 1, 1, 'C')
    
    # Market Opportunities section
    if 'market_opportunities' in insights and insights['market_opportunities']:
        pdf.ln(5)
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(190, 10, 'Market Opportunities', 0, 1, 'L')
        pdf.set_font('Arial', '', 11)
        
        opps = insights['market_opportunities'][:5]  # Limit to top 5 opportunities
        
        for idx, opp in enumerate(opps, 1):
            pdf.set_font('Arial', 'B', 11)
            if 'type' in opp:
                opp_type = opp['type']
                if opp_type == 'high_demand_high_price':
                    title = "High Demand & High Price Opportunity"
                elif opp_type == 'weekend_premium':
                    title = "Weekend Price Premium Opportunity"
                elif opp_type == 'seasonal_variation':
                    title = "Seasonal Price Variation Opportunity"
                else:
                    title = "Market Opportunity"
                
                pdf.cell(190, 7, f"{idx}. {title}", 0, 1, 'L')
            
            pdf.set_font('Arial', '', 10)
            if 'opportunity' in opp:
                pdf.multi_cell(190, 7, opp['opportunity'])
            
            details = []
            if 'origin' in opp and 'destination' in opp:
                details.append(f"Route: {opp['origin']} to {opp['destination']}")
            
            if 'median_price' in opp:
                details.append(f"Median Price: ${opp['median_price']:,.2f}")
            
            if 'price_difference' in opp:
                details.append(f"Weekend Price Premium: ${opp['price_difference']:,.2f}")
            
            if 'high_price_month' in opp and 'low_price_month' in opp:
                details.append(f"High Price Month: {opp['high_price_month']}")
                details.append(f"Low Price Month: {opp['low_price_month']}")
            
            for detail in details:
                pdf.cell(190, 7, detail, 0, 1, 'L')
            
            pdf.ln(3)
    
    # Footer with generation date
    pdf.set_y(-20)
    pdf.set_font('Arial', 'I', 8)
    pdf.cell(0, 10, f'Report generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', 0, 0, 'C')
    
    return pdf.output(dest='S').encode('latin1')

def get_pdf_download_link(pdf_data, filename, text):
    """Generate a download link for a PDF file."""
    b64 = base64.b64encode(pdf_data).decode()
    href = f'<a href="data:application/pdf;base64,{b64}" download="{filename}">{text}</a>'
    return href

@st.cache_data(ttl=3600)
def cache_data_wrapper(func, *args, **kwargs):
    """Wrapper for cached data functions."""
    return func(*args, **kwargs)

def setup_streamlit_page():
    """Set up the Streamlit page with custom styles and configurations."""
    # Set page config
    st.set_page_config(
        page_title="Airline Booking Market Demand",
        page_icon="✈️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS
    st.markdown("""
    <style>
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        h1, h2, h3 {
            color: #1E88E5;
        }
        .stMetric {
            background-color: #f0f2f6;
            border-radius: 5px;
            padding: 10px 15px;
            border-left: 3px solid #1E88E5;
        }
        .sidebar .sidebar-content {
            background-color: #f9f9f9;
        }
        .st-emotion-cache-16txtl3 h1 {
            margin-bottom: 0.5rem;
        }
        .st-emotion-cache-16txtl3 h2 {
            margin-top: 1rem;
            margin-bottom: 0.5rem;
        }
        .info-box {
            padding: 1rem;
            border-radius: 5px;
            margin-bottom: 1rem;
        }
        .info-box-blue {
            background-color: #e3f2fd;
            border-left: 4px solid #1E88E5;
        }
        .info-box-green {
            background-color: #e8f5e9;
            border-left: 4px solid #43a047;
        }
        .info-box-amber {
            background-color: #fff8e1;
            border-left: 4px solid #ffb300;
        }
    </style>
    """, unsafe_allow_html=True)
    
def display_info_box(message, box_type='blue'):
    """Display a styled info box."""
    st.markdown(f"""
    <div class="info-box info-box-{box_type}">
        {message}
    </div>
    """, unsafe_allow_html=True)

def check_api_keys():
    """Check if API keys are configured and return their status."""
    import config
    
    key_status = {
        'opensky': bool(config.OPENSKY_USERNAME and config.OPENSKY_PASSWORD),
        'aviationstack': bool(config.AVIATIONSTACK_API_KEY),
        'amadeus': bool(config.AMADEUS_API_KEY and config.AMADEUS_API_SECRET),
        'openai': bool(config.OPENAI_API_KEY),
        'google': bool(config.GOOGLE_API_KEY),
        'weather': bool(config.WEATHER_API_KEY)
    }
    
    return key_status 