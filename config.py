# config.py
from dotenv import load_dotenv
import os

load_dotenv()

# ===== MySQL =====
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = "aqi_analytics_db"

# ===== Cities: name -> (latitude, longitude) =====
CITIES = {
    "pune": (18.52, 73.86), "mumbai": (19.08, 72.88), "delhi": (28.61, 77.21),
    "bangalore": (12.97, 77.59), "hyderabad": (17.39, 78.49), "chennai": (13.08, 80.27),
    "kolkata": (22.57, 88.36), "ahmedabad": (23.02, 72.57), "jaipur": (26.91, 75.79),
    "lucknow": (26.85, 80.95), "patna": (25.59, 85.14), "bhopal": (23.26, 77.41),
    "chandigarh": (30.73, 76.78), "coimbatore": (11.02, 76.96), "aurangabad": (19.88, 75.34),
}

# How many past days to pull on each run (API allows up to 92)
DAYS_BACK = 30