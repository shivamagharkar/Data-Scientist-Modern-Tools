import azure.functions as func
import datetime
import json
import logging
import pickle
import pandas as pd
import os

app = func.FunctionApp()

@app.route(route="score_model", auth_level=func.AuthLevel.ANONYMOUS)
def score_model(req: func.HttpRequest) -> func.HttpResponse:
    # Get parameters from the request
    supplier = req.params.get('supplier')
    quantity = req.params.get('quantity')
    warehouse = req.params.get('warehouse')
    item_name = req.params.get('item_name')
    schedule_date_str = req.params.get('schedule_date')  # Expected format 'YYYY-MM-DD'

    # Check if any parameter is missing
    missing_params = [
        param for param, value in [
            ("supplier", supplier),
            ("quantity", quantity),
            ("warehouse", warehouse),
            ("item_name", item_name),
            ("schedule_date", schedule_date_str)
        ] if not value
    ]
    if missing_params:
        return func.HttpResponse(
            json.dumps({"error": f"Missing parameters: {', '.join(missing_params)}"}),
            status_code=400
        )

    # Convert quantity to integer
    try:
        quantity = int(quantity)
    except ValueError:
        return func.HttpResponse(
            json.dumps({"error": "Invalid quantity. It must be an integer."}),
            status_code=400
        )

    # Convert schedule_date to datetime and extract the month
    try:
        schedule_date = datetime.datetime.strptime(schedule_date_str, "%Y-%m-%d")
        schedule_month = schedule_date.month
    except ValueError:
        return func.HttpResponse(
            json.dumps({"error": "Invalid schedule_date format. Use 'YYYY-MM-DD'."}),
            status_code=400
        )

    # Log the current working directory
    logging.info(f"Current working directory: {os.getcwd()}")

    # Path to the model
    model_path = os.path.join(os.path.dirname(__file__), 'models', 'best_gbm_model.pkl')
    logging.info(f"Looking for model at: {model_path}")

    # Check if the file exists
    if os.path.exists(model_path):
        logging.info("Model file found!")
    else:
        logging.error(f"Model file not found at {model_path}")
        return func.HttpResponse(
            json.dumps({"error": "Model file not found."}),
            status_code=500
        )

    # Try loading the model
    try:
        model = pickle.load(open(model_path, 'rb'))
        logging.info("Model loaded successfully!")
    except Exception as e:
        logging.error(f"Error loading model: {e}")
        return func.HttpResponse(
            json.dumps({"error": "Model could not be loaded."}),
            status_code=500
        )

    # List of suppliers, warehouses, and item names based on the trained model
    suppliers = ['Aromatico', 'Beans Inc.', 'Fair Trade AG', 'Farmers of Brazil', 'Handelskontor Hamburg']
    warehouses = ['Naples - RR', 'Amsterdam - RR', 'London - RR', 'Hamburg - RR', 'Barcelona - RR', 'Nairobi - RR', 'Istanbul - RR']
    item_names = ['Excelsa', 'Maragogype', 'Maragogype Type B', 'Robusta', 'Liberica', 'Arabica']

    # Prepare the data for prediction
    data = {
        "total_qty": [quantity],
        "schedule_month": [schedule_month],
    }

    # One-hot encode categorical features (supplier, warehouse, item_name)
    for s in suppliers:
        data[f'd_sup_{s}'] = [1 if s == supplier else 0]

    for w in warehouses:
        data[f'd_wh_{w}'] = [1 if w == warehouse else 0]

    for i in item_names:
        data[f'd_item_{i}'] = [1 if i == item_name else 0]

    # Create the DataFrame
    payload = pd.DataFrame(data)

    # Log the columns and data types of the payload
    logging.info(f"Payload columns before reordering: {payload.columns.tolist()}")
    logging.info(f"Payload data types: {payload.dtypes.tolist()}")

    # Ensure columns are ordered according to the model
    model_columns = model.feature_names_in_  # Get the model's expected feature names
    logging.info(f"Model columns: {model_columns}")

    # Reorder payload columns to match the model
    payload = payload[model_columns]

    # Log the reordered columns
    logging.info(f"Payload columns after reordering: {payload.columns.tolist()}")

    # Check for NaN or infinite values in the payload
    if payload.isnull().values.any() or (payload == float('inf')).values.any():
        logging.error("Input payload contains NaN or infinite values.")
        return func.HttpResponse(
            json.dumps({"error": "Input payload contains invalid values."}),
            status_code=400
        )

    # Make the prediction using the loaded model
    try:
        prediction = model.predict(payload)[0]
        logging.info(f"Prediction: {prediction}")
    except Exception as e:
        logging.error(f"Prediction error: {e}")
        logging.error(f"Input payload: {payload}")  # Log the input causing the error
        return func.HttpResponse(
            json.dumps({"error": f"Error during prediction: {str(e)}"}),
            status_code=500
        )

    # Return the prediction response
    return func.HttpResponse(
        json.dumps({
            "message": f"Model scored successfully with quantity: {quantity}, supplier: {supplier}, warehouse: {warehouse}, item_name: {item_name}, and schedule_date: {schedule_date_str}.",
            "prediction": prediction,
            "status_code": 200
        }),
        status_code=200
    )
