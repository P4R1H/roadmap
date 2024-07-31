from fastapi import FastAPI, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from mongo import create_account, add_skills, skill_from_id, skill_search, get_skills, get_user_roadmap

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
    username: str = Form(...), password: str = Form(...), skills: str = Form("")
):
    skills_list = skills.split(",") if skills else []
    success = create_account(username, password, skills_list)
    if success != -1:
        roadmap = get_user_roadmap(username)
        return {"message": "Account created successfully", "roadmap": roadmap}
    else:
        raise HTTPException(status_code=400, detail="Failed to create account")

@app.get("/get_skills")
def get_skills_endpoint(username: str):
    return get_skills(username)

@app.get("/search")
def search_endpoint(q: str = ""):
    return skill_search(q)

@app.post("/add_skills")
def add_skills_endpoint(username: str = Form(...), skills: str = Form(...)):
    skills_list = skills.split(",")
    add_skills(username, skills_list)
    updated_skills = get_skills(username)
    roadmap = get_user_roadmap(username)
    return {"message": "Skills added successfully", "skills": updated_skills, "roadmap": roadmap}

@app.get("/roadmap")
def roadmap_endpoint(username: str):
    roadmap = get_user_roadmap(username)
    return {"username": username, "roadmap": roadmap}
