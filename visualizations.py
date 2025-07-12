"""
Visualization module for the Airline Booking Market Demand application.
Generates charts and visual elements for the dashboard.
"""
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
import folium
from streamlit_folium import folium_static
import logging

# Import from other modules
import config

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# City coordinate mappings for map visualizations
CITY_COORDINATES = {
    # Australian cities
    "Sydney": (-33.8688, 151.2093),
    "Melbourne": (-37.8136, 144.9631),
    "Brisbane": (-27.4698, 153.0251),
    "Perth": (-31.9505, 115.8605),
    "Adelaide": (-34.9285, 138.6007),
    "Darwin": (-12.4634, 130.8456),
    "Gold Coast": (-28.0167, 153.4000),
    "Cairns": (-16.9186, 145.7781),
    "Canberra": (-35.2809, 149.1300),
    "Hobart": (-42.8821, 147.3272),
    
    # International destinations
    "Auckland": (-36.8509, 174.7645),
    "Singapore": (1.3521, 103.8198),
    "Bali": (-8.3405, 115.0920),  # Denpasar
    "Tokyo": (35.6762, 139.6503),
    "Hong Kong": (22.3193, 114.1694),
    "Los Angeles": (34.0522, -118.2437),
    "London": (51.5074, -0.1278),
    "Dubai": (25.2048, 55.2708),
    "Bangkok": (13.7563, 100.5018),
    "Kuala Lumpur": (3.1390, 101.6869)
}

# Airport code to city name mapping
AIRPORT_TO_CITY = {
    # Australian airports
    "SYD": "Sydney",
    "MEL": "Melbourne",
    "BNE": "Brisbane",
    "PER": "Perth",
    "ADL": "Adelaide",
    "DRW": "Darwin",
    "OOL": "Gold Coast",
    "CNS": "Cairns",
    "CBR": "Canberra",
    "HBA": "Hobart",
    
    # International airports
    "AKL": "Auckland",
    "SIN": "Singapore",
    "DPS": "Bali",
    "HND": "Tokyo",
    "HKG": "Hong Kong",
    "LAX": "Los Angeles",
    "LHR": "London",
    "DXB": "Dubai",
    "BKK": "Bangkok",
    "KUL": "Kuala Lumpur"
}

def get_city_name(airport_code):
    """Convert airport code to city name if available."""
    return AIRPORT_TO_CITY.get(airport_code, airport_code)

def get_city_coordinates(city_name):
    """Get coordinates for a city by name."""
    return CITY_COORDINATES.get(city_name, None)

