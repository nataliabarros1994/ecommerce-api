"""Product Service - FastAPI Application"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import products
from app.core.database import init_db
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Product Service",
    description="Product Catalog Service with MongoDB",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    await init_db()

app.include_router(products.router, prefix="/api/products", tags=["products"])


@app.get("/")
async def root():
    return {"service": "Product Service", "status": "running"}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "product-service"}
