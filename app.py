from fastapi import FastAPI
from routes import license_routes

app = FastAPI()

# ADD THIS ROUTE
@app.get("/")
def root():
    return {"message": "Secrets License API is Live."}

app.include_router(license_routes.router)
