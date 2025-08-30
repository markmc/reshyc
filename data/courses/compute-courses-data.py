import json
import math
import pandas as pd


def to_decimal(deg, minutes):
    return deg + (minutes / 60.0)


def to_radians(deg):
    return deg * math.pi / 180.0


# Haversine distance in NM
def haversine(lat1, lon1, lat2, lon2):
    R = 3440.065  # Nautical miles
    dlat = to_radians(lat2 - lat1)
    dlon = to_radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(to_radians(lat1)) * math.cos(to_radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


# --- Bearing calculation ---
def bearing(lat1, lon1, lat2, lon2):
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dlambda = math.radians(lon2 - lon1)
    y = math.sin(dlambda) * math.cos(phi2)
    x = math.cos(phi1)*math.sin(phi2) - math.sin(phi1)*math.cos(phi2)*math.cos(dlambda)
    brng = (math.degrees(math.atan2(y, x)) + 360) % 360
    return brng


# --- Load data ---
with open("marks.json") as f:
    marks = json.load(f)

with open("courses.json") as f:
    courses = json.load(f)

# Create mark dictionary: mark_id -> (lat, lon) - assume West
mark_dict = {}
for m in marks:
    mark_dict[m["ID"]] = (
        to_decimal(m["Lat"]["Deg"], m["Lat"]["Min"]),
        -to_decimal(m["Long"]["Deg"], m["Long"]["Min"])
    )

# Compute course lengths
results = []
for course in courses:
    course_id = course["id"]
    wind_angle = (int(course_id[:2]) * 10) + 10
    mark_ids = [(m["id"], m.get("round") == "S") for m in course["marks"]]

    mark_sequence = "Z"

    total_distance = 0.0
    for i in range(len(mark_ids) - 1):
        m1, m2 = mark_ids[i][0], mark_ids[i+1][0]
        if m1 == "Z":
            continue # Ignore Z mark, all courses include it
        if m1 not in mark_dict or m2 not in mark_dict:
            print(f"Unknown marks {m1} {m2}?")
            continue
        lat1, lon1 = mark_dict[m1]
        lat2, lon2 = mark_dict[m2]

        dist = haversine(lat1, lon1, lat2, lon2)
        brng = bearing(lat1, lon1, lat2, lon2)

        suffix = ""

        # Add 50% for upwind legs
        angle_diff = abs((wind_angle - brng + 180) % 360 - 180)
        if angle_diff <= 37:
            dist *= 1.5
            suffix += "↑"

        # Starboard rounding
        if mark_ids[i+1][1]:
            prefix += "↫"

        total_distance += dist

        mark_sequence += f" {m1}{suffix}"

    prefix = ""
    if mark_ids[i+1][1]:
        prefix = "↫"
    mark_sequence += f" {prefix}{mark_ids[i+1][0]}"

    # Add extra legs - first beat, second leg, and final beat
    total_distance += (0.5*1.5) + 0.3 + (0.3*1.5)
    total_distance = round(total_distance, 2)

    diff_perc = round(abs(course["lengths"]["method2"]-total_distance)/total_distance*100, 2)

    results.append([
        course_id,
        mark_sequence,
        total_distance,
    ])

df = pd.DataFrame(results)
df.to_csv("course_lengths.csv")

print("Calculated lengths saved to course_lengths.csv")
