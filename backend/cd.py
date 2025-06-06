import os
from PIL import Image
import numpy as np
import tensorflow as tf

# Configure upload folder and allowed extensions
UPLOAD_FOLDER = 'uploads'
MODEL_DIR = 'crop_disease_models'  # Directory containing .tflite models
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Helper function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Function to preprocess the image for TensorFlow Lite models
def preprocess_image(image_path, target_size=(224, 224)):
    img = Image.open(image_path).convert('RGB')  # Convert to RGB if needed
    img = img.resize(target_size)  # Resize to match model input size
    img_array = np.array(img) / 255.0  # Normalize pixel values
    img_array = np.expand_dims(img_array, axis=0).astype(np.float32)  # Add batch dimension
    return img_array

# Main function to analyze crop disease
def analyze_crop_disease(file, crop_type):
    try:
        # Validate file
        if not allowed_file(file.filename):
            raise ValueError("Invalid file type")

        # Construct the path to the model file
        model_filename = f"{crop_type.lower()}.tflite"
        MODEL_PATH = os.path.join(MODEL_DIR, model_filename)

        # Ensure the upload folder exists
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        filename = file.filename
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)

        # Check if the model file exists
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(f"Model file not found for crop type '{crop_type}'.")

        # Load the TensorFlow Lite model (disable XNNPACK)
        interpreter = tf.lite.Interpreter(
            model_path=MODEL_PATH,
            experimental_delegates=None,  # Disable XNNPACK
        )
        interpreter.allocate_tensors()

        # Get input and output details
        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()

        # Preprocess the image
        img_array = preprocess_image(file_path, target_size=(input_details[0]['shape'][1], input_details[0]['shape'][2]))

        # Perform inference
        interpreter.set_tensor(input_details[0]['index'], img_array)
        interpreter.invoke()
        predictions = interpreter.get_tensor(output_details[0]['index'])

        # Post-process the predictions
        predicted_class_index = np.argmax(predictions, axis=1)[0]  # Get the predicted class index
        confidence = np.max(predictions) * 100  # Confidence score as percentage

        # Map the predicted class to a disease name (example mapping)
        classes = {
            "rice": ['Bacterial_leaf_blight', 'Brown_spot', 'Leaf_smut'],
            "wheat": ['Rust', 'Powdery_mildew', 'Septoria_leaf_blotch'],
            "corn": ['Northern_leaf_blight', 'Gray_leaf_spot', 'Common_rust']
        }
        predicted_disease = classes[crop_type.lower()][predicted_class_index]

        # Generate a recommendation based on the disease
        recommendations = {
            "Bacterial_leaf_blight": "Apply copper-based fungicides and ensure proper drainage.",
            "Brown_spot": "Remove infected leaves and use fungicides like Mancozeb.",
            "Leaf_smut": "Use resistant varieties and practice crop rotation.",
            "Rust": "Apply systemic fungicides and monitor moisture levels.",
            "Powdery_mildew": "Use sulfur-based fungicides and improve air circulation.",
            "Septoria_leaf_blotch": "Apply fungicides early and rotate crops.",
            "Northern_leaf_blight": "Use resistant hybrids and manage residue.",
            "Gray_leaf_spot": "Apply strobilurin fungicides and reduce plant stress.",
            "Common_rust": "Use fungicides and select resistant varieties."
        }
        recommendation = recommendations.get(predicted_disease, "Consult an expert for further guidance.")

        # Clean up the uploaded file
        os.remove(file_path)

        # Return the results
        return {
            "disease": predicted_disease,
            "confidence": round(confidence, 2),
            "recommendation": recommendation,
        }

    except Exception as e:
        raise Exception(f"Error during analysis: {str(e)}")