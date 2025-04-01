import ee
import datetime
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.impute import SimpleImputer
import matplotlib.pyplot as plt
import base64
import io

# Initialize Earth Engine
try:
    ee.Initialize()
except Exception as e:
    print(f"Error initializing Earth Engine: {e}")
    ee.Authenticate()
    ee.Initialize()

# Function to get user-defined AOI
def get_user_aoi(coords):
    if coords:
        try:
            coords = list(map(float, coords.split(",")))
            if len(coords) == 4:
                return ee.Geometry.Rectangle(coords)
        except ValueError:
            pass
    # Default to Tumkur, Karnataka
    return ee.Geometry.Rectangle([76.5, 13.2, 77.5, 14.0])

# Fetch NDVI time series data
def fetch_ndvi_data(aoi, years=3):
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=years * 365)

    collection = ee.ImageCollection("COPERNICUS/S2") \
        .filterBounds(aoi) \
        .filterDate(str(start_date), str(end_date)) \
        .filterMetadata('CLOUDY_PIXEL_PERCENTAGE', 'less_than', 20) \
        .select(['B8', 'B4'])

    ndvi_collection = collection.map(
        lambda img: img.addBands(img.normalizedDifference(['B8', 'B4']).rename('NDVI'))
    )

    def extract_data(image):
        stats = image.select('NDVI').reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=aoi,
            scale=1000,
            maxPixels=1e8
        )
        return ee.Feature(None, {
            'date': image.date().format('YYYY-MM-dd'),
            'NDVI': stats.get('NDVI')
        })

    features = ndvi_collection.map(extract_data).filter(ee.Filter.notNull(['NDVI']))
    dates = features.aggregate_array('date').getInfo()
    ndvi_values = features.aggregate_array('NDVI').getInfo()

    return pd.DataFrame({'Date': dates, 'NDVI': ndvi_values})

# Preprocess NDVI data
def preprocess_data(df):
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.groupby('Date').mean().reset_index()
    df = df.set_index('Date').sort_index()
    df = df.resample('D').interpolate(method='linear', limit_direction='both')  # Fill missing values
    return df.dropna()

# Detect anomalies in NDVI data
def detect_anomalies(df):
    df['rolling_mean'] = df['NDVI'].rolling(window=30).mean()
    df['rolling_std'] = df['NDVI'].rolling(window=30).std()

    # Z-score method
    df['z_score'] = (df['NDVI'] - df['rolling_mean']) / df['rolling_std']
    df['z_anomaly'] = df['z_score'].abs() > 2.5

    # Handle missing values before passing to IsolationForest
    imputer = SimpleImputer(strategy='mean')  # Replace NaN with column mean
    features = imputer.fit_transform(df[['NDVI', 'rolling_mean', 'rolling_std']].values)

    # Isolation Forest
    clf = IsolationForest(contamination=0.05, random_state=42)
    df['if_anomaly'] = clf.fit_predict(features) == -1

    df['anomaly'] = df['z_anomaly'] | df['if_anomaly']
    return df

# Predict future anomalies
def predict_future_anomalies(df, days=30):
    last_date = df.index[-1]
    future_dates = pd.date_range(last_date + datetime.timedelta(days=1), periods=days, freq='D')

    # Use rolling mean and std for prediction
    rolling_mean = df['rolling_mean'].iloc[-30:].mean()
    rolling_std = df['rolling_std'].iloc[-30:].mean()

    future_ndvi = np.random.normal(rolling_mean, rolling_std, size=len(future_dates))
    future_df = pd.DataFrame({'Date': future_dates, 'NDVI': future_ndvi})
    future_df.set_index('Date', inplace=True)

    # Handle missing values before passing to IsolationForest
    imputer = SimpleImputer(strategy='mean')
    future_features = imputer.fit_transform(future_df[['NDVI']].values)

    # Predict anomalies
    clf = IsolationForest(contamination=0.05, random_state=42)
    future_df['anomaly'] = clf.fit_predict(future_features) == -1

    return future_df

# Analyze and mark problem areas
def analyze_and_mark_problem_areas(aoi, start_date, end_date):
    """
    Fetch Sentinel-2 data, calculate NDVI, MSI, and NDWI, and classify stress areas.
    """
    sentinel2_collection = ee.ImageCollection("COPERNICUS/S2") \
        .filterBounds(aoi) \
        .filterDate(start_date, end_date) \
        .sort('CLOUD_COVERAGE_ASSESSMENT')
    
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

# Plot NDVI data and anomalies
def plot_ndvi_graph(ndvi_df, future_df=None):
    plt.figure(figsize=(12, 6))
    plt.plot(ndvi_df.index, ndvi_df['NDVI'], label='NDVI', color='green', linewidth=2)

    # Highlight anomalies
    anomalies = ndvi_df[ndvi_df['anomaly']]
    plt.scatter(anomalies.index, anomalies['NDVI'], color='red', label='Anomalies', zorder=5)

    if future_df is not None:
        plt.plot(future_df.index, future_df['NDVI'], label='Future NDVI', color='blue', linestyle='--', linewidth=2)

        # Highlight future anomalies
        future_anomalies = future_df[future_df['anomaly']]
        plt.scatter(future_anomalies.index, future_anomalies['NDVI'], color='orange', label='Future Anomalies', zorder=5)

    plt.title('NDVI Time Series with Anomalies')
    plt.xlabel('Date')
    plt.ylabel('NDVI')
    plt.legend()
    plt.grid(True)

    # Save plot to a BytesIO buffer
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.close()

    # Encode image to base64
    image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return image_base64

# Main function for satellite analysis
def analyze_satellite_logic(data):
    try:
        coords = data.get("coords", None)
        start_date = data.get("startDate", "2023-01-01")
        end_date = data.get("endDate", "2023-10-01")

        if not start_date or not end_date:
            raise ValueError("Start date and end date are required.")

        aoi = get_user_aoi(coords)

        # Fetch and process NDVI data
        ndvi_df = fetch_ndvi_data(aoi)
        ndvi_df = preprocess_data(ndvi_df)
        ndvi_df = detect_anomalies(ndvi_df)

        # Predict future anomalies
        future_df = predict_future_anomalies(ndvi_df)

        # Analyze crop and water stress
        crop_stress, water_stress = analyze_and_mark_problem_areas(aoi, start_date, end_date)
        recommendations = generate_recommendations(crop_stress, water_stress, aoi)

        # Plot NDVI graph
        image_base64 = plot_ndvi_graph(ndvi_df, future_df)

        # Filter future anomalies to only include dates where anomaly = True
        future_anomalies = future_df[future_df['anomaly']].index.strftime('%Y-%m-%d').tolist()

        # Return response
        return {
            "ndvi_plot": image_base64,
            "future_anomalies": future_anomalies,
            "recommendations": recommendations
        }

    except Exception as e:
        raise Exception(f"Error during satellite analysis: {str(e)}")