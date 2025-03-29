# Crop Disease Management

This project is a web application for detecting crop diseases using machine learning models. The frontend is built with React, and the backend is built with Flask. The application allows users to upload an image of a crop, select the crop type (e.g., Rice, Wheat, Corn), and receive predictions about the disease affecting the crop, along with recommendations for treatment.

## Table of Contents

- [Installation](#installation)
- [Features](#features)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Errors](#errors)
- [Folder Structure](#folder-structure)
- [Demo](#demo)

---

## Installation

### Prerequisites

- Python 3.8 or higher
- Node.js and npm
- pip for Python package management

### Backend Setup

1. Clone the repository:
    ```sh
    git clone https://github.com/AmeyaMprojects/IITK_HACK_2
    cd IITK_HACK_2/backend
    ```

2. Install the required Python packages:
    ```sh
    pip install -r requirements.txt
    ```

3. Place the TensorFlow Lite models (`rice.tflite`, `wheat.tflite`, etc.) in the `backend/crop_disease_models/` directory.

4. Run the Flask application:
    ```sh
    python app.py
    ```

### Frontend Setup

1. In a new terminal, navigate to the root directory of the project:
    ```sh
    cd IITK_HACK_2/frontend
    ```

2. Install the required npm packages:
    ```sh
    npm install
    ```

3. Start the React application:
    ```sh
    npm run dev
    ```

---

## Features

- **Image Upload**: Users can upload an image of a crop leaf.
- **Crop Type Selection**: Users can select the crop type (e.g., Rice, Wheat, Corn).
- **Disease Detection**: The backend uses TensorFlow Lite models to predict the disease affecting the crop.
- **Recommendations**: Based on the detected disease, the application provides actionable recommendations for treatment.
- **Dynamic Model Loading**: The backend dynamically loads the appropriate TensorFlow Lite model based on the selected crop type.

---

## Usage

1. Open your browser and navigate to [http://localhost:3000](http://localhost:3000).
2. Select the crop type (e.g., Rice, Wheat, Corn) from the dropdown menu.
3. Upload an image of the crop leaf.
4. Click the "Analyze Image" button to detect the disease.
5. View the results, including:
   - The detected disease.
   - Confidence score.
   - Treatment recommendations.

---

## API Endpoints

### `/analyze` (POST)

- **Description**: Analyze an uploaded image to detect crop diseases.
- **Request**:
  - Multipart form data containing:
    - `file`: The uploaded image file.
    - `cropType`: The selected crop type (e.g., Rice, Wheat, Corn).
- **Response**: JSON object containing:
  ```json
  {
    "disease": "Bacterial_leaf_blight",
    "confidence": 92.5,
    "recommendation": "Apply copper-based fungicides and ensure proper drainage."
  }