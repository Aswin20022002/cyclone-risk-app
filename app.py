import streamlit as st
import pandas as pd
import numpy as np
from math import radians, sin, cos, sqrt, atan2

# ---------------- LOAD DATA ----------------
df = pd.read_csv("cyclone_india.csv")
df_pin = pd.read_csv("pincode_data.csv")
df_scores = pd.read_csv("precomputed_scores.csv")

# ---------------- CLEAN CYCLONE DATA ----------------
df = df[['LAT', 'LON', 'USA_WIND']].dropna()

df['LAT'] = pd.to_numeric(df['LAT'], errors='coerce')
df['LON'] = pd.to_numeric(df['LON'], errors='coerce')
df['USA_WIND'] = pd.to_numeric(df['USA_WIND'], errors='coerce')

df = df.dropna()
df.columns = ['lat', 'lon', 'wind']

# ---------------- CLEAN PIN DATA ----------------
df_pin = df_pin[['pincode', 'latitude', 'longitude']]

df_pin['pincode'] = pd.to_numeric(df_pin['pincode'], errors='coerce')
df_pin['latitude'] = pd.to_numeric(df_pin['latitude'], errors='coerce')
df_pin['longitude'] = pd.to_numeric(df_pin['longitude'], errors='coerce')

df_pin = df_pin.dropna()

# ---------------- DISTANCE FUNCTION ----------------
def distance(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1))*cos(radians(lat2))*sin(dlon/2)**2
    return 2 * R * atan2(sqrt(a), sqrt(1 - a))

# ---------------- GET PIN LOCATION ----------------
def get_lat_lon(pin):
    try:
        row = df_pin[df_pin['pincode'] == int(pin)]
        if not row.empty:
            return float(row.iloc[0]['latitude']), float(row.iloc[0]['longitude'])
    except:
        pass
    return None, None

# ---------------- CYCLONE INDICATORS ----------------
def cyclone_indicators(pin_lat, pin_lon):

    decay_sum = 0
    nearby = []

    for _, row in df.iterrows():
        d = distance(pin_lat, pin_lon, row['lat'], row['lon'])

        if d <= 200:
            nearby.append(row)

            if d > 1:  # avoid extreme blow-up
                decay_sum += row['wind'] / (d**2)

    nearby_df = pd.DataFrame(nearby)

    # Track density (point-based, consistent with precompute)
    track_density = len(nearby_df)

    # Max wind
    max_wind = nearby_df['wind'].max() if len(nearby_df) > 0 else 0

    # Distance-decay
    decay = np.log1p(decay_sum)

    return track_density, max_wind, decay

# ---------------- REAL NORMALIZATION (FROM ALL PINs) ----------------
min_td, max_td = df_scores['track_count'].min(), df_scores['track_count'].max()
min_wind, max_wind = df_scores['max_wind'].min(), df_scores['max_wind'].max()
min_decay, max_decay = df_scores['decay_score'].min(), df_scores['decay_score'].max()

def normalize(value, min_val, max_val):
    if max_val == min_val:
        return 0
    return (value - min_val) / (max_val - min_val) * 100

# ---------------- FINAL SCORE ----------------
def cyclone_score(pin):

    lat, lon = get_lat_lon(pin)

    if lat is None:
        return None

    td, wind, decay = cyclone_indicators(lat, lon)

    td_score = normalize(td, min_td, max_td)
    wind_score = normalize(wind, min_wind, max_wind)
    decay_score = normalize(decay, min_decay, max_decay)

    score = (
        0.40 * td_score +
        0.35 * wind_score +
        0.25 * decay_score
    )

    score = max(0, min(100, score))

    return round(score, 2), td, wind

# ---------------- STREAMLIT UI ----------------
st.title("🌪️ Cyclone Risk Assessment Tool")

pin = st.text_input("Enter PIN Code")

if pin:
    result = cyclone_score(pin)

    if result:
        score, td, wind = result

        st.subheader(f"Cyclone Score: {score}")
        st.write(f"Track Density: {td}")
        st.write(f"Max Wind: {wind}")

        if score > 70:
            st.error("High cyclone risk")
        elif score > 40:
            st.warning("Moderate cyclone exposure")
        else:
            st.success("Low cyclone risk")
    else:
        st.write("Invalid PIN code")
