"""Seed Firestore with initial camera data for Sentinel Bridge."""
from google.cloud import firestore

db = firestore.Client(project="sentinel-ggl-aipw")

CAMERAS = [
    {
        "id": "CAM-001",
        "name": "CAM-001",
        "location": "405 N. BROADWAY ST, METRO CENTRAL",
        "status": "LIVE",
        "zone": "ZONE_ALPHA",
        "lat": 34.0522,
        "lng": -118.2437,
    },
    {
        "id": "CAM-002",
        "name": "CAM-002",
        "location": "INTERSECTION 5TH & MAIN",
        "status": "ALERT",
        "zone": "ZONE_BRAVO",
        "lat": 34.0486,
        "lng": -118.2488,
    },
    {
        "id": "CAM-003",
        "name": "CAM-003",
        "location": "METRO PARK SOUTH ENTRANCE",
        "status": "LIVE",
        "zone": "ZONE_ALPHA",
        "lat": 34.0511,
        "lng": -118.2553,
    },
    {
        "id": "CAM-004",
        "name": "CAM-004",
        "location": "822 HARBOR VIEW DRIVE",
        "status": "OFFLINE",
        "zone": "ZONE_CHARLIE",
        "lat": 33.7361,
        "lng": -118.2922,
    },
    {
        "id": "CAM-005",
        "name": "CAM-005",
        "location": "INDUSTRIAL LOOP SECTOR 7",
        "status": "STANDBY",
        "zone": "ZONE_GAMMA",
        "lat": 34.0195,
        "lng": -118.4912,
    },
    {
        "id": "CAM-006",
        "name": "CAM-006",
        "location": "HIGHWAY 101 OVERPASS",
        "status": "LIVE",
        "zone": "ZONE_DELTA",
        "lat": 34.1023,
        "lng": -118.3262,
    },
]


def seed():
    batch = db.batch()
    for cam in CAMERAS:
        ref = db.collection("cameras").document(cam["id"])
        batch.set(ref, cam)
    batch.commit()
    print(f"Seeded {len(CAMERAS)} cameras into sentinel-ggl-aipw/cameras")


if __name__ == "__main__":
    seed()
