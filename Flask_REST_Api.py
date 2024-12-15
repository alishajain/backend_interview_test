from flask import Flask, request, jsonify
from collections import deque
import threading
import time
import random

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
                "temperature": random.uniform(20.0, 100.0),
                "speed": random.uniform(500, 1500),
                "status": random.choice(["RUNNING", "STOPPED"])
            }
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
            "status": self.data_queue[-1]["status"]
        }

# Flask app setup
app = Flask(__name__)

# In-memory storage for machine status
machine_status = "IDLE"
ALLOWED_STATUSES = {"STARTED", "COMPLETED", "IDLE"}

# Initialize data processor
processor = MachineDataProcessor()

@app.route('/data', methods=['GET'])
def get_data():
    """Endpoint to return processed machine data."""
    return jsonify({"data": processor.processed_data, "status": machine_status}), 200

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
    threading.Thread(target=processor.generate_mock_data, daemon=True).start()
    app.run(debug=True)
