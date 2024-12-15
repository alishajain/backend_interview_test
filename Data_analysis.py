from flask import Flask, request, jsonify
from collections import deque
import threading
import time
import random
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class MachineDataProcessor:
    """Class to handle machine data processing and moving average calculations."""
    def __init__(self, max_readings=5, interval=10):
        self.data_queue = deque(maxlen=max_readings)
        self.processed_data = {}
        self.interval = interval

    def generate_mock_data(self):
        """Simulates reading machine data and calculates moving average."""
        while True:
            new_data = {
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
                "temperature": random.uniform(20.0, 100.0),
                "speed": random.uniform(500, 1500),
                "status": random.choice(["RUNNING", "STOPPED"])
            }
            logging.info(f"Generated new data: {new_data}")
            self.data_queue.append(new_data)
            self.calculate_moving_average()
            time.sleep(self.interval)

    def calculate_moving_average(self):
        """Calculates moving averages from the last N readings."""
        if not self.data_queue:
            return

        self.processed_data = {
            "temperature_avg": sum(d["temperature"] for d in self.data_queue) / len(self.data_queue),
            "speed_avg": sum(d["speed"] for d in self.data_queue) / len(self.data_queue),
            "status": self.data_queue[-1]["status"],
            "raw_data": list(self.data_queue)  # Include raw data for analytics
        }
        logging.info(f"Updated processed data: {self.processed_data}")

    def get_statistics(self):
        """Calculate analytics for the processed data."""
        data = self.processed_data.get("raw_data", [])
        if not data:
            return {}

        values = [entry['temperature'] for entry in data]
        average = sum(values) / len(values)
        maximum = max(values)
        minimum = min(values)

        # Detect anomalies (20% deviation)
        threshold = 0.2 * average
        anomalies = [entry for entry in data if abs(entry['temperature'] - average) > threshold]

        return {
            "average_temperature": average,
            "max_temperature": maximum,
            "min_temperature": minimum,
            "anomalies": anomalies
        }

# Flask app setup
app = Flask(__name__)

# In-memory storage for machine status
machine_status = "IDLE"
machine_status_lock = threading.Lock()
ALLOWED_STATUSES = {"STARTED", "COMPLETED", "IDLE"}

# Initialize data processor
processor = MachineDataProcessor()

@app.route('/data', methods=['GET'])
def get_data():
    """Endpoint to return processed machine data with analytics."""
    analytics = processor.get_statistics()
    return jsonify({"data": processor.processed_data, "analytics": analytics, "status": machine_status}), 200

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
        with machine_status_lock:
            machine_status = status
        logging.info(f"Updated machine status to: {machine_status}")
        return jsonify({"message": "Status updated successfully.", "status": machine_status}), 200
    except Exception as e:
        logging.error(f"Error updating status: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Start background thread for data ingestion and processing
    threading.Thread(target=processor.generate_mock_data, daemon=True).start()
    logging.info("Starting Flask application...")
    app.run(debug=True)
