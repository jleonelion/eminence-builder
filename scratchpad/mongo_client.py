from pymongo import MongoClient
from bson.objectid import ObjectId
from dataclasses import dataclass, asdict
from typing import Optional
import datetime

# Define the dataclass
@dataclass
class User:
    name: str
    age: int
    email: str
    birthday: datetime = None
    _id: Optional[ObjectId] = None

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["mydatabase"]
collection = db["users"]

# Create a new document
def create_document(user: User):
    user_dict = asdict(user)
    if user_dict["_id"] is None:
        del user_dict["_id"]
    result = collection.insert_one(user_dict)
    print(f"Document created with id: {result.inserted_id}")

# Read documents
def read_documents():
    documents = collection.find()
    for doc in documents:
        print(User(**doc))

# Update a document
def update_document(document_id: str, update_data: dict):
    result = collection.update_one({"_id": ObjectId(document_id)}, {"$set": update_data})
    print(f"Matched {result.matched_count} document(s) and modified {result.modified_count} document(s)")

# Delete a document
def delete_document(document_id: str):
    result = collection.delete_one({"_id": ObjectId(document_id)})
    print(f"Deleted {result.deleted_count} document(s)")

def find_document_by_birthdate(birthdate: datetime):
    documents = collection.find({"birthday": birthdate})
    for doc in documents:
        print(User(**doc))

if __name__ == "__main__":
    # Example usage
    new_user = User(name="John Doe", age=30, email="john.doe@example.com", birthday=datetime.datetime(2000, 6, 26))
    # create_document(new_user)

    print("Documents in collection:")
    read_documents()

    print("Finding documents where name contains 'John' and birthday month is July:")
    documents = collection.find({
        "$expr": {
            "$eq": [
                { "$month": "$birthday" },
                6
            ]
        }
    })

    for doc in documents:
        print(User(**doc))
    # Replace with a valid document ID to test update and delete operations
    # document_id = "your_document_id_here"
    # update_data = {"age": 31}
    # update_document(document_id, update_data)

    # delete_document(document_id)