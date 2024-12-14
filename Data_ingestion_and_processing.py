import time
import json
from collections import deque

# Simulate the data stream from a mocked endpoint or JSON file
def read_mock_data():
    # Replace this with actual data reading logic
    return {
        "timestamp": time.time(),
        "temperature": round(20 + (5 * (time.time() % 5)), 2),
        "speed": round(100 + (10 * (time.time() % 7)), 2),
        "status": "RUNNING"
    }

def calculate_moving_average(data_queue, new_data):
    for key in new_data:
        if key not in ["timestamp", "status"]:  # Exclude non-numeric keys
            if key not in data_queue:
                data_queue[key] = deque(maxlen=5)
            data_queue[key].append(new_data[key])
    
    # Calculate the moving average for each parameter
    averages = {
        key: round(sum(values) / len(values), 2) for key, values in data_queue.items()
    }
    return averages

def main():
    data_queue = {}

    try:
        while True:
            new_data = read_mock_data()
            moving_averages = calculate_moving_average(data_queue, new_data)

            # Combine new data with moving averages
            transformed_data = {
                "timestamp": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(new_data["timestamp"])),
                "moving_averages": moving_averages,
                "status": new_data["status"]
            }

            print(json.dumps(transformed_data, indent=2))

            time.sleep(10)  # Simulate 10-second intervals
    except KeyboardInterrupt:
        print("Program terminated.")
        
if __name__ == "__main__":
    main()
