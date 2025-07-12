"""
Data processing module for the Airline Booking Market Demand application.
Handles data cleaning, analysis, and insights generation.
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from collections import Counter
import re
import json

# Import from other modules
import config

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DataProcessor:
    """Process and analyze flight data to extract market insights."""
    
    def __init__(self, raw_data=None):
        """Initialize with optional raw data."""
        self.raw_data = raw_data
        self.processed_data = None
        self.insights = {}
    
    def load_data(self, data):
        """Load raw data for processing."""
        self.raw_data = data
        return self
    
    def clean_data(self):
        """Clean and prepare the raw flight data."""
        if self.raw_data is None or len(self.raw_data) == 0:
            logger.warning("No data to clean")
            return self
        
        df = self.raw_data.copy()
        
        # Handle missing values
        if 'price' in df.columns and df['price'].isna().any():
            # Fill missing prices with median values for the same route
            route_medians = df.groupby(['origin', 'destination'])['price'].transform('median')
            df['price'].fillna(route_medians, inplace=True)
            # Any remaining NaNs get overall median
            df['price'].fillna(df['price'].median(), inplace=True)
        
        # Ensure dates are in datetime format
        if 'flight_date' in df.columns:
            try:
                df['flight_date'] = pd.to_datetime(df['flight_date'])
            except:
                logger.warning("Could not convert flight_date to datetime")
        
        # Remove duplicate flights
        if len(df.columns) > 3:  # Only if we have enough columns to identify duplicates
            df = df.drop_duplicates(subset=['flight_date', 'flight_time', 'origin', 'destination', 'airline'], 
                                   keep='first')
        
        # Remove outliers in price (if price exists)
        if 'price' in df.columns:
            # Calculate IQR
            Q1 = df['price'].quantile(0.25)
            Q3 = df['price'].quantile(0.75)
            IQR = Q3 - Q1
            
            # Define bounds
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            # Filter outliers
            df = df[(df['price'] >= lower_bound) & (df['price'] <= upper_bound)]
        
        # Add day of week if we have flight date
        if 'flight_date' in df.columns and pd.api.types.is_datetime64_any_dtype(df['flight_date']):
            df['day_of_week'] = df['flight_date'].dt.dayofweek
            df['month'] = df['flight_date'].dt.month
            df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
        
        self.processed_data = df
        return self
    
    def analyze_popular_routes(self, top_n=10):
        """Analyze and identify the most popular routes."""
        if self.processed_data is None:
            logger.warning("No processed data available for route analysis")
            return None
        
        # Count route frequencies
        route_counts = self.processed_data.groupby(['origin', 'destination']).size().reset_index(name='frequency')
        
        # Sort by frequency and get top N
        popular_routes = route_counts.sort_values('frequency', ascending=False).head(top_n)
        
        # Add route type (domestic/international)
        def is_domestic(row):
            # Check if both origin and destination are Australian airports
            origin_is_aus = row['origin'] in config.AUSTRALIAN_CITIES.values()
            dest_is_aus = row['destination'] in config.AUSTRALIAN_CITIES.values()
            return origin_is_aus and dest_is_aus
        
        popular_routes['is_domestic'] = popular_routes.apply(is_domestic, axis=1)
        
        # Store in insights
        self.insights['popular_routes'] = popular_routes.to_dict('records')
        return popular_routes
    
    def analyze_price_trends(self):
        """Analyze price trends over time."""
        if self.processed_data is None or 'price' not in self.processed_data.columns:
            logger.warning("No price data available for trend analysis")
            return None
        
        df = self.processed_data
        
        # Ensure we have datetime for analysis
        if 'flight_date' in df.columns and pd.api.types.is_datetime64_any_dtype(df['flight_date']):
            # Daily average price
            daily_avg = df.groupby('flight_date')['price'].agg(['mean', 'median', 'count']).reset_index()
            daily_avg.columns = ['date', 'avg_price', 'median_price', 'flight_count']
            
            # Weekly average price
            df['week'] = df['flight_date'].dt.isocalendar().week
            df['year'] = df['flight_date'].dt.isocalendar().year
            weekly_avg = df.groupby(['year', 'week'])['price'].agg(['mean', 'median', 'count']).reset_index()
            weekly_avg.columns = ['year', 'week', 'avg_price', 'median_price', 'flight_count']
            
            # Store in insights
            self.insights['daily_price_trends'] = daily_avg.to_dict('records')
            self.insights['weekly_price_trends'] = weekly_avg.to_dict('records')
            
            return {
                'daily': daily_avg,
                'weekly': weekly_avg
            }
        else:
            logger.warning("Flight date not available for trend analysis")
            return None
    
    def analyze_seasonal_patterns(self):
        """Analyze seasonal patterns in flight data."""
        if self.processed_data is None:
            logger.warning("No processed data available for seasonal analysis")
            return None
        
        df = self.processed_data
        
        # Check if we have necessary date information
        if 'month' not in df.columns:
            if 'flight_date' in df.columns and pd.api.types.is_datetime64_any_dtype(df['flight_date']):
                df['month'] = df['flight_date'].dt.month
            else:
                logger.warning("Date information not available for seasonal analysis")
                return None
        
        # Monthly patterns
        monthly_stats = df.groupby('month').agg({
            'price': ['mean', 'median', 'count'] if 'price' in df.columns else 'count'
        }).reset_index()
        
        # Rename columns for clarity
        if 'price' in df.columns:
            monthly_stats.columns = ['month', 'avg_price', 'median_price', 'flight_count']
        else:
            monthly_stats.columns = ['month', 'flight_count']
        
        # Day of week patterns if available
        if 'day_of_week' in df.columns:
            day_stats = df.groupby('day_of_week').agg({
                'price': ['mean', 'median', 'count'] if 'price' in df.columns else 'count'
            }).reset_index()
            
            # Rename columns
            if 'price' in df.columns:
                day_stats.columns = ['day_of_week', 'avg_price', 'median_price', 'flight_count']
            else:
                day_stats.columns = ['day_of_week', 'flight_count']
            
            # Map day numbers to names
            day_names = {0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday', 
                        4: 'Friday', 5: 'Saturday', 6: 'Sunday'}
            day_stats['day_name'] = day_stats['day_of_week'].map(day_names)
            
            # Store in insights
            self.insights['day_of_week_patterns'] = day_stats.to_dict('records')
        
        # Store monthly patterns in insights
        self.insights['monthly_patterns'] = monthly_stats.to_dict('records')
        
        # Calculate peak travel periods (top 2 months)
        peak_months = monthly_stats.sort_values('flight_count', ascending=False).head(2)['month'].tolist()
        peak_month_names = [datetime(2000, m, 1).strftime('%B') for m in peak_months]
        self.insights['peak_travel_periods'] = peak_month_names
        
        return {
            'monthly': monthly_stats,
            'day_of_week': day_stats if 'day_of_week' in df.columns else None,
            'peak_months': peak_months
        }
    
    def analyze_price_distribution(self):
        """Analyze price distribution and categories."""
        if self.processed_data is None or 'price' not in self.processed_data.columns:
            logger.warning("No price data available for distribution analysis")
            return None
        
        df = self.processed_data
        
        # Calculate price distribution statistics
        price_stats = {
            'min': df['price'].min(),
            'max': df['price'].max(),
            'mean': df['price'].mean(),
            'median': df['price'].median(),
            'std': df['price'].std(),
            'q1': df['price'].quantile(0.25),
            'q3': df['price'].quantile(0.75)
        }
        
        # Create price categories
        bins = [0, 200, 500, 1000, float('inf')]
        labels = ['Budget', 'Economy', 'Premium', 'Luxury']
        df['price_category'] = pd.cut(df['price'], bins=bins, labels=labels)
        
        # Count flights by price category
        price_categories = df['price_category'].value_counts().reset_index()
        price_categories.columns = ['category', 'count']
        
        # Store in insights
        self.insights['price_stats'] = price_stats
        self.insights['price_categories'] = price_categories.to_dict('records')
        
        return {
            'stats': price_stats,
            'categories': price_categories
        }
    
    def analyze_market_opportunities(self):
        """Identify potential market opportunities from the flight data."""
        if self.processed_data is None:
            logger.warning("No processed data available for opportunity analysis")
            return None
        
        df = self.processed_data
        opportunities = []
        
        # Opportunity 1: Routes with high demand but limited flights
        if 'origin' in df.columns and 'destination' in df.columns:
            route_demand = df.groupby(['origin', 'destination']).size().reset_index(name='frequency')
            high_demand = route_demand[route_demand['frequency'] > route_demand['frequency'].median()]
            
            # Cross-reference with price data if available
            if 'price' in df.columns:
                route_prices = df.groupby(['origin', 'destination'])['price'].median().reset_index()
                route_analysis = high_demand.merge(route_prices, on=['origin', 'destination'])
                
                # Find routes with high demand and high prices (opportunity for competitive entry)
                high_opportunity = route_analysis[route_analysis['price'] > route_analysis['price'].median()]
                for _, row in high_opportunity.head(5).iterrows():
                    opportunities.append({
                        'type': 'high_demand_high_price',
                        'origin': row['origin'],
                        'destination': row['destination'],
                        'frequency': row['frequency'],
                        'median_price': row['price'],
                        'opportunity': 'High demand route with above-average prices'
                    })
        
        # Opportunity 2: Weekend vs weekday price differentials
        if 'is_weekend' in df.columns and 'price' in df.columns:
            weekend_premium = df.groupby(['origin', 'destination', 'is_weekend'])['price'].median().reset_index()
            
            # Reshape to have weekday and weekend prices in separate columns
            weekend_premium = weekend_premium.pivot_table(
                index=['origin', 'destination'], 
                columns='is_weekend', 
                values='price'
            ).reset_index()
            
            if 0 in weekend_premium.columns and 1 in weekend_premium.columns:
                weekend_premium.columns = ['origin', 'destination', 'weekday_price', 'weekend_price']
                weekend_premium['price_difference'] = weekend_premium['weekend_price'] - weekend_premium['weekday_price']
                weekend_premium['price_ratio'] = weekend_premium['weekend_price'] / weekend_premium['weekday_price']
                
                # Find routes with significant weekend premium
                weekend_opportunities = weekend_premium[weekend_premium['price_ratio'] > 1.3].sort_values(
                    'price_difference', ascending=False
                )
                
                for _, row in weekend_opportunities.head(5).iterrows():
                    opportunities.append({
                        'type': 'weekend_premium',
                        'origin': row['origin'],
                        'destination': row['destination'],
                        'weekday_price': row['weekday_price'],
                        'weekend_price': row['weekend_price'],
                        'price_difference': row['price_difference'],
                        'opportunity': 'Significant price premium on weekends'
                    })
        
        # Opportunity 3: Seasonal pricing opportunities
        if 'month' in df.columns and 'price' in df.columns:
            monthly_prices = df.groupby(['origin', 'destination', 'month'])['price'].median().reset_index()
            
            # Find routes with high seasonal price variation
            for route in monthly_prices['origin'].unique():
                route_data = monthly_prices[monthly_prices['origin'] == route]
                if len(route_data) > 1:
                    price_range = route_data['price'].max() - route_data['price'].min()
                    price_ratio = route_data['price'].max() / route_data['price'].min() if route_data['price'].min() > 0 else 1
                    
                    if price_ratio > 1.5:  # Significant seasonal variation
                        dest = route_data.iloc[route_data['price'].idxmax()]['destination']
                        max_month = route_data.iloc[route_data['price'].idxmax()]['month']
                        min_month = route_data.iloc[route_data['price'].idxmin()]['month']
                        
                        opportunities.append({
                            'type': 'seasonal_variation',
                            'origin': route,
                            'destination': dest,
                            'high_price_month': datetime(2000, max_month, 1).strftime('%B'),
                            'low_price_month': datetime(2000, min_month, 1).strftime('%B'),
                            'price_ratio': price_ratio,
                            'opportunity': f'Significant seasonal price variation (ratio: {price_ratio:.2f}x)'
                        })
        
        # Store opportunities in insights
        self.insights['market_opportunities'] = opportunities
        
        return opportunities
    
    def generate_summary_insights(self):
        """Generate summary insights for the dashboard."""
        insights = {}
        
        if self.processed_data is None:
            logger.warning("No processed data available for summary insights")
            return insights
        
        df = self.processed_data
        
        # Basic flight statistics
        insights['total_flights'] = len(df)
        
        if 'is_domestic' in df.columns:
            domestic_count = df['is_domestic'].sum()
            insights['domestic_flights'] = int(domestic_count)
            insights['international_flights'] = int(len(df) - domestic_count)
            insights['domestic_percentage'] = round((domestic_count / len(df)) * 100, 1)
        
        if 'price' in df.columns:
            insights['avg_price'] = round(df['price'].mean(), 2)
            insights['median_price'] = round(df['price'].median(), 2)
            
            if 'is_domestic' in df.columns:
                domestic_df = df[df['is_domestic'] == True]
                international_df = df[df['is_domestic'] == False]
                
                if len(domestic_df) > 0:
                    insights['avg_domestic_price'] = round(domestic_df['price'].mean(), 2)
                
                if len(international_df) > 0:
                    insights['avg_international_price'] = round(international_df['price'].mean(), 2)
        
        # Most frequent origins and destinations
        if 'origin' in df.columns:
            top_origins = df['origin'].value_counts().head(5).to_dict()
            insights['top_origins'] = [{'code': k, 'count': v} for k, v in top_origins.items()]
            
        if 'destination' in df.columns:
            top_destinations = df['destination'].value_counts().head(5).to_dict()
            insights['top_destinations'] = [{'code': k, 'count': v} for k, v in top_destinations.items()]
        
        # Map airport codes to city names where possible
        airport_to_city = {v: k for k, v in config.AUSTRALIAN_CITIES.items()}
        airport_to_city.update({v: k for k, v in config.POPULAR_INTERNATIONAL_DESTINATIONS.items()})
        
        if 'top_origins' in insights:
            for item in insights['top_origins']:
                item['city'] = airport_to_city.get(item['code'], item['code'])
                
        if 'top_destinations' in insights:
            for item in insights['top_destinations']:
                item['city'] = airport_to_city.get(item['code'], item['code'])
        
        # Time-based insights
        if 'day_of_week' in df.columns:
            busiest_day_idx = df['day_of_week'].value_counts().idxmax()
            day_names = {0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday', 
                        4: 'Friday', 5: 'Saturday', 6: 'Sunday'}
            insights['busiest_day'] = day_names.get(busiest_day_idx)
            
            if 'is_weekend' in df.columns and 'price' in df.columns:
                weekend_df = df[df['is_weekend'] == 1]
                weekday_df = df[df['is_weekend'] == 0]
                
                if len(weekend_df) > 0 and len(weekday_df) > 0:
                    insights['weekend_price_premium'] = round(
                        (weekend_df['price'].mean() / weekday_df['price'].mean() - 1) * 100, 1
                    )
        
        if 'month' in df.columns:
            busiest_month_idx = df['month'].value_counts().idxmax()
            insights['busiest_month'] = datetime(2000, busiest_month_idx, 1).strftime('%B')
        
        # Store the complete insights
        self.insights['summary'] = insights
        
        return insights
    
    def run_all_analyses(self):
        """Run all analysis methods to generate comprehensive insights."""
        if self.raw_data is None:
            logger.warning("No data available for analysis")
            return self
        
        # Clean data first
        self.clean_data()
        
        # Run all analyses
        self.analyze_popular_routes()
        self.analyze_price_trends()
        self.analyze_seasonal_patterns()
        self.analyze_price_distribution()
        self.analyze_market_opportunities()
        self.generate_summary_insights()
        
        return self
    
    def get_insights(self, category=None):
        """Get generated insights, optionally filtered by category."""
        if not self.insights:
            logger.warning("No insights available. Run analyses first.")
            return {}
        
        if category and category in self.insights:
            return self.insights[category]
        
        return self.insights


def generate_ai_insights(data, ai_provider='mock'):
    """Generate AI-powered insights from the processed data."""
    if ai_provider == 'openai' and config.OPENAI_API_KEY:
        return generate_openai_insights(data)
    elif ai_provider == 'gemini' and config.GOOGLE_API_KEY:
        return generate_gemini_insights(data)
    else:
        # Fall back to mock insights
        return generate_mock_ai_insights(data)

def generate_openai_insights(data):
    """Generate insights using OpenAI API."""
    # Implementation would depend on openai package
    # This is a placeholder
    return {
        'trend_summary': 'OpenAI trend analysis would be here',
        'recommendations': ['Recommendation 1', 'Recommendation 2']
    }

def generate_gemini_insights(data):
    """Generate insights using Google Gemini API."""
    # Implementation would depend on google-generativeai package
    # This is a placeholder
    return {
        'trend_summary': 'Google Gemini trend analysis would be here',
        'recommendations': ['Recommendation 1', 'Recommendation 2']
    }

def generate_mock_ai_insights(data):
    """Generate mock AI insights when no AI provider is available."""
    insights = {
        'trend_summary': '',
        'market_observations': [],
        'hostel_recommendations': [],
        'seasonal_strategies': []
    }
    
    # Generate trend summary
    if 'summary' in data:
        summary = data['summary']
        
        if 'domestic_percentage' in summary:
            domestic_pct = summary['domestic_percentage']
            if domestic_pct > 70:
                insights['trend_summary'] += f"The market is predominantly domestic ({domestic_pct}% of flights), suggesting strong intra-Australian travel demand. "
            else:
                insights['trend_summary'] += f"There's a healthy mix of domestic ({domestic_pct}%) and international flights, indicating diverse travel patterns. "
        
        if 'busiest_day' in summary and 'busiest_month' in summary:
            insights['trend_summary'] += f"{summary['busiest_day']} is the most popular day for flights, and {summary['busiest_month']} shows the highest travel activity. "
        
        if 'weekend_price_premium' in summary:
            premium = summary['weekend_price_premium']
            insights['trend_summary'] += f"Weekend flights command a {premium}% price premium over weekday flights. "
    
    # Generate market observations
    if 'popular_routes' in data:
        routes = data['popular_routes'][:5]  # Top 5 routes
        for route in routes:
            origin = route.get('origin', '')
            dest = route.get('destination', '')
            insights['market_observations'].append(
                f"High demand observed between {origin} and {dest}, suggesting strong traveler interest in this route."
            )
    
    # Generate hostel recommendations
    if 'market_opportunities' in data:
        opportunities = data['market_opportunities'][:3]  # Top 3 opportunities
        for opportunity in opportunities:
            opp_type = opportunity.get('type', '')
            if opp_type == 'high_demand_high_price':
                dest = opportunity.get('destination', '')
                insights['hostel_recommendations'].append(
                    f"Consider expanding hostel capacity near {dest} airport due to high demand and premium pricing in this market."
                )
            elif opp_type == 'seasonal_variation':
                high_month = opportunity.get('high_price_month', '')
                dest = opportunity.get('destination', '')
                insights['hostel_recommendations'].append(
                    f"Implement dynamic pricing for hostels near {dest} during {high_month} to capitalize on peak travel season pricing."
                )
    
    # Generate seasonal strategies
    if 'monthly_patterns' in data:
        if isinstance(data['monthly_patterns'], list) and len(data['monthly_patterns']) > 0:
            # Find months with highest flight counts
            flight_counts = {item['month']: item.get('flight_count', 0) for item in data['monthly_patterns']}
            peak_months = sorted(flight_counts.items(), key=lambda x: x[1], reverse=True)[:2]
            
            for month_num, _ in peak_months:
                month_name = datetime(2000, month_num, 1).strftime('%B')
                insights['seasonal_strategies'].append(
                    f"Increase hostel capacity and rates during {month_name}, which shows significantly higher travel volume."
                )
        
        # Add a general seasonal strategy
        insights['seasonal_strategies'].append(
            "Consider offering package deals with local attractions during shoulder seasons to boost occupancy rates."
        )
    
    return insights 