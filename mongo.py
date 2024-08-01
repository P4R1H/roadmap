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
roadmaps = database["Roadmaps"]

try:
    client.admin.command("ping")
    print("Successfully connected")
except Exception as e:
    print(f"Couldn't connect: {e}")

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_account(username, password, skills=None, desired_role="SWE @ Microsoft"):
    if users.find_one({"username": username}):
        print("Username already exists")
        return -1

    password_hash = hash_password(password)

    result = users.insert_one(
        {
            "username": username,
            "password": password_hash,
            "skills": skills if skills else [],
            "desired_role": desired_role,
            "roadmap": []
        }
    )

    if result.acknowledged:
        print(f"Account created successfully for {username}")
        update_user_roadmap(username)
        return 1
    else:
        print("Failed to create account")
        return -1

def create_account_from_email(email):
    if users.find_one({"email": email}):
        print("Account already exists")
        return -1

    result = users.insert_one(
        {
            "email": email,
            "password": None,
            "skills": [],
            "desired_role": "SWE @ Microsoft",
            "roadmap": []
        }
    )

    if result.acknowledged:
        print(f"Account created successfully for {email}")
        update_user_roadmap(email)
        return 1
    else:
        print("Failed to create account")
        return -1

def delete_skills(username, skills_list):
    user = users.find_one({"username": username})
    if not user:
        print(f"User {username} not found")
        return -1

    updated_skills = [skill for skill in user.get("skills", []) if skill not in skills_list]
    users.update_one(
        {"username": username},
        {"$set": {"skills": updated_skills}}
    )

    update_user_roadmap(username)
    print(f"Skills deleted for {username}")
    return 1

def skill_from_id(skill_id):
    return skills.find_one({"_id": ObjectId(skill_id)})

def add_skills(username, new_skills):
    user = users.find_one({"username": username})
    if not user:
        print(f"User {username} not found")
        return -1

    updated_skills = list(set(user.get("skills", []) + new_skills))
    users.update_one(
        {"username": username},
        {"$set": {"skills": updated_skills}}
    )

    update_user_roadmap(username)
    print(f"Skills updated for {username}")
    return 1

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

def get_base_roadmap():
    return roadmaps.find_one({"type": "base"})["steps"]

def get_role_specific_roadmap(role):
    return roadmaps.find_one({"type": "role_specific", "role": role})["steps"]

def generate_user_roadmap(username, desired_role):
    user = users.find_one({"username": username})
    if not user:
        return None
    user_roadmap = user.get("roadmap", [])

    if not user_roadmap:
        base_roadmap = get_base_roadmap()
        role_specific_steps = get_role_specific_roadmap(desired_role)
        user_roadmap = base_roadmap + role_specific_steps
        
    user_skills = set(user.get("skills", []))

    for step in user_roadmap:
        step_skills = set(skill["name"] for skill in step["skills"])
        step["completed"] = step_skills.issubset(user_skills)

    return user_roadmap

def update_user_roadmap(username):
    user = users.find_one({"username": username})
    if not user:
        print(f"User {username} not found")
        return

    desired_role = user.get("desired_role", "SWE @ Microsoft") 
    updated_roadmap = generate_user_roadmap(username, desired_role)
    
    users.update_one({"username": username}, {"$set": {"roadmap": updated_roadmap}})

def get_user_roadmap(username):
    user = users.find_one({"username": username})
    if user:
        if "roadmap" not in user or not user["roadmap"]:
            update_user_roadmap(username)
        return user["roadmap"]
    return None
