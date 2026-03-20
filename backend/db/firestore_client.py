from google.cloud import firestore

try:
    db = firestore.Client()
except Exception as e:
    db = None
