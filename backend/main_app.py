from iot import get_iot_data
from cd import analyze_crop_disease
# from cb import chatbot
# from sat import analyze_satellite_logic
from flask import Flask, jsonify, request
from flask_cors import CORS

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing (CORS)

# Route for IoT Data
@app.route('/api/analyze-crop-disease', methods=['POST'])
def analyze_crop():
    try:
        # Check if the POST request contains a file
        if 'file' not in request.files:
            return jsonify({"error": "No file part"}), 400

        file = request.files['file']

        # Get the crop type from the form data
        crop_type = request.form.get('cropType')
        if not crop_type:
            return jsonify({"error": "Crop type is required"}), 400

        # Call the analyze_crop_disease function
        result = analyze_crop_disease(file, crop_type)

        # Return the response
        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route for Crop Disease Analysis
@app.route('/api/iot-data', methods=['GET'], endpoint='iot_data_endpoint')  # Explicit endpoint name
def iot_data():
    try:
        response = get_iot_data()
        return jsonify(response), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route for Chatbot Handling
# @app.route('/api/chat', methods=['POST'])
# def handle_chat():
#     try:
#         # Parse the JSON payload from the frontend
#         data = request.json
#         user_input = data.get("message", "").strip()
#         if not user_input:
#             return jsonify({"error": "Message cannot be empty."}), 400
#         # Call the chatbot function to generate a response
#         bot_response = chatbot(user_input)
#         # Return the response as JSON
#         return jsonify({"response": bot_response}), 200
#     except Exception as e:
#         # Handle unexpected errors gracefully
#         return jsonify({"error": f"An error occurred: {str(e)}"}), 500

# Route for Satellite Data Analysis
@app.route('/api/analyze-satellite', methods=['POST'])
# def analyze_satellite():
#     try:
#         # Parse the JSON payload from the frontend
#         data = request.json
#         result = analyze_satellite_logic(data)
#         # Return the response as JSON
#         return jsonify(result), 200
#     except Exception as e:
#         # Handle unexpected errors gracefully
#         return jsonify({"error": str(e)}), 500

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)