from fastapi import FastAPI, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from mongo import create_account, add_skills, skill_from_id, skill_search

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
    if success:
        return {"message": "Account created successfully"}
    else:
        raise HTTPException(status_code=400, detail="Failed to create account")


@app.get("/search")
def search_endpoint(q: str = ""):
    return skill_search(q)
