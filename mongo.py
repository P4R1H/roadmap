from pymongo import MongoClient
import os
import hashlib

client = MongoClient(f"")
database = client["automap"]
users = database["Users"]
skills = database["Skills"]

try:
    client.admin.command('ping')
    print("Successfully connected")
except Exception as e:
    print(f"Couldn't connect: {e}")

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_account(username, password, skills=None):
    if users.find_one({"username": username}):
        print("Username already exists")
        return -1

    password_hash = hash_password(password)

    result = users.insert_one( {
        "username": username,
        "password": password_hash,
        "skills": skills if skills else []
    })
    
    if result.acknowledged:
        print(f"Account created successfully for {username}")
    else:
        print("Failed to create account")


def skill_from_id(skill_id):
    return(skills.find_one({"_id": skill_id}))

def add_skills(username, skills):
    print("TEst")
    
def get_skills(user_id: str):
    user = skills.find_one({"_id": user_id})
    if user:
        return user.get("skills", [])
    return []

    
