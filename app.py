import pandas as pd
from math import radians, sin, cos, sqrt, atan2
# Upload these files in Colab before running:
# cyclone_india.csv (IBTrACS filtered NI)
# pincode_data.csv

df = pd.read_csv("cyclone_india.csv")
df_pin = pd.read_csv("pincode_data.csv")
# --- Cyclone data ---
df = df[['LAT', 'LON', 'USA_WIND']].dropna()

df['LAT'] = pd.to_numeric(df['LAT'], errors='coerce')
df['LON'] = pd.to_numeric(df['LON'], errors='coerce')
df['USA_WIND'] = pd.to_numeric(df['USA_WIND'], errors='coerce')

df = df.dropna()
df.columns = ['lat', 'lon', 'wind']


# --- PIN data ---
df_pin = df_pin[['pincode', 'latitude', 'longitude']]

df_pin['pincode'] = pd.to_numeric(df_pin['pincode'], errors='coerce')
df_pin['latitude'] = pd.to_numeric(df_pin['latitude'], errors='coerce')
df_pin['longitude'] = pd.to_numeric(df_pin['longitude'], errors='coerce')

df_pin = df_pin.dropna()
def distance(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in km
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    return 2 * R * atan2(sqrt(a), sqrt(1 - a))
  def get_lat_lon(pin):
    row = df_pin[df_pin['pincode'] == int(pin)]
    if not row.empty:
        return float(row.iloc[0]['latitude']), float(row.iloc[0]['longitude'])
    return None, None
    def cyclone_indicators(pin_lat, pin_lon):

    import numpy as np

    nearby = []
    decay_sum = 0

    for _, row in df.iterrows():
        d = distance(pin_lat, pin_lon, row['lat'], row['lon'])

        if d <= 200:
            nearby.append(row)

            # Distance-decayed exposure
            if d > 0:
                decay_sum += row['wind'] / (d**2)

    nearby_df = pd.DataFrame(nearby)

    # 1. Track density
    track_density = len(nearby_df)

    # 2. Max wind exposure
    max_wind = nearby_df['wind'].max() if len(nearby_df) > 0 else 0

    # 3. Distance-decayed exposure (FIXED)
    decay = np.log1p(decay_sum)

    return track_density, max_wind, decay
    # Track density max (approx)
max_td = 200   # safe upper bound

# Wind range (realistic)
min_wind = df['wind'].min()
max_wind = df['wind'].max()

# Decay range (approx after log)
min_decay = 0
max_decay = 0.02   # adjust based on observed values
import numpy as np

sample = df_pin.sample(200)  # only 200 PINs → fast

td_list = []
wind_list = []
decay_list = []

for _, row in sample.iterrows():
    lat = row['latitude']
    lon = row['longitude']

    td, wind, decay = cyclone_indicators(lat, lon)

    td_list.append(td)
    wind_list.append(wind)
    decay_list.append(decay)

# Realistic ranges
min_td, max_td = min(td_list), max(td_list)
min_wind, max_wind = min(wind_list), max(wind_list)
min_decay, max_decay = min(decay_list), max(decay_list)
def normalize(value, min_val, max_val):
    if max_val == min_val:
        return 0
    return (value - min_val) / (max_val - min_val) * 100
  def cyclone_score(pin):

    lat, lon = get_lat_lon(pin)

    if lat is None:
        return None

    td, wind, decay = cyclone_indicators(lat, lon)

    # Normalize each component
    td_score = normalize(td, 0, max_td)
    wind_score = normalize(wind, min_wind, max_wind)
    decay_score = normalize(decay, min_decay, max_decay)

    # Weighted score
    score = (
        0.40 * td_score +
        0.35 * wind_score +
        0.25 * decay_score
    )

    # FINAL SAFETY (IMPORTANT)
    score = max(0, min(100, score))

    return round(score, 2), td, wind
    pin = input("Enter PIN code: ")

result = cyclone_score(pin)

if result:
    score, td, wind = result

    print("\n🌪️ Cyclone Score:", score)
    print(f"Track Density: {td}")
    print(f"Max Wind: {wind}")

    if score > 70:
        print("High cyclone risk due to strong storms and high exposure.")
    elif score > 40:
        print("Moderate cyclone exposure.")
    else:
        print("Low cyclone risk.")

else:
    print("Invalid PIN code")
