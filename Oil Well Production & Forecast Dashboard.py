# Databricks notebook source
# DBTITLE 1,Install Dependencies
# MAGIC %pip install streamlit databricks-sql-connector

# COMMAND ----------

# DBTITLE 1,Restart Python
dbutils.library.restartPython()

# COMMAND ----------

import streamlit as st
from databricks import sql
import pandas as pd
import os

# Page configuration
st.set_page_config(page_title="Oil Well Production Dashboard", layout="wide")

# Title
st.title("🛢️ Oil Well Production & Forecast Dashboard")

# Database connection function
@st.cache_resource
def get_connection():
    return sql.connect(
        server_hostname=os.getenv("DATABRICKS_SERVER_HOSTNAME"),
        http_path=os.getenv("DATABRICKS_HTTP_PATH"),
        access_token=os.getenv("DATABRICKS_TOKEN")
    )

# Load wells list
@st.cache_data
def load_wells():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT well_id, well_name FROM istm637_831004060.oilgas.dim_well ORDER BY well_name")
    wells = cursor.fetchall()
    cursor.close()
    return {f"{row[1]} ({row[0]})": row[0] for row in wells}

# Load historical data
@st.cache_data
def load_history(well_id):
    conn = get_connection()
    query = """
    SELECT d.calendar_date, f.oil_bbl 
    FROM istm637_831004060.oilgas.fact_production f 
    JOIN istm637_831004060.oilgas.dim_date d ON f.date_id = d.date_id 
    WHERE f.well_id = :well_id 
    ORDER BY d.calendar_date
    """
    df = pd.read_sql(query, conn, params={"well_id": well_id})
    return df

# Load forecast data
@st.cache_data
def load_forecast(well_id):
    conn = get_connection()
    query = """
    SELECT day_ahead, predicted_oil_bbl 
    FROM istm637_831004060.oilgas.well_forecast 
    WHERE well_id = :well_id 
    ORDER BY day_ahead
    """
    df = pd.read_sql(query, conn, params={"well_id": well_id})
    return df

# Main app
try:
    # Load wells dropdown
    wells_dict = load_wells()
    
    # Dropdown selector
    selected_well_display = st.selectbox(
        "Select a Well:",
        options=list(wells_dict.keys()),
        index=0
    )
    
    selected_well_id = wells_dict[selected_well_display]
    
    # Load data for selected well
    with st.spinner("Loading data..."):
        history_df = load_history(selected_well_id)
        forecast_df = load_forecast(selected_well_id)
    
    # Display charts side by side
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Historical Production")
        if not history_df.empty:
            st.line_chart(
                history_df.set_index('calendar_date')['oil_bbl'],
                use_container_width=True
            )
            st.caption(f"Total records: {len(history_df):,}")
        else:
            st.info("No historical data available for this well.")
    
    with col2:
        st.subheader("🔮 Production Forecast")
        if not forecast_df.empty:
            st.line_chart(
                forecast_df.set_index('day_ahead')['predicted_oil_bbl'],
                use_container_width=True
            )
            st.caption(f"Forecast days: {len(forecast_df):,}")
        else:
            st.info("No forecast data available for this well.")

except Exception as e:
    st.error(f"Error loading data: {str(e)}")
    st.info("Please ensure your Databricks connection is properly configured.")

# COMMAND ----------

# DBTITLE 1,Test Data Access
# Test the data queries without Streamlit UI
import pandas as pd
from pyspark.sql import SparkSession

spark = SparkSession.builder.getOrCreate()

# Get list of wells
print("📋 Available Wells:")
wells_df = spark.sql("""
    SELECT well_id, well_name 
    FROM istm637_831004060.oilgas.dim_well 
    ORDER BY well_name
    LIMIT 10
""")
display(wells_df)

# Pick the first well to test with
first_well = wells_df.first()
if first_well:
    test_well_id = first_well.well_id
    test_well_name = first_well.well_name
    
    print(f"\n🔍 Testing with: {test_well_name} (ID: {test_well_id})")
    
    # Get historical production data
    print("\n📊 Historical Production (last 30 days):")
    history = spark.sql(f"""
        SELECT d.calendar_date, f.oil_bbl 
        FROM istm637_831004060.oilgas.fact_production f 
        JOIN istm637_831004060.oilgas.dim_date d ON f.date_id = d.date_id 
        WHERE f.well_id = {test_well_id}
        ORDER BY d.calendar_date DESC
        LIMIT 30
    """)
    display(history)
    
    # Get forecast data
    print("\n🔮 Production Forecast:")
    forecast = spark.sql(f"""
        SELECT day_ahead, predicted_oil_bbl 
        FROM istm637_831004060.oilgas.well_forecast 
        WHERE well_id = {test_well_id}
        ORDER BY day_ahead
        LIMIT 30
    """)
    display(forecast)
    
    print(f"\n✅ Data access test complete!")
    print(f"   - Historical records: {history.count()}")
    print(f"   - Forecast records: {forecast.count()}")
