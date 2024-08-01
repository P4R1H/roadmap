from fastapi import FastAPI, Form, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from mongo import create_account, add_skills, delete_skills, skill_search, get_skills, get_user_roadmap, update_user_roadmap, create_account_from_email, get_desired_role

origins = [
    "*",
]

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/create_account")
def create_account_endpoint(
    username: str = Form(...),
    password: str = Form(...),
    skills: str = Form(""),
    desired_role: str = Form("SWE @ Microsoft")
):
    skills_list = skills.split(",") if skills else []
    success = create_account(username, password, skills_list, desired_role)
    if success != -1:
        roadmap = get_user_roadmap(username)
        return {"message": "Account created successfully", "roadmap": roadmap}
    else:
        raise HTTPException(status_code=400, detail="Failed to create account")

@app.post("/create_account_from_email")
def create_account_from_email_endpoint(email: str = Form(...)):
    success = create_account_from_email(email)
    if success == -1:
        return {"message": "Account already exists or failed to create"}
    roadmap = get_user_roadmap(email)
    return {"message": "Account created successfully", "roadmap": roadmap}

@app.get("/get_skills")
def get_skills_endpoint(username: str):
    return get_skills(username)

@app.get("/search")
def search_endpoint(q: str = ""):
    return skill_search(q)

@app.get("/get_desired_role")
def get_desired_role_endpoint(username: str):
    role = get_desired_role(username)
    roadmap = get_user_roadmap(username)
    if role:
        return {"username": username, "desired_role": role, "roadmap" : roadmap}
    else:
        raise HTTPException(status_code=404, detail="User or desired role not found")


@app.post("/add_skills")
def add_skills_endpoint(username: str = Form(...), skills: str = Form(...)):
    skills_list = [skill.strip() for skill in skills.split(",") if skill.strip()]
    if not skills_list:
        raise HTTPException(status_code=400, detail="No valid skills provided")
    success = add_skills(username, skills_list)
    if success != -1:
        updated_skills = get_skills(username)
        roadmap = get_user_roadmap(username)
        return {"message": "Skills added successfully", "skills": updated_skills, "roadmap": roadmap}
    else:
        raise HTTPException(status_code=400, detail="Failed to add skills")

@app.post("/delete_skills")
def delete_skills_endpoint(username: str = Form(...), skills: str = Form(...)):
    skills_list = [skill.strip() for skill in skills.split(",") if skill.strip()]
    if not skills_list:
        raise HTTPException(status_code=400, detail="No valid skills provided")
    success = delete_skills(username, skills_list)
    if success != -1:
        updated_skills = get_skills(username)
        roadmap = get_user_roadmap(username)
        return {"message": "Skills deleted successfully", "skills": updated_skills, "roadmap": roadmap}
    else:
        raise HTTPException(status_code=400, detail="Failed to delete skills")

@app.get("/roadmap")
def roadmap_endpoint(username: str):
    roadmap = get_user_roadmap(username)
    if roadmap:
        return {"username": username, "roadmap": roadmap}
    else:
        raise HTTPException(status_code=404, detail="User or roadmap not found")

@app.post("/update_roadmap")
def update_roadmap_endpoint(username: str = Form(...)):
    update_user_roadmap(username)
    roadmap = get_user_roadmap(username)
    if roadmap:
        return {"message": "Roadmap updated successfully", "roadmap": roadmap}
    else:
        raise HTTPException(status_code=404, detail="User or roadmap not found")
