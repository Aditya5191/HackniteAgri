import React, { useState, useEffect } from "react";
import axios from "axios";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import Speedometer from "react-d3-speedometer";
import Header from "./Header"; // Import the Header component

const LiveStats = () => {
  const [sensorData, setSensorData] = useState([]);
  const [recommendations, setRecommendations] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await axios.get("http://localhost:5000/api/iot-data");
        const newData = {
          timestamp: response.data.Timestamp,
          soil_moisture: response.data.Soil_Moisture_pct,
          temperature: response.data.Temperature_C,
          humidity: response.data.Humidity_pct,
          rainfall: response.data.Rainfall_mm,
          ndvi: response.data.NDVI_Mean,
          soil_ph: response.data.Soil_pH,
          soil_ec: response.data.Soil_EC_dS_m,
        };
        const newRecommendations = {
          water_needed: response.data.Water_Needed_liters_ha_day,
          fertilizer_needed: response.data.Fertilizer_Needed_kg_ha,
        };

        setSensorData((prevData) => [...prevData, newData].slice(-10));
        setRecommendations(newRecommendations);
      } catch (err) {
        setError("Error fetching IoT data. Please try again.");
      } finally {
        setLoading(false);
      }
    };

    const interval = setInterval(fetchData, 5000);
    fetchData();
    return () => clearInterval(interval);
  }, []);

  return (
    <div>
      {/* Include the Header */}
      <Header />

      {/* Main Content */}
      <div className="container" style={{ paddingTop: "60px" }}>
        <h1>Live Stats</h1>

        {error && <p style={{ color: "red" }}>{error}</p>}
        {loading && <p>Loading...</p>}

        {recommendations && (
          <div>
            <h2>Recommendations:</h2>
            <div style={{ display: "flex", justifyContent: "space-between" }}>
              <div style={{ width: "45%" }}>
                <h3>Water Needed</h3>
                <Speedometer
                  value={recommendations.water_needed}
                  minValue={0}
                  maxValue={200}
                  needleColor="black"
                  startColor="#00bfff"
                  segments={5}
                  endColor="#0000ff"
                  textColor="#ffffff"
                  currentValueText={`Liters/hectare/day: ${recommendations.water_needed}`}
                />
              </div>
              <div style={{ width: "45%" }}>
                <h3>Fertilizer Needed</h3>
                <Speedometer
                  value={recommendations.fertilizer_needed}
                  minValue={0}
                  maxValue={200}
                  needleColor="black"
                  startColor="#00bfff"
                  segments={5}
                  endColor="#0000ff"
                  textColor="#ffffff"
                  currentValueText={`Kg/hectare: ${recommendations.fertilizer_needed}`}
                />
              </div>
            </div>
          </div>
        )}

        {sensorData.length > 0 && (
          <div>
            <h2>Live Sensor Readings</h2>
            <ResponsiveContainer width="100%" height={400}>
              <LineChart data={sensorData}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255, 255, 255, 0.3)" />
                <XAxis dataKey="timestamp" stroke="#ffffff" />
                <YAxis stroke="#ffffff" />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "rgba(0, 0, 0, 0.7)",
                    border: "none",
                    borderRadius: "5px",
                  }}
                  itemStyle={{ color: "#ffffff" }}
                />
                <Line type="monotone" dataKey="soil_moisture" stroke="#00f0ff" strokeWidth={2} dot={{ fill: "#00f0ff" }} name="Soil Moisture (%)" />
                <Line type="monotone" dataKey="temperature" stroke="#ff0000" strokeWidth={2} dot={{ fill: "#ff0000" }} name="Temperature (°C)" />
                <Line type="monotone" dataKey="humidity" stroke="#00ff00" strokeWidth={2} dot={{ fill: "#00ff00" }} name="Humidity (%)" />
                <Line type="monotone" dataKey="rainfall" stroke="#0000ff" strokeWidth={2} dot={{ fill: "#0000ff" }} name="Rainfall (mm)" />
                <Line type="monotone" dataKey="ndvi" stroke="#ffff00" strokeWidth={2} dot={{ fill: "#ffff00" }} name="NDVI Mean" />
                <Line type="monotone" dataKey="soil_ph" stroke="#ff00ff" strokeWidth={2} dot={{ fill: "#ff00ff" }} name="Soil pH" />
                <Line type="monotone" dataKey="soil_ec" stroke="#00ffff" strokeWidth={2} dot={{ fill: "#00ffff" }} name="Soil EC (dS/m)" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>
    </div>
  );
};

export default LiveStats;