else:
    print("❌ No wells found in the database")

# COMMAND ----------

# DBTITLE 1,Visualize Well Production & Forecast
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta

# Select a producing well for testing
test_well_id = 'WELL-0010'
test_well_name = 'Adams 21-32'

print(f"📊 Testing Dashboard for: {test_well_name} ({test_well_id})")
print("=" * 60)

# Get historical production data (last 90 days)
history_df = spark.sql(f"""
    SELECT d.calendar_date, f.oil_bbl
    FROM istm637_831004060.oilgas.fact_production f
    JOIN istm637_831004060.oilgas.dim_date d ON f.date_id = d.date_id
    WHERE f.well_id = '{test_well_id}'
    ORDER BY d.calendar_date DESC
    LIMIT 90
""").toPandas()

print(f"\n✅ Historical data: {len(history_df)} records")
print(f"   Date range: {history_df['calendar_date'].min()} to {history_df['calendar_date'].max()}")
print(f"   Production range: {history_df['oil_bbl'].min():.1f} - {history_df['oil_bbl'].max():.1f} bbl/day")
print(f"   Average: {history_df['oil_bbl'].mean():.1f} bbl/day")

# Get forecast data
forecast_df = spark.sql(f"""
    SELECT day_ahead, predicted_oil_bbl
    FROM istm637_831004060.oilgas.well_forecast
    WHERE well_id = '{test_well_id}'
    ORDER BY day_ahead
""").toPandas()

print(f"\n✅ Forecast data: {len(forecast_df)} records")
print(f"   Forecast range: Day {forecast_df['day_ahead'].min()} to {forecast_df['day_ahead'].max()}")
print(f"   Predicted range: {forecast_df['predicted_oil_bbl'].min():.1f} - {forecast_df['predicted_oil_bbl'].max():.1f} bbl/day")

# Create forecast dates (starting from last historical date)
last_date = history_df['calendar_date'].max()
forecast_df['forecast_date'] = pd.to_datetime(last_date) + pd.to_timedelta(forecast_df['day_ahead'], unit='D')

# Create visualization
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

# Historical Production
ax1.plot(history_df['calendar_date'], history_df['oil_bbl'], linewidth=2, color='#1f77b4')
ax1.set_title('📊 Historical Production', fontsize=14, fontweight='bold', pad=15)
ax1.set_xlabel('Date', fontsize=11)
ax1.set_ylabel('Oil Production (bbl/day)', fontsize=11)
ax1.grid(True, alpha=0.3)
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
ax1.tick_params(axis='x', rotation=45)
ax1.text(0.02, 0.98, f'Total records: {len(history_df):,}', 
         transform=ax1.transAxes, fontsize=9, verticalalignment='top',
         bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

# Production Forecast
ax2.plot(forecast_df['forecast_date'], forecast_df['predicted_oil_bbl'], 
         linewidth=2, color='#ff7f0e', linestyle='--')
ax2.set_title('🔮 Production Forecast', fontsize=14, fontweight='bold', pad=15)
ax2.set_xlabel('Date', fontsize=11)
ax2.set_ylabel('Predicted Oil Production (bbl/day)', fontsize=11)
ax2.grid(True, alpha=0.3)
ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
ax2.tick_params(axis='x', rotation=45)
ax2.text(0.02, 0.98, f'Forecast days: {len(forecast_df):,}', 
         transform=ax2.transAxes, fontsize=9, verticalalignment='top',
         bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

plt.suptitle(f'🛢️ Oil Well Production & Forecast Dashboard: {test_well_name}', 
             fontsize=16, fontweight='bold', y=1.02)
plt.tight_layout()
plt.show()

print("\n" + "=" * 60)
print("✅ Dashboard test complete!")
print("\n💡 Note: The Streamlit app above is designed to run as a standalone")
print("   web application. This test validates the underlying data queries.")