from pymongo import MongoClient   #Warehouse Manager.

client = MongoClient("mongodb://localhost:27017/")
db = client["ai_recruitment"]

def save_candidate(data):
    db.candidates.insert_one(data)

def get_all():
    return list(db.candidates.find({}, {"_id": 0}))
