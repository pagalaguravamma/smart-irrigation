from flask import Flask, request, jsonify
from datetime import datetime
from collections import deque
from flask_cors import CORS  # Import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
app.config['JSON_SORT_KEYS'] = False

# Configuration storage
crop_config = {
    1: {"name": "Tomato", "min_threshold": 30, "max_threshold": 60, "automatic_mode": True, "manual_duration": 0, "relay_status": "OFF"},
    2: {"name": "Lettuce", "min_threshold": 40, "max_threshold": 70, "automatic_mode": True, "manual_duration": 0, "relay_status": "OFF"},
    3: {"name": "Pepper", "min_threshold": 35, "max_threshold": 65, "automatic_mode": True, "manual_duration": 0, "relay_status": "OFF"},
    4: {"name": "Strawberry", "min_threshold": 25, "max_threshold": 55, "automatic_mode": True, "manual_duration": 0, "relay_status": "OFF"}
}

# Data storage (last 10 readings)
sensor_data = deque(maxlen=10)

@app.route('/update_crop', methods=['POST'])
def update_crop():
    data = request.json
    if not data or "crop_number" not in data:
        return jsonify({"status": "error", "message": "Missing crop_number"}), 400

    crop_num = data["crop_number"]
    if crop_num not in crop_config:
        return jsonify({"status": "error", "message": "Invalid crop number"}), 400

    # Update only provided fields
    for field in data:
        if field in crop_config[crop_num] and field != "crop_number":
            crop_config[crop_num][field] = data[field]

    return jsonify({
        "status": "success",
        "message": f"Crop {crop_num} updated",
        "config": crop_config[crop_num]
    })

@app.route('/reset_all', methods=['POST'])
def reset_all():
    global crop_config
    crop_config = {
        1: {"name": "Tomato", "min_threshold": 30, "max_threshold": 60, "automatic_mode": True, "manual_duration": 0, "relay_status": "OFF"},
        2: {"name": "Lettuce", "min_threshold": 40, "max_threshold": 70, "automatic_mode": True, "manual_duration": 0, "relay_status": "OFF"},
        3: {"name": "Pepper", "min_threshold": 35, "max_threshold": 65, "automatic_mode": True, "manual_duration": 0, "relay_status": "OFF"},
        4: {"name": "Strawberry", "min_threshold": 25, "max_threshold": 55, "automatic_mode": True, "manual_duration": 0, "relay_status": "OFF"}
    }
    return jsonify({"status": "success", "message": "All crops reset to defaults"})

@app.route('/get_config', methods=['GET'])
def get_config():
    crop_num = request.args.get('crop', type=int)
    if crop_num and crop_num in crop_config:
        return jsonify(crop_config[crop_num])
    return jsonify({k: v for k, v in crop_config.items()})

@app.route('/receive_data', methods=['POST'])
def receive_data():
    data = request.json
    if not data:
        return jsonify({"status": "error", "message": "No data received"}), 400

    timestamp = datetime.now().isoformat()
    sensor_data.append({
        "timestamp": timestamp,
        "data": data,
        "config": {k: v for k, v in crop_config.items()}
    })
    return jsonify({"status": "success", "message": "Data stored"})

@app.route('/get_data', methods=['GET'])
def get_data():
    if not sensor_data:
        return jsonify({"status": "error", "message": "No data available"}), 404
    return jsonify(sensor_data[-1])

@app.route('/set_manual', methods=['POST'])
def set_manual():
    data = request.json
    if not data or "crop_number" not in data or "duration" not in data:
        return jsonify({"status": "error", "message": "Missing parameters"}), 400

    crop_num = data["crop_number"]
    if crop_num not in crop_config:
        return jsonify({"status": "error", "message": "Invalid crop number"}), 400

    crop_config[crop_num]["automatic_mode"] = False
    crop_config[crop_num]["manual_duration"] = data["duration"] * 60 * 1000  # Convert minutes to milliseconds
    crop_config[crop_num]["relay_status"] = "ON"  # Relay is turned ON in manual mode

    return jsonify({
        "status": "success",
        "message": f"Crop {crop_num} set to manual for {data['duration']} minutes",
        "config": crop_config[crop_num]
    })

if __name__ == '__main__':
    app.run(port=2041, debug=True)
