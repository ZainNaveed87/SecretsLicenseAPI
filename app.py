from fastapi import FastAPI
from routes import license_routes

app = FastAPI()

app.include_router(license_routes.router)
