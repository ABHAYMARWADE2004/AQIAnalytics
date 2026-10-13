# dashboard.py
# AQI Analytics Dashboard - 30 days of hourly air quality across Indian cities

import streamlit as st
import pandas as pd
from database import get_all_readings, clear_all_readings

st.set_page_config(page_title="AQI Analytics Dashboard", page_icon="🌫️", layout="wide")

st.markdown("""
<style>
    [data-testid="stMetric"] {
        background-color: #1A1D29;
        border: 1px solid #2D3142;
        padding: 15px;
        border-radius: 10px;
    }
    h2, h3 { color: #4FC3F7; }
    .stButton>button { border-radius: 8px; border: 1px solid #4FC3F7; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style="text-align: center; padding: 10px 0 30px 0;">
    <h1 style="font-size: 42px; margin-bottom: 0;">🌫️ AQI Analytics Dashboard</h1>
    <p style="font-size: 16px; color: #999;">Air quality trends across Indian cities, last 30 days</p>
</div>
""", unsafe_allow_html=True)

records = get_all_readings()

if len(records) == 0:
    st.warning("No data yet. Run `python collect_data.py` first.")
    st.stop()

df = pd.DataFrame(records, columns=["City", "AQI", "Measured At"])
df["Measured At"] = pd.to_datetime(df["Measured At"])
df["Date"] = df["Measured At"].dt.date
df["Hour"] = df["Measured At"].dt.hour

# ===== Sidebar =====
all_cities = sorted(df["City"].unique())
default_cities = [c for c in ["delhi", "kolkata", "mumbai", "pune", "bangalore", "coimbatore"] if c in all_cities]

with st.sidebar:
    st.header("⚙️ Filters")
    selected = st.multiselect("Cities", all_cities, default=default_cities)

    st.divider()
    st.caption("Run `python collect_data.py` to refresh. It fills in any missing hours.")
    if st.button("🗑️ Clear All Data"):
        clear_all_readings()
        st.success("All data cleared.")
        st.rerun()

if not selected:
    st.info("Pick at least one city from the sidebar.")
    st.stop()

fdf = df[df["City"].isin(selected)]

# ===== Top stats =====
avg_by_city = fdf.groupby("City")["AQI"].mean().round().sort_values(ascending=False)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Readings", f"{len(fdf):,}")
col2.metric("Most polluted (avg)", f"{avg_by_city.index[0].title()} ({int(avg_by_city.iloc[0])})")
col3.metric("Cleanest (avg)", f"{avg_by_city.index[-1].title()} ({int(avg_by_city.iloc[-1])})")
col4.metric("Data through", fdf["Measured At"].max().strftime("%d %b, %H:%M"))

st.divider()

# ===== City comparison =====
st.subheader("📊 Average AQI by City")
st.bar_chart(avg_by_city)

# ===== Daily trend =====
st.subheader("📈 Daily Average AQI Trend")
daily = fdf.groupby(["Date", "City"])["AQI"].mean().round(1).reset_index()
trend = daily.pivot(index="Date", columns="City", values="AQI")
trend.index = pd.to_datetime(trend.index)
st.line_chart(trend)

# ===== Time of day =====
st.subheader("🕐 When Is Air Quality Worst? (Average AQI by Hour of Day, IST)")
hourly = fdf.groupby("Hour")["AQI"].mean().round(1)
st.bar_chart(hourly)
peak_hour = int(hourly.idxmax())
low_hour = int(hourly.idxmin())
st.info(f"Across the selected cities, AQI is highest around {peak_hour}:00 "
        f"and lowest around {low_hour}:00.")

# ===== Unhealthy share =====
st.subheader("⚠️ Share of Hours With Unhealthy Air (AQI above 150)")
bad_share = (fdf["AQI"] > 150).groupby(fdf["City"]).mean().mul(100).round(1).sort_values(ascending=False)
st.bar_chart(bad_share)

st.divider()

# ===== AQI reference =====
st.subheader("ℹ️ AQI Categories")
st.table(pd.DataFrame({
    "AQI Range": ["0-50", "51-100", "101-150", "151-200", "201-300", "301+"],
    "Category": ["Good", "Moderate", "Unhealthy for Sensitive Groups", "Unhealthy", "Very Unhealthy", "Hazardous"],
}))

# ===== Raw data + export =====
st.subheader("📋 Readings")
st.dataframe(fdf[["City", "AQI", "Measured At"]], use_container_width=True)

st.download_button(
    label="📥 Download as CSV",
    data=fdf[["City", "AQI", "Measured At"]].to_csv(index=False),
    file_name="aqi_readings.csv",
    mime="text/csv",
)

st.caption("Data: Open-Meteo Air Quality API (CAMS ENSEMBLE data provider). "
           "Values are model-based estimates, not ground-station measurements.")