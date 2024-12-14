import time
import json
from collections import deque
from datetime import datetime

class MachineDataProcessor:
    def __init__(self, window_size=5, interval=10, data_file="data.json"):
        self.window_size = window_size
        self.interval = interval
        self.data_file = data_file
        self.data_queue = {
            "temperature": deque(maxlen=self.window_size),
            "speed": deque(maxlen=self.window_size),
        }
        self.status = "RUNNING"

    def read_machine_data(self):
        """Read machine data from a JSON file"""
        try:
            with open(self.data_file, "r") as file:
                data = json.load(file)
                return {
                    "timestamp": datetime.now().isoformat(),
                    "temperature": data.get("temperature"),
                    "speed": data.get("speed"),
                    "status": data.get("status", "UNKNOWN")
                }
        except FileNotFoundError:
            print(f"Error: File '{self.data_file}' not found.")
            return None
        except json.JSONDecodeError:
            print(f"Error: Failed to decode JSON from '{self.data_file}'.")
            return None

    def calculate_moving_averages(self):
        """Calculate moving averages for all numeric parameters"""
        averages = {
            key: round(sum(values) / len(values), 2) if values else None
            for key, values in self.data_queue.items()
        }
        return averages

    def process_data(self):
        """Process data from the JSON file and calculate moving averages"""
        new_data = self.read_machine_data()
        if not new_data:
            return None

        # Update the deque with new readings
        for key in self.data_queue:
            if new_data[key] is not None:
                self.data_queue[key].append(new_data[key])

        # Calculate moving averages
        moving_averages = self.calculate_moving_averages()

        # Combine data and averages
        transformed_data = {
            "timestamp": new_data["timestamp"],
            "moving_averages": moving_averages,
            "status": new_data["status"]
        }

        return transformed_data

    def run(self):
        """Continuously process data at the specified interval"""
        iteration = 1
        try:
            while True:
                print(f"\nReading #{iteration} at {datetime.now().strftime('%H:%M:%S')}")
                result = self.process_data()
                if result:
                    print(json.dumps(result, indent=2))
                print("Waiting for next reading...")
                time.sleep(self.interval)
                iteration += 1
        except KeyboardInterrupt:
            print("\nStopping data processing...")

if __name__ == "__main__":
    # Configure the processor
    window_size = int(input("Enter moving average window size (default 5): ") or 5)
    interval = int(input("Enter data fetching interval in seconds (default 10): ") or 10)
    data_file = input("Enter the path to the data file (default 'data.json'): ") or "data.json"
    processor = MachineDataProcessor(window_size=window_size, interval=interval, data_file=data_file)
    processor.run()
