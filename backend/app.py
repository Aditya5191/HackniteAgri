from flask import Flask, jsonify
from flask_cors import CORS
import numpy as np
import time
from datetime import datetime
import pickle

app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing for React frontend

# Initial state variables (starting from 2004)
current_year = 2004
current_month = 1

# Climate change factors (gradual warming, shifting rainfall)
temp_increase_per_year = 0.02  # Small temperature increase each year
rainfall_variability = 0.97  # Slight decrease in rainfall over years

# Load the pipeline and models
with open('num_pipeline.pkl', 'rb') as f:
    pipeline = pickle.load(f)

with open('trained_model_1.pkl', 'rb') as f:
    water_model = pickle.load(f)

with open('trained_model_2.pkl', 'rb') as f:
    fertilizer_model = pickle.load(f)

# Function to simulate realistic IoT sensor data
def generate_sensor_data():
    global current_year, current_month

    # Generate climate-related variables with trends
    temperature = np.random.normal(20 + (current_year - 2004) * temp_increase_per_year, 3)  # Slight warming
    rainfall = np.random.normal(100 * (rainfall_variability ** (current_year - 2004)), 30)  # Decreasing rainfall
    humidity = np.random.normal(60, 10)  # Humidity around 60%
    soil_moisture = np.clip(np.random.normal(50 + 0.3 * rainfall - 0.1 * temperature, 10), 10, 90)
    ndvi = np.clip(np.random.normal(0.4 + 0.005 * soil_moisture - 0.002 * temperature, 0.1), 0, 1)

    # Soil pH (more neutral when moisture is high, acidic when rainfall is excessive)
    soil_pH = np.clip(np.random.normal(6.5 - 0.02 * rainfall + 0.01 * soil_moisture, 0.2), 5.5, 7.5)

    # Soil Electrical Conductivity (EC) - Higher in dry conditions due to salt accumulation
    soil_EC = np.clip(np.random.normal(0.5 + 0.01 * temperature - 0.02 * soil_moisture, 0.1), 0.1, 1.5)

    # Increment month and year
    current_month += 1
    if current_month > 12:
        current_month = 1
        current_year += 1

    # Add timestamp
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Return simulated data
    return {
        "Year": current_year,
        "Month": current_month,
        "Temperature_C": round(float(temperature), 2),
        "Rainfall_mm": round(float(rainfall), 2),
        "Humidity_pct": round(float(humidity), 2),
        "Soil_Moisture_pct": round(float(soil_moisture), 2),
        "NDVI_Mean": round(float(ndvi), 4),
        "Soil_pH": round(float(soil_pH), 2),
        "Soil_EC_dS_m": round(float(soil_EC), 2),
        "Timestamp": timestamp
    }

# API Endpoint to Simulate Live IoT Data
@app.route('/iot-data', methods=['GET'])
def get_iot_data():
    sensor_data = generate_sensor_data()

    # Prepare data for prediction
    input_data = [
        sensor_data["Year"],
        sensor_data["Month"],
        sensor_data["Temperature_C"],
        sensor_data["Rainfall_mm"],
        sensor_data["Humidity_pct"],
        sensor_data["Soil_Moisture_pct"],
        sensor_data["NDVI_Mean"],
        sensor_data["Soil_pH"],
        sensor_data["Soil_EC_dS_m"]
    ]

    # Preprocess data using the pipeline
    processed_data = pipeline.transform([input_data])

    # Predict water and fertilizer requirements
    water_needed = round(water_model.predict(processed_data)[0], 2)
    fertilizer_needed = round(fertilizer_model.predict(processed_data)[0], 2)

    # Add predictions to the response
    sensor_data["Water_Needed_liters_ha_day"] = water_needed
    sensor_data["Fertilizer_Needed_kg_ha"] = fertilizer_needed

    return jsonify(sensor_data)

if __name__ == '__main__':
    app.run(debug=True)