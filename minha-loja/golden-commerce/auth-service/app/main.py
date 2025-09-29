from fastapi import FastAPI
from .database import engine
from .models import Base

app = FastAPI(title="Auth Service", version=1.0)

Base.metadata.create_all(bind=engine)  # Prateleiras nascem!

@app.get("/health")
def health():
    return {"status": "Auth service OK!"}

# Se tem routers/auth.py, inclua: from .routers.auth import router as auth_router
# app.include_router(auth_router, prefix="/api")