def create_price_trend_chart(data, time_period='daily'):
    """Create a price trend line chart over time."""
    if time_period == 'daily' and 'daily_price_trends' in data:
        df = pd.DataFrame(data['daily_price_trends'])
        x_col = 'date'
        title = "Daily Flight Price Trends"
    elif time_period == 'weekly' and 'weekly_price_trends' in data:
        df = pd.DataFrame(data['weekly_price_trends'])
        # Create a week-year string for x-axis
        df['week_year'] = df['year'].astype(str) + '-W' + df['week'].astype(str).str.zfill(2)
        x_col = 'week_year'
        title = "Weekly Flight Price Trends"
    else:
        return None
    
    if df.empty:
        return None
    
    fig = px.line(
        df, 
        x=x_col, 
        y=['avg_price', 'median_price'],
        title=title,
        labels={
            'value': 'Price (AUD)',
            x_col: 'Date',
            'variable': 'Metric'
        }
    )
    
    # Add flight count as a secondary axis
    fig2 = px.bar(
        df, 
        x=x_col, 
        y='flight_count',
        opacity=0.5
    )
    
    fig.add_traces(fig2.data)
    
    # Set up secondary y-axis for flight count
    fig.update_layout(
        yaxis=dict(title='Price (AUD)'),
        yaxis2=dict(
            title='Number of Flights',
            overlaying='y',
            side='right'
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(l=20, r=20, t=40, b=20),
        hovermode="x unified"
    )
    
    # Update the added traces to use secondary y-axis
    fig.update_traces(yaxis="y2", selector=dict(name="flight_count"))
    
    return fig

def create_popular_routes_chart(data):
    """Create a bar chart of popular routes."""
    if 'popular_routes' not in data:
        return None
    
    df = pd.DataFrame(data['popular_routes'])
    
    if df.empty:
        return None
    
    # Convert airport codes to city names
    df['origin_city'] = df['origin'].apply(get_city_name)
    df['destination_city'] = df['destination'].apply(get_city_name)
    
    # Create route labels
    df['route'] = df['origin_city'] + ' to ' + df['destination_city']
    
    # Create color based on domestic/international
    df['route_type'] = df['is_domestic'].apply(lambda x: 'Domestic' if x else 'International')
    
    fig = px.bar(
        df.sort_values('frequency', ascending=True).tail(10),  # Show top 10 in ascending order
        y='route',
        x='frequency',
        color='route_type',
        title="Most Popular Flight Routes",
        labels={
            'route': 'Route',
            'frequency': 'Number of Flights',
            'route_type': 'Route Type'
        },
        color_discrete_map={
            'Domestic': '#3366CC',
            'International': '#FF9900'
        }
    )
    
    fig.update_layout(
        xaxis_title="Number of Flights",
        yaxis_title="",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    return fig

def create_seasonal_heatmap(data):
    """Create a heatmap showing seasonal demand patterns."""
    if 'monthly_patterns' not in data:
        return None
    
    df = pd.DataFrame(data['monthly_patterns'])
    
    if df.empty:
        return None
    
    # Add month names
    month_names = {
        1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
        7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'
    }
    df['month_name'] = df['month'].map(month_names)
    
    # Sort by month number
    df = df.sort_values('month')
    
    # Create heatmap using flight_count
    fig = go.Figure(data=go.Heatmap(
        z=[df['flight_count']],
        x=df['month_name'],
        colorscale='Viridis',
        showscale=True
    ))
    
    fig.update_layout(
        title="Seasonal Flight Demand Patterns",
        xaxis_title="Month",
        yaxis_visible=False,
        margin=dict(l=20, r=20, t=40, b=20),
        height=200
    )
    
    return fig

def create_day_of_week_chart(data):
    """Create a bar chart showing flight patterns by day of week."""
    if 'day_of_week_patterns' not in data:
        return None
    
    df = pd.DataFrame(data['day_of_week_patterns'])
    
    if df.empty:
        return None
    
    # Sort by day of week
    df = df.sort_values('day_of_week')
    
    fig = px.bar(
        df,
        x='day_name',
        y='flight_count',
        title="Flight Frequency by Day of Week",
        labels={
            'day_name': 'Day of Week',
            'flight_count': 'Number of Flights'
        },
        color='flight_count',
        color_continuous_scale='Viridis'
    )
    
    if 'avg_price' in df.columns:
        # Add price line on secondary axis
        fig2 = px.line(
            df, 
            x='day_name', 
            y='avg_price',
            markers=True
        )
        
        fig.add_traces(fig2.data)
        
        # Set up secondary y-axis for price
        fig.update_layout(
            yaxis=dict(title='Number of Flights'),
            yaxis2=dict(
                title='Average Price (AUD)',
                overlaying='y',
                side='right'
            )
        )
        
        # Update the added traces to use secondary y-axis
        fig.update_traces(yaxis="y2", selector=dict(name="avg_price"))
    
    fig.update_layout(
        xaxis_title="Day of Week",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    return fig

def create_price_distribution_chart(data):
    """Create a histogram showing price distribution."""
    if 'price_categories' not in data:
        return None
    
    df = pd.DataFrame(data['price_categories'])
    
    if df.empty:
        return None
    
    # Sort categories in meaningful order
    category_order = ['Budget', 'Economy', 'Premium', 'Luxury']
    df['category'] = pd.Categorical(df['category'], categories=category_order, ordered=True)
    df = df.sort_values('category')
    
    fig = px.bar(
        df,
        x='category',
        y='count',
        title="Flight Count by Price Category",
        labels={
            'category': 'Price Category',
            'count': 'Number of Flights'
        },
        color='category',
        color_discrete_map={
            'Budget': '#3366CC',
            'Economy': '#33CC99',
            'Premium': '#FFCC33',
            'Luxury': '#FF6633'
        }
    )
    
    fig.update_layout(
        xaxis_title="Price Category",
        yaxis_title="Number of Flights",
        showlegend=False,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    return fig

def create_flight_map(data, map_type='popular_routes'):
    """Create an interactive map visualization of routes or airports."""
    if map_type == 'popular_routes' and 'popular_routes' in data:
        return create_route_map(data['popular_routes'])
    else:
        return None

def create_route_map(routes_data, top_n=10):
    """Create an interactive map showing flight routes."""
    if not routes_data:
        return None
    
    df = pd.DataFrame(routes_data)
    
    if len(df) > top_n:
        df = df.sort_values('frequency', ascending=False).head(top_n)
    
    # Create a base map centered on Australia
    m = folium.Map(location=[-25.2744, 133.7751], zoom_start=4)
    
    # Add routes
    for _, route in df.iterrows():
        origin_code = route['origin']
        dest_code = route['destination']
        
        # Convert codes to city names
        origin_city = get_city_name(origin_code)
        dest_city = get_city_name(dest_code)
        
        # Get coordinates
        origin_coords = get_city_coordinates(origin_city)
        dest_coords = get_city_coordinates(dest_city)
        
        if origin_coords and dest_coords:
            # Add markers for origin and destination
            folium.CircleMarker(
                location=origin_coords,
                radius=5,
                color='blue',
                fill=True,
                fill_opacity=0.7,
                popup=f"{origin_city} ({origin_code})"
            ).add_to(m)
            
            folium.CircleMarker(
                location=dest_coords,
                radius=5,
                color='red',
                fill=True,
                fill_opacity=0.7,
                popup=f"{dest_city} ({dest_code})"
            ).add_to(m)
            
            # Add line connecting the cities
            line_color = 'blue' if route.get('is_domestic', False) else 'red'
            folium.PolyLine(
                locations=[origin_coords, dest_coords],
                color=line_color,
                weight=2 + min(route.get('frequency', 1) / 10, 8),  # Scale line width by frequency
                opacity=0.7,
                popup=f"{origin_city} to {dest_city}: {route.get('frequency', 'N/A')} flights"
            ).add_to(m)
    
    # Add a legend
    legend_html = '''
    <div style="position: fixed; bottom: 50px; left: 50px; z-index: 1000; background-color: white; padding: 10px; border: 1px solid grey;">
    <h4>Route Legend</h4>
    <div><i style="background: blue; width: 15px; height: 2px; display: inline-block;"></i> Domestic Routes</div>
    <div><i style="background: red; width: 15px; height: 2px; display: inline-block;"></i> International Routes</div>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))
    
    return m

def create_price_scatter(data):
    """Create a scatter plot of price vs. demand."""
    if 'popular_routes' not in data:
        return None
    
    routes = pd.DataFrame(data['popular_routes'])
    
    if 'origin' not in routes.columns or 'destination' not in routes.columns:
        return None
    
    # Extract price data if available
    if 'price' in routes.columns:
        fig = px.scatter(
            routes,
            x='frequency',
            y='price',
            color='is_domestic',
            size='frequency',
            hover_name='destination',
            labels={
                'frequency': 'Flight Frequency',
                'price': 'Average Price (AUD)',
                'is_domestic': 'Route Type'
            },
            title="Price vs. Demand by Route",
            color_discrete_map={
                True: '#3366CC',
                False: '#FF9900'
            }
        )
        
        fig.update_layout(
            xaxis_title="Flight Frequency (Demand)",
            yaxis_title="Average Price (AUD)",
            legend_title="Route Type",
            margin=dict(l=20, r=20, t=40, b=20)
        )
        
        # Update legend labels
        fig.update_layout(
            legend=dict(
                title="Route Type",
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                traceorder="normal",
                itemsizing="constant"
            )
        )
        
        # Update hover template
        fig.update_traces(
            hovertemplate="<b>%{hovertext}</b><br>Frequency: %{x}<br>Price: $%{y:.2f}<extra></extra>"
        )
        
        return fig
    
    return None

def create_opportunity_table(opportunities):
    """Create a formatted table of market opportunities."""
    if not opportunities:
        return None
    
    # Create a DataFrame for display
    df = pd.DataFrame(opportunities)
    
    if df.empty:
        return None
    
    # Select and rename columns for display
    display_cols = [
        'type', 'origin', 'destination', 'opportunity'
    ]
    
    # Add additional columns based on opportunity type
    if 'high_demand_high_price' in df['type'].values:
        if 'median_price' in df.columns:
            display_cols.append('median_price')
    
    if 'weekend_premium' in df['type'].values:
        if 'price_difference' in df.columns:
            display_cols.append('price_difference')
    
    if 'seasonal_variation' in df['type'].values:
        if 'high_price_month' in df.columns and 'low_price_month' in df.columns:
            display_cols.extend(['high_price_month', 'low_price_month'])
    
    # Filter columns that exist in the DataFrame
    display_cols = [col for col in display_cols if col in df.columns]
    
    return df[display_cols]

def create_market_overview_metrics(data):
    """Create a set of metrics for the market overview."""
    if 'summary' not in data:
        return None
    
    summary = data['summary']
    
    metrics = []
    
    # Total flights
    if 'total_flights' in summary:
        metrics.append({
            'label': 'Total Flights',
            'value': f"{summary['total_flights']:,}"
        })
    
    # Domestic vs International
    if 'domestic_percentage' in summary:
        metrics.append({
            'label': 'Domestic Flights',
            'value': f"{summary['domestic_percentage']}%"
        })
    
    # Average prices
    if 'avg_domestic_price' in summary and 'avg_international_price' in summary:
        metrics.append({
            'label': 'Avg. Domestic Price',
            'value': f"${summary['avg_domestic_price']:,.2f}"
        })
        metrics.append({
            'label': 'Avg. International Price',
            'value': f"${summary['avg_international_price']:,.2f}"
        })
    elif 'avg_price' in summary:
        metrics.append({
            'label': 'Average Price',
            'value': f"${summary['avg_price']:,.2f}"
        })
    
    # Busiest day and month
    if 'busiest_day' in summary:
        metrics.append({
            'label': 'Busiest Day',
            'value': summary['busiest_day']
        })
    
    if 'busiest_month' in summary:
        metrics.append({
            'label': 'Peak Month',
            'value': summary['busiest_month']
        })
    
    return metrics 