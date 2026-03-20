from backend.db.firestore_client import db

cameras = [
  {"cam_id": "CAM-001", "lat": 17.3850, "lng": 78.4867, "address": "NH-44, Mehdipatnam, Hyderabad", "zone": "South", "status": "LIVE"},
  {"cam_id": "CAM-002", "lat": 17.4399, "lng": 78.4983, "address": "Begumpet Flyover, Hyderabad", "zone": "Central", "status": "ALERT"},
  {"cam_id": "CAM-003", "lat": 17.3616, "lng": 78.4747, "address": "Tolichowki Junction, Hyderabad", "zone": "West", "status": "LIVE"},
  {"cam_id": "CAM-004", "lat": 17.4156, "lng": 78.5312, "address": "LB Nagar Signal, Hyderabad", "zone": "East", "status": "OFFLINE"},
  {"cam_id": "CAM-005", "lat": 17.4947, "lng": 78.3996, "address": "Miyapur X Roads, Hyderabad", "zone": "North", "status": "LIVE"},
  {"cam_id": "CAM-006", "lat": 17.3724, "lng": 78.5478, "address": "Uppal Ring Road, Hyderabad", "zone": "East", "status": "LIVE"},
]

def seed():
    if not db:
        print("Firestore client not initialized.")
        return
    for cam in cameras:
        db.collection("cameras").document(cam["cam_id"]).set(cam)
    print("Seeded successfully.")

if __name__ == "__main__":
    seed()
