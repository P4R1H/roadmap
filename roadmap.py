from typing import List, Dict, Any

def generate_roadmap(roadmap: List[Dict[str, Any]], user_skills: List[str]) -> List[Dict[str, Any]]:
    updated_roadmap = []

    for step in roadmap:
        skills_needed = set(step.get("skills_needed", []))
        user_skills_set = set(user_skills)
        if skills_needed.issubset(user_skills_set):
            step["status"] = "completed"
        else:
            step["status"] = "to-do"
        
        updated_roadmap.append(step)
    
    return updated_roadmap
