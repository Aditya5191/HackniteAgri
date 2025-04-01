import ee
import requests
from datetime import datetime, timedelta

# Initialize Earth Engine
try:
    ee.Initialize()
except Exception as e:
    print(f"Error initializing Earth Engine: {e}")
    ee.Authenticate()
    ee.Initialize()

# Expanded knowledge base
CROP_DATA = {
    "rice": {
        "ndvi_healthy": 0.6, "ndwi_healthy": 0.2, "fertilizer": "Nitrogen (20 kg/acre)",
        "pests": {"stem borer": "Yellowing leaves, holes in stems; use Trichogramma cards.",
                  "leaf folder": "Folded leaves; apply neem oil."},
        "ideal_temp": (25, 35), "water_need": 50, "yield_tips": "Ensure standing water during flowering."
    },
    # ... (other crops omitted for brevity)
}

SOIL_GUIDE = {
    "low": (0, 10, "Soil is very dry. Increase irrigation and add organic manure."),
    "moderate": (10, 30, "Soil moisture is okay but could improve. Light irrigation recommended."),
    "high": (30, 100, "Soil is well-moisturized. No extra water needed.")
}

GOV_SCHEMES = {
    "irrigation": "PM Krishi Sinchayee Yojana offers irrigation subsidies.",
    "fertilizer": "Nutrient Based Subsidy (NBS) scheme supports fertilizer costs.",
    "general": "PM-KISAN provides Rs. 6000/year income support."
}

# Analyze farm data using Earth Engine
def analyze_farm(location, start_date, end_date):
    area = ee.Geometry.Rectangle([location['lon'] - 0.1, location['lat'] - 0.1,
                                  location['lon'] + 0.1, location['lat'] + 0.1])
    sentinel2 = ee.ImageCollection("COPERNICUS/S2") \
        .filterBounds(area) \
        .filterDate(start_date, end_date) \
        .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 10)) \
        .first()
    if sentinel2 is None:
        return None, "No recent satellite data available for your area."
    ndvi = sentinel2.normalizedDifference(['B8', 'B4']).rename('NDVI')
    ndwi = sentinel2.normalizedDifference(['B3', 'B8']).rename('NDWI')
    soil_data = ee.Image("projects/soilgrids-isric/phh2o_mean").clip(area)
    soil_moisture = soil_data.select('phh2o_0-5cm_mean').rename('SoilMoisture')
    sample = ee.Image(ndvi.addBands(ndwi).addBands(soil_moisture)) \
        .sample(region=area, scale=10).first().getInfo()['properties']
    return sample, None

# Fetch weather data (current + 7-day forecast) from Open-Meteo
def get_weather(location):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={location['lat']}&longitude={location['lon']}&hourly=temperature_2m,precipitation,soil_moisture_0_1cm&past_days=30&forecast_days=7"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()["hourly"]
        current = {
            "temp": data["temperature_2m"][-1],
            "precip": sum(data["precipitation"][-24:]) / 24,  # Last 24h average
            "soil_moisture": data["soil_moisture_0_1cm"][-1]
        }
        # Forecast: Average next 7 days
        future_temp = sum(data["temperature_2m"][-168:]) / 168  # Last 168 hours = 7 days
        future_precip = sum(data["precipitation"][-168:]) / 7  # Total precip over 7 days
        forecast = {"temp": future_temp, "precip": future_precip}
        return current, forecast
    return {"temp": 25, "precip": 0, "soil_moisture": 10}, {"temp": 25, "precip": 0}  # Fallback

