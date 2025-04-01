import React, { useState } from "react";
import Header from "./Header"; // Import the reusable Header component

const CropDiseaseManagement = () => {
  const [selectedFile, setSelectedFile] = useState(null); // State for uploaded file
  const [cropType, setCropType] = useState(""); // State for selected crop type
  const [analysisResult, setAnalysisResult] = useState(null); // State for analysis result
  const [loading, setLoading] = useState(false); // State for loading indicator
  const [error, setError] = useState(null); // State for error handling

  // Handle file selection
  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      setSelectedFile(file);
      setAnalysisResult(null); // Reset previous results
      setError(null); // Reset errors
    }
  };

  // Handle crop type selection
  const handleCropTypeChange = (event) => {
    setCropType(event.target.value);
  };

  // Function to analyze the image using the backend API
  const analyzeImage = async () => {
    if (!selectedFile) {
      setError("Please select an image first.");
      return;
    }

    if (!cropType) {
      setError("Please select a crop type.");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // Create a FormData object
      const formData = new FormData();
      formData.append("file", selectedFile); // Append the file
      formData.append("cropType", cropType); // Append the crop type

      // Make a POST request to the backend API
      const response = await fetch("http://localhost:5000/api/analyze-crop-disease", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || "Failed to analyze the image.");
      }

      const data = await response.json();

      // Update the state with the analysis result
      setAnalysisResult(data);
    } catch (err) {
      setError(err.message || "Error analyzing the image. Please try again.");
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
        <h1>Crop Disease Management</h1>
        <p>Upload an image of your crop to detect diseases and get recommendations.</p>

        {/* Crop Type Selection */}
        <div style={{ margin: "20px 0", textAlign: "center" }}>
          <label htmlFor="crop-type" style={{ marginRight: "10px" }}>
            Select Crop Type:
          </label>
          <select
            id="crop-type"
            value={cropType}
            onChange={handleCropTypeChange}
            style={{
              padding: "8px",
              borderRadius: "5px",
              border: "2px solid var(--primary-green)",
              background: "rgba(0, 0, 0, 0.68)",
              color: "#ffffff",
            }}
          >
            <option value="">--Select Crop--</option>
            <option value="Rice">Rice</option>
            <option value="Wheat">Wheat</option>
            <option value="Corn">Corn</option>
          </select>
        </div>

        {/* File Upload Section */}
        <div style={{ margin: "20px 0", textAlign: "center" }}>
          <label htmlFor="file-upload" className="file-label">
            <span>Choose Image</span>
          </label>
          <input
            id="file-upload"
            type="file"
            accept="image/*"
            onChange={handleFileChange}
            style={{ display: "none" }}
          />
          {selectedFile && (
            <p style={{ marginTop: "10px", color: "#ffffff" }}>Selected File: {selectedFile.name}</p>
          )}
        </div>

        {/* Analyze Button */}
        <button onClick={analyzeImage} disabled={loading} style={{ padding: "10px 20px" }}>
          {loading ? "Analyzing..." : "Analyze Image"}
        </button>

        {/* Error Message */}
        {error && <p style={{ color: "red", marginTop: "10px" }}>{error}</p>}

        {/* Analysis Results */}
        {analysisResult && (
          <div style={{ marginTop: "20px", textAlign: "left" }}>
            <h2>Analysis Results:</h2>
            <p><strong>Disease Detected:</strong> {analysisResult.disease}</p>
            <p><strong>Confidence:</strong> {analysisResult.confidence}%</p>
            <p><strong>Recommendation:</strong> {analysisResult.recommendation}</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default CropDiseaseManagement;