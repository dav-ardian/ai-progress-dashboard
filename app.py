import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.express as px

# Load data (contoh: dari Excel lokal, nanti bisa diganti Google Sheets)
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Konfigurasi scope
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

# Load credentials.json
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

# Buka Google Sheet
spreadsheet = client.open("Book2")
sheet = spreadsheet.worksheet("Sitelist IHR Survey - JABO")

# Ambil data ke DataFrame
data = sheet.get_all_records()
df = pd.DataFrame(data)


# Pastikan kolom koordinat ada
if "LAT" in df.columns and "LONG" in df.columns:
    df = df.dropna(subset=["LAT", "LONG"])

# --- Dashboard Layout ---
st.set_page_config(page_title="AI Monitoring Dashboard", layout="wide")
st.title("📊 AI-Powered Monitoring Dashboard")

# Summary KPIs
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Sites", len(df))
with col2:
    st.metric("Done", (df["MILESTONE STATUS"] == "Done").sum())
with col3:
    st.metric("Pending", (df["MILESTONE STATUS"] != "Done").sum())

# Map Visualization
st.subheader("🗺️ Site Map")
map_center = [df["LAT"].mean(), df["LONG"].mean()]
m = folium.Map(location=map_center, zoom_start=8)

for _, row in df.iterrows():
    status = str(row["MILESTONE STATUS"]).lower()
    if "done" in status:
        color = "red"
    elif "pending" in status or "progress" in status:
        color = "orange"
    else:
        color = "blue"
    folium.Marker(
        location=[row["LAT"], row["LONG"]],
        popup=f"<b>{row['SITE NAME']}</b><br>Status: {row['MILESTONE STATUS']}",
        icon=folium.Icon(color=color)
    ).add_to(m)

st_data = st_folium(m, width=800, height=500)

# Chart Visualization
st.subheader("📈 Progress Charts")
status_count = df["MILESTONE STATUS"].value_counts().reset_index()
status_count.columns = ["Status", "Count"]
fig = px.pie(status_count, names="Status", values="Count", title="Site Status Distribution")
st.plotly_chart(fig, use_container_width=True)

# AI Insight (placeholder)
st.subheader("🤖 AI Insights")
st.info("Contoh: Region Bogor hanya 40% selesai, lebih rendah dari rata-rata 62%. Prioritaskan Bogor minggu depan.")

query = st.text_input("Tanyakan sesuatu ke AI tentang data ini:")
if query:
    # Placeholder jawaban AI (nanti integrasi ke LLM)
    st.success(f"AI menjawab: berdasarkan data, '{query}' masih dalam pengembangan integrasi.")
