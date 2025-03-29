from flask import Flask, request, jsonify
from flask_cors import CORS  # Import CORS for handling cross-origin requests
import ee
import os

# Initialize Earth Engine
try:
    ee.Initialize()
except Exception as e:
    print(f"Error initializing Earth Engine: {e}")
    ee.Authenticate()
    ee.Initialize()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes (fixes preflight OPTIONS requests)

# Function to get user-defined AOI
def get_user_aoi(coords):
    """
    Parse user-provided coordinates or use default Tumkur, Karnataka.
    """
    if coords:
        try:
            coords = list(map(float, coords.split(",")))
            if len(coords) == 4:
                return ee.Geometry.Rectangle(coords)
            else:
                raise ValueError("Invalid coordinates format. Expected: min_lon,min_lat,max_lon,max_lat.")
        except ValueError as ve:
            print(f"Coordinates parsing error: {ve}")
    # Default to Tumkur, Karnataka
    return ee.Geometry.Rectangle([76.5, 13.2, 77.5, 14.0])

# Analyze and mark problem areas
def analyze_and_mark_problem_areas(aoi, start_date, end_date):
    """
    Fetch Sentinel-2 data, calculate NDVI, MSI, and NDWI, and classify stress areas.
    """
    # Filter Sentinel-2 data by date and location
    sentinel2_collection = ee.ImageCollection("COPERNICUS/S2") \
        .filterBounds(aoi) \
        .filterDate(start_date, end_date) \
        .sort('CLOUD_COVERAGE_ASSESSMENT')
    
    # Check if collection is empty
    if sentinel2_collection.size().getInfo() == 0:
        raise ValueError("No Sentinel-2 data found for the given date range and location.")
    
    sentinel2 = sentinel2_collection.first()

    # Calculate NDVI, MSI, and NDWI
    ndvi = sentinel2.normalizedDifference(['B8', 'B4']).rename('NDVI')
    swir1 = sentinel2.select('B11')
    nir = sentinel2.select('B8')
    msi = swir1.divide(nir).rename('MSI')
    green = sentinel2.select('B3')
    ndwi = green.subtract(nir).divide(green.add(nir)).rename('NDWI')

    # Classify areas based on thresholds
    crop_stress = ndvi.expression(
        "(NDVI < 0.5 && MSI > 1.8) ? 2" +  # Severe crop stress
        ": (NDVI < 0.7 && MSI > 1.0) ? 1" +  # Moderate crop stress
        ": 0",  # No stress
        {'NDVI': ndvi, 'MSI': msi}).rename('CropStress')

    water_stress = ndwi.lt(-0.1).rename('WaterStress')  # Low NDWI indicates water stress

    return crop_stress, water_stress

# Generate recommendations based on raster data
def generate_recommendations(crop_stress, water_stress, aoi):
    """
    Sample random points in the AOI and generate recommendations based on stress classifications.
    """
    recommendations = []
    
    sample_points = ee.FeatureCollection.randomPoints(
        region=aoi,
        points=10,  # Number of random points
        seed=123  # Fixed seed for reproducibility
    )
    
    sampled_data = crop_stress.addBands(water_stress).sampleRegions(
        collection=sample_points,
        scale=100,  # Scale in meters
        geometries=True
    ).getInfo()
    
    for feature in sampled_data['features']:
        coords = feature['geometry']['coordinates']
        lon, lat = coords[0], coords[1]
        crop_val = feature['properties']['CropStress']
        water_val = feature['properties']['WaterStress']
        
        if crop_val > 0:
            severity = "severe" if crop_val == 2 else "moderate"
            recommendations.append({
                "type": f"Crop Stress ({severity})",
                "latitude": lat,
                "longitude": lon,
                "recommendation": "Apply irrigation and fertilizers to improve crop health."
            })
        
        if water_val > 0:
            recommendations.append({
                "type": "Water Stress",
                "latitude": lat,
                "longitude": lon,
                "recommendation": "Increase irrigation and monitor soil moisture levels."
            })
    
    return recommendations

@app.route('/analyze-satellite', methods=['POST'])
def analyze_satellite():
    """
    Endpoint to analyze satellite data and generate recommendations.
    """
    try:
        # Parse request data
        data = request.json
        coords = data.get("coords", None)  # Optional user-provided coordinates
        start_date = data.get("startDate", "2023-01-01")
        end_date = data.get("endDate", "2023-10-01")

        # Validate input
        if not start_date or not end_date:
            return jsonify({"error": "Start date and end date are required."}), 400

        # Get AOI
        aoi = get_user_aoi(coords)

        # Analyze and classify problem areas
        crop_stress, water_stress = analyze_and_mark_problem_areas(aoi, start_date, end_date)

        # Generate recommendations
        recommendations = generate_recommendations(crop_stress, water_stress, aoi)

        # Return results
        return jsonify({"recommendations": recommendations})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=4000)