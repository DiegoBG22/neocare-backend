from database import Base, engine
import models

models.Base.metadata.create_all(bind=engine)

from fastapi import FastAPI
from auth_router import router as auth_router

app = FastAPI()

app.include_router(auth_router)

@app.get("/health")
async def health_check():
    return {"status": "OK", "service": "FastAPI Backend"}
