import React, { useState } from "react";
import Header from "./Header"; // Import the reusable Header component

const SatelliteData = () => {
  const [coords, setCoords] = useState(""); // State for user-provided coordinates
  const [startDate, setStartDate] = useState("2023-01-01"); // Default start date
  const [endDate, setEndDate] = useState("2023-10-01"); // Default end date
  const [recommendations, setRecommendations] = useState([]); // Recommendations from backend
  const [loading, setLoading] = useState(false); // Loading state
  const [error, setError] = useState(null); // Error state

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await fetch("http://localhost:4000/analyze-satellite", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ coords, startDate, endDate }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || "Failed to analyze satellite data.");
      }

      const data = await response.json();
      setRecommendations(data.recommendations);
    } catch (err) {
      setError(err.message || "An error occurred while analyzing satellite data.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      {/* Include the Header */}
      <Header />

      {/* Main Content */}
      <div className="container" style={{ paddingTop: "60px" }}>
        <h1>Satellite Data Analysis</h1>
        <p>Analyze satellite data for crop health monitoring.</p>

        {/* Form Section */}
        <form onSubmit={handleSubmit} style={{ margin: "20px 0", textAlign: "center" }}>
          {/* Coordinates Input */}
          <div style={{ marginBottom: "10px" }}>
            <label htmlFor="coords" style={{ marginRight: "10px" }}>
              Coordinates (min_lon,min_lat,max_lon,max_lat):
            </label>
            <input
              type="text"
              id="coords"
              value={coords}
              onChange={(e) => setCoords(e.target.value)}
              placeholder="e.g., 76.5,13.2,77.5,14.0"
              style={{
                padding: "8px",
                borderRadius: "5px",
                border: "2px solid var(--primary-green)",
                background: "rgba(0, 0, 0, 0.68)",
                color: "#ffffff",
              }}
            />
          </div>

          {/* Start Date Input */}
          <div style={{ marginBottom: "10px" }}>
            <label htmlFor="startDate" style={{ marginRight: "10px" }}>
              Start Date:
            </label>
            <input
              type="date"
              id="startDate"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              style={{
                padding: "8px",
                borderRadius: "5px",
                border: "2px solid var(--primary-green)",
                background: "rgba(0, 0, 0, 0.68)",
                color: "#ffffff",
              }}
            />
          </div>

          {/* End Date Input */}
          <div style={{ marginBottom: "10px" }}>
            <label htmlFor="endDate" style={{ marginRight: "10px" }}>
              End Date:
            </label>
            <input
              type="date"
              id="endDate"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              style={{
                padding: "8px",
                borderRadius: "5px",
                border: "2px solid var(--primary-green)",
                background: "rgba(0, 0, 0, 0.68)",
                color: "#ffffff",
              }}
            />
          </div>

          {/* Analyze Button */}
          <button
            type="submit"
            disabled={loading}
            style={{
              padding: "10px 20px",
              backgroundColor: "var(--primary-green)",
              color: "#fff",
              border: "none",
              borderRadius: "5px",
              cursor: "pointer",
            }}
          >
            {loading ? "Analyzing..." : "Analyze"}
          </button>
        </form>

        {/* Error Message */}
        {error && <p style={{ color: "red", marginTop: "10px", textAlign: "center" }}>{error}</p>}

        {/* Recommendations */}
        {recommendations.length > 0 && (
          <div style={{ marginTop: "20px", textAlign: "left" }}>
            <h2>Recommendations:</h2>
            <ul style={{ listStyleType: "none", paddingLeft: "0" }}>
              {recommendations.map((rec, index) => (
                <li key={index} style={{ marginBottom: "10px" }}>
                  <strong>Type:</strong> {rec.type}<br />
                  <strong>Location:</strong> Latitude={rec.latitude}, Longitude={rec.longitude}<br />
                  <strong>Recommendation:</strong> {rec.recommendation}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
};

export default SatelliteData;