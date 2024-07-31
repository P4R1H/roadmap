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
            "roadmap": []  # Empty roadmap, will be generated on first access
        }
    )

    if result.acknowledged:
        print(f"Account created successfully for {username}")
        update_user_roadmap(username)  # Generate initial roadmap
        return 1
    else:
        print("Failed to create account")
        return -1

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

    desired_role = user.get("desired_role", "SWE @ Microsoft")  # Default role if not set
    updated_roadmap = generate_user_roadmap(username, desired_role)
    
    users.update_one({"username": username}, {"$set": {"roadmap": updated_roadmap}})

def get_user_roadmap(username):
    user = users.find_one({"username": username})
    if user:
        if "roadmap" not in user or not user["roadmap"]:
            update_user_roadmap(username)
        return user["roadmap"]
    return None

# Initialize roadmaps in the database
def initialize_roadmaps():
    if roadmaps.count_documents({}) == 0:
        base_roadmap = {
            "type": "base",
            "steps": [
                {
                    "step": "Learn a programming language",
                    "skills": [{"name": "Programming Language", "level": "basic"}],
                },
                {
                    "step": "Solve leetcode easy problems",
                    "skills": [{"name": "Problem Solving", "level": "basic"}],
                },
                {
                    "step": "Build an easy project",
                    "skills": [{"name": "Project Development", "level": "basic"}],
                },
                {
                    "step": "Learn about common data structures",
                    "skills": [{"name": "Data Structures", "level": "basic"}],
                },
                {
                    "step": "Learn version control (Git)",
                    "skills": [{"name": "Version Control", "level": "basic"}],
                },
                {
                    "step": "Solve leetcode easy and medium problems",
                    "skills": [{"name": "Problem Solving", "level": "intermediate"}],
                },
                {
                    "step": "Participate in a coding contest",
                    "skills": [{"name": "Competitive Programming", "level": "basic"}],
                },
                {
                    "step": "Learn common DevOps tools",
                    "skills": [{"name": "DevOps", "level": "basic"}],
                },
                {
                    "step": "Participate in hackathons",
                    "skills": [{"name": "Hackathons", "level": "intermediate"}],
                },
                {
                    "step": "Contribute to open source projects",
                    "skills": [{"name": "Open Source", "level": "intermediate"}],
                },
                {
                    "step": "Learn advanced DSA concepts",
                    "skills": [{"name": "Advanced DSA", "level": "advanced"}],
                },
                {
                    "step": "Strengthen core OOP concepts",
                    "skills": [{"name": "OOPS", "level": "intermediate"}],
                },
                {
                    "step": "Strengthen core DBMS concepts",
                    "skills": [{"name": "DBMS", "level": "intermediate"}],
                },
                {
                    "step": "Learn OS, Computer Architecture, and System Design basics",
                    "skills": [
                        {"name": "OS", "level": "basic"},
                        {"name": "Computer Architecture", "level": "basic"},
                        {"name": "System Design", "level": "basic"}
                    ],
                },
                {
                    "step": "Practice with mock interviews",
                    "skills": [{"name": "Interview Preparation", "level": "intermediate"}],
                },
            ]
        }

        role_specific_roadmap = {
            "type": "role_specific",
            "role": "SWE @ Microsoft",
            "steps": [
                {
                    "step": "Learn C# and .NET framework",
                    "skills": [
                        {"name": "C#", "level": "intermediate"},
                        {"name": ".NET", "level": "intermediate"}
                    ],
                },
                {
                    "step": "Understand Microsoft Azure",
                    "skills": [{"name": "Azure", "level": "intermediate"}],
                },
                {
                    "step": "Practice advanced system design",
                    "skills": [{"name": "System Design", "level": "advanced"}],
                },
                {
                    "step": "Learn about Microsoft's development practices",
                    "skills": [{"name": "Microsoft Development Practices", "level": "intermediate"}],
                },
                {
                    "step": "Contribute to .NET open source projects",
                    "skills": [
                        {"name": "Open Source", "level": "advanced"},
                        {"name": ".NET", "level": "advanced"}
                    ],
                },
                {
                    "step": "Prepare for Microsoft-specific interview questions",
                    "skills": [{"name": "Microsoft Interview Preparation", "level": "advanced"}],
                },
            ]
        }

        roadmaps.insert_one(base_roadmap)
        roadmaps.insert_one(role_specific_roadmap)
        print("Roadmaps initialized in the database")
    else:
        print("Roadmaps already exist in the database")

# Call this function when the application starts
initialize_roadmaps()