import streamlit as st
import pandas as pd
import numpy as np
from math import radians, sin, cos, sqrt, atan2

# ---------------- LOAD DATA ----------------
df = pd.read_csv("cyclone_india.csv", skiprows=[1])
df_pin = pd.read_csv("pincode_data.csv")
df_scores = pd.read_csv("precomputed_scores.csv")

# ---------------- CLEAN CYCLONE DATA ----------------
df = pd.read_csv("cyclone_india.csv", skiprows=[1])
df.columns = df.columns.str.lower()

df = df[['lat', 'lon', 'usa_wind']]

df['lat'] = pd.to_numeric(df['lat'], errors='coerce')
df['lon'] = pd.to_numeric(df['lon'], errors='coerce')
df['usa_wind'] = pd.to_numeric(df['usa_wind'], errors='coerce')

df['usa_wind'] = df['usa_wind'].replace(-9999, np.nan)

df = df.dropna()
df = df[df['usa_wind'] > 0]

df.columns = ['lat', 'lon', 'wind']

# ---------------- CLEAN PIN DATA ----------------
df_pin.columns = df_pin.columns.str.lower()

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

# ---------------- CYCLONE INDICATORS ----------------
def cyclone_indicators(pin_lat, pin_lon):

    nearby = []
    decay_sum = 0

    for _, row in df.iterrows():
        d = distance(pin_lat, pin_lon, row['lat'], row['lon'])

        # ✅ MATCH PRECOMPUTE (300 km)
        if d <= 300:
            nearby.append(row)

            if d > 1:
                decay_sum += row['wind'] / (d**2)

    nearby_df = pd.DataFrame(nearby)

    if nearby_df.empty:
        return 0, 0, 0

    # ✅ MATCH PRECOMPUTE (TRACK POINT COUNT)
    track_density = len(nearby_df)

    max_wind = nearby_df['wind'].max()

    decay = np.log1p(decay_sum)

    return track_density, max_wind, decay

# ---------------- NORMALIZATION (MATCH CSV) ----------------
df_scores.columns = df_scores.columns.str.strip()

min_td, max_td = df_scores['track_count'].min(), df_scores['track_count'].max()
min_wind, max_wind = df_scores['max_wind'].min(), df_scores['max_wind'].max()
min_decay, max_decay = df_scores['decay_score'].min(), df_scores['decay_score'].max()

def normalize(value, min_val, max_val):
    if max_val == min_val:
        return 0
    val = (value - min_val) / (max_val - min_val) * 100
    return max(0, min(100, val))

# ---------------- SCORE ----------------
def cyclone_score(pin):

    try:
        row = df_pin[df_pin['pincode'] == int(pin)]
        if row.empty:
            return None
        lat = float(row.iloc[0]['latitude'])
        lon = float(row.iloc[0]['longitude'])
    except:
        return None

    td, wind, decay = cyclone_indicators(lat, lon)

    td_score = normalize(td, min_td, max_td)
    wind_score = normalize(wind, min_wind, max_wind)
    decay_score = normalize(decay, min_decay, max_decay)

    score = 0.40 * td_score + 0.35 * wind_score + 0.25 * decay_score
    score = max(0, min(100, score))

    return round(score, 2), td, wind

# ---------------- UI ----------------
st.title("🌪️ Cyclone Risk Assessment Tool")

pin = st.text_input("Enter PIN Code")

if pin:
    result = cyclone_score(pin)

    if result:
        score, td, wind = result

        st.subheader(f"Cyclone Score: {score}")
        st.write(f"Track Density (points): {td}")
        st.write(f"Max Wind: {wind}")

        if score > 80:
            st.error("Very High cyclone risk")
        elif score > 60:
            st.warning("High cyclone risk")
        elif score > 40:
            st.warning("Moderate cyclone exposure")
        else:
            st.success("Low cyclone risk")
    else:
        st.write("Invalid PIN code")
