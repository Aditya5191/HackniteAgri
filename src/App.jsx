import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import LiveStats from "./LiveStats"; // Import LiveStats component
import SatelliteData from "./SatelliteData"; // Import SatelliteData component
import CropDiseaseManagement from "./CropDiseaseManagement"; // Import CropDiseaseManagement component
import Chatbot from "./chatbot"; // Import the Chatbot component

// Main App Component
const App = () => {
  return (
    <Router>
      <div>
        {/* Main Content */}
        <Routes>
          <Route path="/" element={<LiveStats />} />
          <Route path="/satellite-data" element={<SatelliteData />} />
          <Route path="/crop-disease-management" element={<CropDiseaseManagement />} />
        </Routes>

        {/* Global Chatbot */}
        <Chatbot />
      </div>
    </Router>
  );
};

export default App;