# Generate recommendations
def generate_recommendations(farm_data, current_weather, forecast_weather, crop_type="unknown"):
    ndvi = farm_data.get('NDVI', 0.5)
    ndwi = farm_data.get('NDWI', 0.0)
    soil_moisture = farm_data.get('SoilMoisture', 10)
    temp = current_weather["temp"]
    precip = current_weather["precip"]
    forecast_temp = forecast_weather["temp"]
    forecast_precip = forecast_weather["precip"]
    crop_info = CROP_DATA.get(crop_type.lower(), {
        "ndvi_healthy": 0.5, "ndwi_healthy": 0.0, "fertilizer": "General (10 kg/acre)",
        "ideal_temp": (20, 30), "water_need": 40, "pests": {}, "yield_tips": "General care."
    })
    recs = []
    # Irrigation (current + forecast)
    water_deficit = crop_info["water_need"] - precip
    if ndwi < crop_info["ndwi_healthy"] - 0.2 and precip < 5:
        recs.append(f"Your {crop_type} farm is very dry (NDWI: {ndwi:.2f}). Add 40-50 mm of water now.")
    elif ndwi < crop_info["ndwi_healthy"]:
        recs.append(f"Your {crop_type} needs water (NDWI: {ndwi:.2f}). Add {max(20, water_deficit):.0f} mm.")
    else:
        recs.append("Your farm has enough water now.")
    if forecast_precip < 5:
        recs.append(f"Little rain expected next week ({forecast_precip:.1f} mm/day). Plan extra irrigation.")
    # Fertilizer
    if ndvi < crop_info["ndvi_healthy"] - 0.2:
        recs.append(f"Your {crop_type} is weak (NDVI: {ndvi:.2f}). Use {crop_info['fertilizer']} soon.")
    elif ndvi < crop_info["ndvi_healthy"]:
        recs.append(f"Your {crop_type} could use a boost (NDVI: {ndvi:.2f}). Apply half of {crop_info['fertilizer']}.")
    else:
        recs.append("Your crops are healthy; no fertilizer needed now.")
    # Pesticides
    if ndvi < crop_info["ndvi_healthy"] - 0.1 and precip > 20 and temp > 25:
        recs.append(
            f"High moisture and heat ({temp:.1f}°C) might attract pests. Watch for: {', '.join([f'{k} ({v})' for k, v in crop_info['pests'].items()])}.")
    elif ndvi < crop_info["ndvi_healthy"] - 0.2:
        recs.append(
            f"Weak crops (NDVI: {ndvi:.2f}) could mean pests. Check for: {', '.join([f'{k} ({v})' for k, v in crop_info['pests'].items()])}.")
    # Soil Health
    for key, (min_val, max_val, advice) in SOIL_GUIDE.items():
        if min_val <= soil_moisture < max_val:
            recs.append(f"{advice} (Soil moisture: {soil_moisture:.1f}%)")
            break
    # Temperature (current + forecast)
    temp_min, temp_max = crop_info["ideal_temp"]
    if temp < temp_min:
        recs.append(f"Too cold now ({temp:.1f}°C) for {crop_type}. Use mulch or covers.")
    elif temp > temp_max:
        recs.append(f"Too hot now ({temp:.1f}°C) for {crop_type}. Provide shade or extra water.")
    if forecast_temp < temp_min:
        recs.append(f"Expect cold weather next week ({forecast_temp:.1f}°C). Prepare protection.")
    elif forecast_temp > temp_max:
        recs.append(f"Expect hot weather next week ({forecast_temp:.1f}°C). Plan extra watering.")
    # Yield Tips
    recs.append(f"To improve {crop_type} yield: {crop_info['yield_tips']}")
    # Government Schemes
    if "water" in " ".join(recs).lower():
        recs.append(GOV_SCHEMES["irrigation"])
    if "fertilizer" in " ".join(recs).lower():
        recs.append(GOV_SCHEMES["fertilizer"])
    recs.append(GOV_SCHEMES["general"])
    return recs

# Chatbot logic
def chatbot(user_input):
    user_input = user_input.lower().strip()
    location = {'lat': 20.0, 'lon': 73.8}  # Nashik default
    crop_type = "unknown"
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    # Parse location
    locations = {"pune": (18.5, 73.8), "nashik": (20.0, 73.8), "mumbai": (19.07, 72.87),
                 "delhi": (28.61, 77.21), "bangalore": (12.97, 77.59)}
    for city, (lat, lon) in locations.items():
        if city in user_input:
            location = {'lat': lat, 'lon': lon}
            break
    if "latitude" in user_input or "longitude" in user_input:
        try:
            lat, lon = map(float, [s for s in user_input.split() if s.replace('.', '').isdigit()][:2])
            location = {'lat': lat, 'lon': lon}
        except:
            pass
    # Parse crop type
    for crop in CROP_DATA.keys():
        if crop in user_input:
            crop_type = crop
            break
    # Fetch data
    farm_data, error = analyze_farm(location, start_date, end_date)
    if error:
        return error
    current_weather, forecast_weather = get_weather(location)
    # Handle queries
    response = [f"For your {crop_type} farm at {location['lat']}°N, {location['lon']}°E:"]
    if "advice" in user_input or "farm" in user_input or not any(
            k in user_input for k in ["weather", "soil", "pest", "scheme", "yield"]):
        recs = generate_recommendations(farm_data, current_weather, forecast_weather, crop_type)
        response.extend(recs)
    if "weather" in user_input or "rain" in user_input:
        response.append(
            f"Now: Temp {current_weather['temp']:.1f}°C, Rain {current_weather['precip']:.1f} mm (last 24h).")
        response.append(
            f"Next 7 days: Avg Temp {forecast_weather['temp']:.1f}°C, Avg Rain {forecast_weather['precip']:.1f} mm/day.")
    if "soil" in user_input:
        for key, (min_val, max_val, advice) in SOIL_GUIDE.items():
            if min_val <= farm_data['SoilMoisture'] < max_val:
                response.append(f"Soil: {advice} (Moisture: {farm_data['SoilMoisture']:.1f}%)")
                break
    if "pest" in user_input or "bug" in user_input:
        if crop_type != "unknown":
            response.append(
                f"Watch for {crop_type} pests: {', '.join([f'{k} ({v})' for k, v in CROP_DATA[crop_type]['pests'].items()])}.")
    if "scheme" in user_input or "subsidy" in user_input:
        response.extend(GOV_SCHEMES.values())
    if "yield" in user_input or "improve" in user_input:
        response.append(f"To boost {crop_type} yield: {CROP_DATA[crop_type]['yield_tips']}")
    if "resource" in user_input or "manage" in user_input:
        response.append(
            f"Manage {crop_type}: Use {CROP_DATA[crop_type]['water_need']} mm/season water, apply fertilizer only when needed, rotate crops.")
    if not response[1:]:
        response.append("Ask me about irrigation, fertilizer, pests, soil, weather, schemes, yield, or resources!")
    return "\n".join(response)