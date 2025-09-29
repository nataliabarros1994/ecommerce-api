from fastapi import FastAPI
from .database import engine
from .models import Base
from .routers.products import router as products_router

app = FastAPI(title="Product Service", version=1.0)

Base.metadata.create_all(bind=engine)  # Feitiço: prateleiras nascem na loja também!

app.include_router(products_router)  # Liga a rota mágica para listar produtos do banco

@app.get("/health")
def health():
    return {"status": "Product service OK!"}