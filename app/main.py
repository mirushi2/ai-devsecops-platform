# DevSecOps CI/CD automation test 1
from fastapi import FastAPI

app = FastAPI(
    title="AI DevSecOps Platform",
    version="1.0.0"
)


@app.get("/")
def home():
    return {
        "message": "AI DevSecOps Platform is running",
        "status": "success"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.get("/users/{user_id}")
def get_user(user_id: int):
    return {
        "user_id": user_id,
        "name": f"User-{user_id}"
    }