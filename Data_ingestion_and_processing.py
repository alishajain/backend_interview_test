import time
import json
from collections import deque
from datetime import datetime
import random

class MachineDataProcessor:
    def __init__(self, window_size=5, interval=10):
        self.window_size = window_size
        self.interval = interval
        self.data_queue = {
            "temperature": deque(maxlen=self.window_size),
            "speed": deque(maxlen=self.window_size),
        }
        self.status = "RUNNING"

    def simulate_machine_data(self):
        """Simulate reading data from a machine"""
        return {
            "timestamp": datetime.now().isoformat(),
            "temperature": round(random.uniform(60, 85), 2),
            "speed": round(random.uniform(1000, 1200), 2),
            "status": random.choice(["RUNNING", "STOPPED", "WARNING"])
        }

    def calculate_moving_averages(self):
        """Calculate moving averages for all numeric parameters"""
        averages = {
            key: round(sum(values) / len(values), 2) if values else None
            for key, values in self.data_queue.items()
        }
        return averages

    def process_data(self):
        """Simulate data processing with moving averages"""
        new_data = self.simulate_machine_data()

        # Update the deque with new readings
        for key in self.data_queue:
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
    processor = MachineDataProcessor(window_size=window_size, interval=interval)
    processor.run()
