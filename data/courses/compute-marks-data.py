import json
import math
import pandas as pd


# Magnetic variation (negative = west)
MAG_VARIATION = -2.0


def to_decimal(deg, minutes):
    return deg + (minutes / 60.0)


def to_radians(deg):
    return deg * math.pi / 180.0


# Haversine distance in NM
def haversine_nm(lat1, lon1, lat2, lon2):
    R = 3440.065  # Nautical miles
    dlat = to_radians(lat2 - lat1)
    dlon = to_radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(to_radians(lat1)) * math.cos(to_radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


# Initial bearing (true)
def initial_bearing(lat1, lon1, lat2, lon2):
    lat1_rad = to_radians(lat1)
    lat2_rad = to_radians(lat2)
    dlon_rad = to_radians(lon2 - lon1)
    x = math.sin(dlon_rad) * math.cos(lat2_rad)
    y = math.cos(lat1_rad) * math.sin(lat2_rad) - math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(dlon_rad)
    bearing = math.degrees(math.atan2(x, y))
    return (bearing + 360) % 360


# Apply magnetic variation
def magnetic_bearing(true_bearing):
    mag_brg = true_bearing + MAG_VARIATION
    if mag_brg < 0:
        mag_brg += 360
    elif mag_brg >= 360:
        mag_brg -= 360
    return mag_brg


with open("marks.json", "r") as f:
    marks = json.load(f)


for m in marks:
    m["Lat"]["Dec"] = to_decimal(m["Lat"]["Deg"], m["Lat"]["Min"])
    m["Long"]["Dec"] = -to_decimal(m["Long"]["Deg"], m["Long"]["Min"])  # Assume West


# Build table
ids = [m["ID"] for m in marks]
table = []


for m1 in marks:
    row = []
    for m2 in marks:
        if m1 == m2:
            row.append("—")
            continue

        m1_lat, m1_long = m1["Lat"]["Dec"], m1["Long"]["Dec"]
        m2_lat, m2_long = m2["Lat"]["Dec"], m2["Long"]["Dec"]
        dist = haversine_nm(m1_lat, m1_long, m2_lat, m2_long)
        true_brg = initial_bearing(m1_lat, m1_long, m2_lat, m2_long)
        mag_brg = magnetic_bearing(true_brg)
        row.append(f"{mag_brg:.0f}° / {dist:.2f}")

    table.append(row)

df = pd.DataFrame(table, index=ids, columns=ids)
df.to_csv("marks_bearings_distances.csv")
