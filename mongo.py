from pymongo import MongoClient
import os
import hashlib
from dotenv import load_dotenv
from bson import json_util, ObjectId
import json
load_dotenv()

client = MongoClient(os.getenv("MONGO_URI"))
database = client["automap"]
users = database["Users"]
skills = database["Skills"]

try:
    client.admin.command("ping")
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

    result = users.insert_one(
        {
            "username": username,
            "password": password_hash,
            "skills": skills if skills else [],
        }
    )

    if result.acknowledged:
        print(f"Account created successfully for {username}")
    else:
        print("Failed to create account")

def skill_from_id(skill_id):
    return skills.find_one({"_id": ObjectId(skill_id)})

def add_skills(username, new_skills):
    user = users.find_one({"username": username})
    if not user:
        print(f"User {username} not found")
        return -1

    updated_skills = list(set(user.get("skills", []) + new_skills))
    result = users.update_one(
        {"username": username},
        {"$set": {"skills": updated_skills}}
    )

    if result.modified_count > 0:
        print(f"Skills updated for {username}")
    else:
        print(f"Failed to update skills for {username}")

def get_skills(username: str):
    user = users.find_one({"username": username})
    if user:
        return user.get("skills", [])
    return []

def skill_search(q: str):
    res = skills.aggregate(
        [
            {
                "$search": {
                    "index": "Skill-search",
                    "text": {
                        "path": "Name",
                        "query": f"{q}",
                        "fuzzy": {
                            "maxEdits": 2,
                            "maxExpansions": 100,
                        },
                    },
                }
            }
        ]
    )
    
    return json.loads(json_util.dumps(res))

def roadmap_for_skills(username):
    user_skills = get_skills(username)
    recommended_skills = []  
    # Placeholder
    if "Python" not in user_skills:
        recommended_skills.append("Python")
    if "Machine Learning" not in user_skills:
        recommended_skills.append("Machine Learning")
    
    return recommended_skills

def update_roadmap(username, new_skills):
    # Temp
    existing_skills = get_skills(username)
    combined_skills = list(set(existing_skills + new_skills))
    users.update_one({"username": username}, {"$set": {"skills": combined_skills}})
    return roadmap_for_skills(username)
