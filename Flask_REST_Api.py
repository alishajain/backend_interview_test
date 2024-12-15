from flask import Flask, request, jsonify
import threading
import time
import random

def generate_mock_data():
    """Reading machine data every 10 seconds and calculates moving average."""
    global processed_data
    mock_data = []

    while True:
        new_data = {
            "temperature": random.uniform(20.0, 100.0),
            "speed": random.uniform(500, 1500),
            "status": random.choice(["RUNNING", "STOPPED"])
        }
        mock_data.append(new_data)

        if len(mock_data) > 5:
            mock_data.pop(0)

        moving_avg = {
            "temperature_avg": sum(d["temperature"] for d in mock_data) / len(mock_data),
            "speed_avg": sum(d["speed"] for d in mock_data) / len(mock_data),
            "status": mock_data[-1]["status"]
        }

        # Update global processed data
        processed_data = moving_avg

        # Wait 10 seconds before the next reading
        time.sleep(10)

app = Flask(__name__)

# In-memory storage for machine data and status
processed_data = {}  # This will hold the machine data
machine_status = "IDLE"  # Default status

# Allowed statuses for validation
ALLOWED_STATUSES = {"STARTED", "COMPLETED", "IDLE"}

@app.route('/data', methods=['GET'])
def get_data():
    """Endpoint to return processed machine data."""
    return jsonify({"data": processed_data, "status": machine_status}), 200

@app.route('/status', methods=['POST'])
def update_status():
    """Endpoint to update the machine's job status."""
    try:
        request_data = request.get_json()
        if not request_data or 'status' not in request_data:
            return jsonify({"error": "Missing 'status' field."}), 400

        status = request_data['status']
        if status not in ALLOWED_STATUSES:
            return jsonify({"error": f"Invalid status. Allowed values are {ALLOWED_STATUSES}"}), 400

        global machine_status
        machine_status = status
        return jsonify({"message": "Status updated successfully.", "status": machine_status}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Start background thread for data ingestion and processing
    threading.Thread(target=generate_mock_data, daemon=True).start()
    app.run(debug=True)
