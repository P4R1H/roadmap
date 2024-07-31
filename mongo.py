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
            "roadmap": generate_roadmap()
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
    users.update_one(
        {"username": username},
        {"$set": {"skills": updated_skills}}
    )

    update_user_roadmap(username, updated_skills)
    print(f"Skills updated for {username}")

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

def generate_roadmap():
    return [
        {"step": "Learn a language", "skills": ["Programming Language"], "completed": False},
        {"step": "Solve leetcode easy", "skills": ["Problem Solving"], "completed": False},
        {"step": "Build an easy project", "skills": ["Project Development"], "completed": False},
        {"step": "Learn about common datastructures", "skills": ["Data Structures"], "completed": False},
        {"step": "Leetcode easys + mediums", "skills": ["Problem Solving"], "completed": False},
        {"step": "Give your first codechef contest", "skills": ["Competitive Programming"], "completed": False},
        {"step": "Choose a domain (webdev, AI/ML, app dev)", "skills": ["Domain Knowledge"], "completed": False},
        {"step": "Create projects in your chosen domain", "skills": ["Project Development"], "completed": False},
        {"step": "Learn common devops tools", "skills": ["DevOps"], "completed": False},
        {"step": "Start applying for internships", "skills": ["Networking", "Interview Preparation"], "completed": False},
        {"step": "Participate in hackathons", "skills": ["Hackathons"], "completed": False},
        {"step": "Contribute to open source", "skills": ["Open Source"], "completed": False},
        {"step": "Learn complex DSA concepts", "skills": ["Advanced DSA"], "completed": False},
        {"step": "Attend Microsoft webinars", "skills": ["Networking"], "completed": False},
        {"step": "Strengthen core OOPS concepts", "skills": ["OOPS"], "completed": False},
        {"step": "Strengthen core DBMS", "skills": ["DBMS"], "completed": False},
        {"step": "Strengthen core OS/COA/System design", "skills": ["OS", "COA", "System Design"], "completed": False},
        {"step": "Practice with mock interviews", "skills": ["Interview Preparation"], "completed": False},
        {"step": "Give interview!", "skills": ["Interview Preparation"], "completed": False},
    ]

def update_user_roadmap(username, updated_skills):
    user = users.find_one({"username": username})
    if not user:
        print(f"User {username} not found")
        return

    roadmap = user.get("roadmap", generate_roadmap())
    for step in roadmap:
        if not step["completed"]:
            if all(skill in updated_skills for skill in step["skills"]):
                step["completed"] = True
    
    users.update_one({"username": username}, {"$set": {"roadmap": roadmap}})

def get_user_roadmap(username):
    user = users.find_one({"username": username})
    if user:
        updated_skills = user.get("skills", [])
        update_user_roadmap(username, updated_skills)  # Ensure the roadmap is updated before returning
        return user["roadmap"]
    return generate_roadmap()
