from pymongo import MongoClient
import os
import hashlib
import json

client = MongoClient(os.getenv("MONGO_URI"))
database = client["automap"]
users = database["Users"]
skills = database["Skills"]
roadmaps = database["Roadmaps"]


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

initialize_roadmaps()