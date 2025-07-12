"""
Airline Booking Market Demand Analysis Application

A Streamlit web application that analyzes airline booking market demand data
for a hostel business group across Australian cities.

Main features:
- Flight data visualization and analysis
- Market demand insights and trends
- Business intelligence for hostel placement decisions
- Interactive filters and controls
- Data export capabilities
"""
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import time
import os
import io
from fpdf import FPDF

# Import application modules
import data_collector as dc
import data_processor as dp
import visualizations as viz
import utils
import config

# Set up page config and styling
utils.setup_streamlit_page()

# Initialize session state if needed
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
if 'selected_city' not in st.session_state:
    st.session_state.selected_city = config.DEFAULT_CITY
if 'date_range' not in st.session_state:
    st.session_state.date_range = config.DEFAULT_DATE_RANGE
if 'insights' not in st.session_state:
    st.session_state.insights = {}
if 'raw_data' not in st.session_state:
    st.session_state.raw_data = None

# Main layout structure
def main():
    # App header
    st.title("✈️ Airline Booking Market Demand Analysis")
    st.markdown("""
    Analyze flight market demand to make data-driven hostel business decisions across Australian cities.
    """)
    
    # Sidebar for inputs and controls
    with st.sidebar:
        st.header("Analysis Controls")
        
        # City selection
        city_options = list(config.AUSTRALIAN_CITIES.keys())
        city = st.selectbox(
            "Select City", 
            options=city_options,
            index=city_options.index(st.session_state.selected_city) if st.session_state.selected_city in city_options else 0
        )
        city_code = config.AUSTRALIAN_CITIES[city]
        
        # Date range selection
        date_range = st.slider(
            "Analysis Period (days)", 
            min_value=7, 
            max_value=90, 
            value=st.session_state.date_range,
            step=7
        )
        
        # Filter options
        st.subheader("Filters")
        route_type = st.multiselect(
            "Route Type",
            options=["Domestic", "International"],
            default=["Domestic", "International"]
        )
        
        # Price range filter (if we have price data)
        if st.session_state.data_loaded and st.session_state.raw_data is not None and 'price' in st.session_state.raw_data.columns:
            min_price = float(st.session_state.raw_data['price'].min())
            max_price = float(st.session_state.raw_data['price'].max())
            
            price_range = st.slider(
                "Price Range (AUD)",
                min_value=min_price,
                max_value=max_price,
                value=(min_price, max_price),
                step=50.0
            )
        else:
            price_range = (0, 5000)
        
        # Load data button
        if st.button("Load Data"):
            with st.spinner("Loading flight data..."):
                # Get flight data
                data = dc.get_flight_data(city_code, days=date_range)
                
                # Store in session state
                st.session_state.raw_data = data
                st.session_state.selected_city = city
                st.session_state.date_range = date_range
                st.session_state.data_loaded = True
                
                # Process data and generate insights
                processor = dp.DataProcessor()
                processor.load_data(data).run_all_analyses()
                
                # Store insights
                st.session_state.insights = processor.get_insights()
                
                # Generate AI insights
                ai_insights = dp.generate_ai_insights(st.session_state.insights)
                st.session_state.insights['ai_insights'] = ai_insights
                
                st.success(f"Loaded data for {city} ({len(data)} flights)")
        
        # Data export section
        if st.session_state.data_loaded:
            st.subheader("Export Options")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("Export CSV"):
                    if st.session_state.raw_data is not None:
                        csv_data = st.session_state.raw_data.to_csv(index=False)
                        st.download_button(
                            label="Download CSV",
                            data=csv_data,
                            file_name=f"flight_data_{city}_{datetime.now().strftime('%Y%m%d')}.csv",
                            mime="text/csv"
                        )
            
            with col2:
                if st.button("Export Report"):
                    if st.session_state.insights:
                        try:
                            pdf_data = utils.export_pdf_report(
                                st.session_state.raw_data,
                                st.session_state.insights,
                                city
                            )
                            
                            st.download_button(
                                label="Download PDF",
                                data=pdf_data,
                                file_name=f"flight_report_{city}_{datetime.now().strftime('%Y%m%d')}.pdf",
                                mime="application/pdf"
                            )
                        except Exception as e:
                            st.error(f"Error generating PDF: {str(e)}")
        
        # About section
        st.sidebar.markdown("---")
        st.sidebar.info(
            "This application analyzes airline booking market demand to help "
            "hostel businesses make data-driven decisions for expansion and marketing."
        )
    
    # Main content area
    if not st.session_state.data_loaded:
        # Show welcome screen with instructions
        st.info("👈 Select a city and analysis period in the sidebar, then click 'Load Data' to begin.")
        
        st.subheader("Application Features")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            - **Market Demand Analysis**: Visualize flight patterns and demand trends
            - **Price Trend Analysis**: Track pricing fluctuations over time
            - **Seasonal Patterns**: Identify peak travel periods
            - **Business Insights**: Get AI-powered recommendations for hostel operations
            """)
        
        with col2:
            st.markdown("""
            - **Interactive Maps**: View route popularity visually
            - **Data Export**: Download data and reports for offline analysis
            - **Customizable Filters**: Focus on specific market segments
            - **Australian Market Focus**: Specialized for major Australian cities
            """)
        
        # Show sample image
        st.image("https://storage.googleapis.com/gweb-cloudblog-publish/images/travel_predictions.max-1000x1000.jpg", 
                caption="Sample visualization of flight demand patterns")
        
    else:
        # Apply filters to the data
        filtered_data = filter_data(st.session_state.raw_data, route_type, price_range)
        
        # Check if we have data after filtering
        if filtered_data.empty:
            st.warning("No data available after applying filters. Try adjusting your filter criteria.")
            return
            
        # Display dashboard with tabs
        tab1, tab2, tab3, tab4 = st.tabs(["Market Overview", "Route Analysis", "Price Analysis", "Business Insights"])
        
        with tab1:
            display_market_overview(filtered_data)
            
        with tab2:
            display_route_analysis(filtered_data)
            
        with tab3:
            display_price_analysis(filtered_data)
            
        with tab4:
            display_business_insights()

def filter_data(data, route_types, price_range):
    """Apply filters to the flight data."""
    if data is None or data.empty:
        return pd.DataFrame()
    
    # Create a copy to avoid modifying the original
    filtered = data.copy()
    
    # Apply route type filter
    if "Domestic" in route_types and "International" in route_types:
        pass  # No filtering needed, keep both
    elif "Domestic" in route_types:
        filtered = filtered[filtered['is_domestic'] == True]
    elif "International" in route_types:
        filtered = filtered[filtered['is_domestic'] == False]
    
    # Apply price range filter if price column exists
    if 'price' in filtered.columns:
        filtered = filtered[(filtered['price'] >= price_range[0]) & 
                           (filtered['price'] <= price_range[1])]
    
    return filtered

def display_market_overview(data):
    """Display the market overview dashboard."""
    st.header("Market Overview")
    
    # Display summary metrics
    if 'summary' in st.session_state.insights:
        summary = st.session_state.insights['summary']
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Flights", f"{summary.get('total_flights', 0):,}")
        
        with col2:
            st.metric("Domestic Flights", f"{summary.get('domestic_percentage', 0)}%")
        
        with col3:
            if 'avg_price' in summary:
                st.metric("Avg. Price", f"${summary['avg_price']:,.2f}")
        
        with col4:
            if 'busiest_day' in summary:
                st.metric("Busiest Day", summary['busiest_day'])
    
    # Seasonal demand heatmap
    st.subheader("Seasonal Demand Patterns")
    seasonal_fig = viz.create_seasonal_heatmap(st.session_state.insights)
    if seasonal_fig:
        st.plotly_chart(seasonal_fig, use_container_width=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Day of week patterns
        st.subheader("Day of Week Patterns")
        day_fig = viz.create_day_of_week_chart(st.session_state.insights)
        if day_fig:
            st.plotly_chart(day_fig, use_container_width=True)
    
    with col2:
        # Price distribution
        st.subheader("Price Distribution")
        price_dist_fig = viz.create_price_distribution_chart(st.session_state.insights)
        if price_dist_fig:
            st.plotly_chart(price_dist_fig, use_container_width=True)
    
    # Route map
    st.subheader("Popular Routes Map")
    route_map = viz.create_flight_map(st.session_state.insights, map_type='popular_routes')
    if route_map:
        from streamlit_folium import folium_static
        folium_static(route_map, width=1000)

def display_route_analysis(data):
    """Display the route analysis dashboard."""
    st.header("Route Analysis")
    
    # Popular routes bar chart
    st.subheader("Most Popular Routes")
    routes_fig = viz.create_popular_routes_chart(st.session_state.insights)
    if routes_fig:
        st.plotly_chart(routes_fig, use_container_width=True)
    
    # Price vs Demand scatter plot
    st.subheader("Price vs. Demand Analysis")
    scatter_fig = viz.create_price_scatter(st.session_state.insights)
    if scatter_fig:
        st.plotly_chart(scatter_fig, use_container_width=True)
    
    # Raw data table with filters
    st.subheader("Route Data")
    
    # Create a DataFrame specifically for route analysis
    if 'origin' in data.columns and 'destination' in data.columns:
        route_counts = data.groupby(['origin', 'destination']).agg({
            'price': ['count', 'mean', 'median'] if 'price' in data.columns else 'count',
            'is_domestic': 'first' if 'is_domestic' in data.columns else None
        }).reset_index()
        
        # Flatten multi-level column names
        if isinstance(route_counts.columns, pd.MultiIndex):
            route_counts.columns = ['_'.join(col).rstrip('_') for col in route_counts.columns.values]
        
        # Rename columns for clarity
        columns_map = {
            'price_count': 'flight_count',
            'price_mean': 'avg_price',
            'price_median': 'median_price'
        }
        route_counts.rename(columns=columns_map, inplace=True)
        
        # Add city names
        route_counts['origin_city'] = route_counts['origin'].apply(viz.get_city_name)
        route_counts['destination_city'] = route_counts['destination'].apply(viz.get_city_name)
        
        # Add route type
        if 'is_domestic_first' in route_counts.columns:
            route_counts['route_type'] = route_counts['is_domestic_first'].apply(
                lambda x: 'Domestic' if x else 'International'
            )
        
        # Display the table
        st.dataframe(route_counts, use_container_width=True)

def display_price_analysis(data):
    """Display the price analysis dashboard."""
    st.header("Price Analysis")
    
    # Price trends over time
    st.subheader("Price Trends Over Time")
    
    tab1, tab2 = st.tabs(["Daily Trends", "Weekly Trends"])
    
    with tab1:
        daily_fig = viz.create_price_trend_chart(st.session_state.insights, time_period='daily')
        if daily_fig:
            st.plotly_chart(daily_fig, use_container_width=True)
        else:
            st.info("Daily price trend data not available.")
    
    with tab2:
        weekly_fig = viz.create_price_trend_chart(st.session_state.insights, time_period='weekly')
        if weekly_fig:
            st.plotly_chart(weekly_fig, use_container_width=True)
        else:
            st.info("Weekly price trend data not available.")
    
    # Price statistics
    if 'price_stats' in st.session_state.insights:
        st.subheader("Price Statistics")
        stats = st.session_state.insights['price_stats']
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Minimum Price", utils.format_currency(stats.get('min')))
            st.metric("Maximum Price", utils.format_currency(stats.get('max')))
        
        with col2:
            st.metric("Average Price", utils.format_currency(stats.get('mean')))
            st.metric("Median Price", utils.format_currency(stats.get('median')))
        
        with col3:
            st.metric("Standard Deviation", f"${stats.get('std', 0):.2f}")
        
        with col4:
            st.metric("25th Percentile", utils.format_currency(stats.get('q1')))
            st.metric("75th Percentile", utils.format_currency(stats.get('q3')))
    
    # Price factors analysis
    st.subheader("Price Influencing Factors")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Domestic vs International prices
        if 'summary' in st.session_state.insights:
            summary = st.session_state.insights['summary']
            if 'avg_domestic_price' in summary and 'avg_international_price' in summary:
                domestic_price = summary['avg_domestic_price']
                international_price = summary['avg_international_price']
                
                # Create a simple comparison chart
                comparison_data = pd.DataFrame({
                    'Route Type': ['Domestic', 'International'],
                    'Average Price': [domestic_price, international_price]
                })
                
                import plotly.express as px
                fig = px.bar(
                    comparison_data, 
                    x='Route Type', 
                    y='Average Price',
                    color='Route Type',
                    text_auto=True,
                    labels={'Average Price': 'Average Price (AUD)'},
                    color_discrete_map={'Domestic': '#3366CC', 'International': '#FF9900'}
                )
                fig.update_layout(showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Weekend vs Weekday prices
        if 'summary' in st.session_state.insights:
            summary = st.session_state.insights['summary']
            if 'weekend_price_premium' in summary:
                premium = summary['weekend_price_premium']
                
                st.metric("Weekend Price Premium", f"{premium}%")
                st.write(f"Flights on weekends are on average {premium}% more expensive than weekday flights.")

def display_business_insights():
    """Display the business insights dashboard."""
    st.header("Business Intelligence for Hostel Operations")
    
    # AI-generated insights
    if 'ai_insights' in st.session_state.insights:
        ai_insights = st.session_state.insights['ai_insights']
        
        # Trend summary
        if 'trend_summary' in ai_insights and ai_insights['trend_summary']:
            st.subheader("Market Trend Summary")
            utils.display_info_box(ai_insights['trend_summary'], box_type='blue')
        
        # Market observations
        if 'market_observations' in ai_insights and ai_insights['market_observations']:
            st.subheader("Market Observations")
            for idx, obs in enumerate(ai_insights['market_observations'][:5], 1):
                st.write(f"{idx}. {obs}")
        
        # Hostel recommendations
        if 'hostel_recommendations' in ai_insights and ai_insights['hostel_recommendations']:
            st.subheader("Hostel Business Recommendations")
            for idx, rec in enumerate(ai_insights['hostel_recommendations'], 1):
                utils.display_info_box(f"{idx}. {rec}", box_type='green')
        
        # Seasonal strategies
        if 'seasonal_strategies' in ai_insights and ai_insights['seasonal_strategies']:
            st.subheader("Seasonal Business Strategies")
            for idx, strategy in enumerate(ai_insights['seasonal_strategies'], 1):
                utils.display_info_box(f"{idx}. {strategy}", box_type='amber')
    
    # Market opportunities
    if 'market_opportunities' in st.session_state.insights:
        st.subheader("Market Opportunities")
        opportunities = st.session_state.insights['market_opportunities']
        
        if opportunities:
            opp_table = viz.create_opportunity_table(opportunities)
            if opp_table is not None:
                st.dataframe(opp_table, use_container_width=True)
        else:
            st.info("No significant market opportunities identified with the current data.")
    
    # Correlation with external factors
    st.subheader("Correlation with External Factors")
    st.write("""
    The following factors have been identified as having a significant impact on hostel demand 
    in relation to flight patterns:
    
    1. **Seasonal Travel Patterns**: Peak flight seasons strongly correlate with increased hostel bookings
    2. **Price Sensitivity**: Budget travelers (lowest price quartile flights) show highest correlation with hostel stays
    3. **Weekend vs. Weekday**: Weekend flight surges typically lead to 2-3 day hostel occupancy increases
    4. **International Flight Correlation**: International arrivals typically lead to longer average hostel stays
    """)

if __name__ == "__main__":
    main() 