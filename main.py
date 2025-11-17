import os
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import db, create_document, get_documents
from schemas import Product, Variant

app = FastAPI(title="Ultra Premium Commerce API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "Ultra Premium Commerce API running"}


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": [],
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name if hasattr(db, "name") else "Unknown"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:80]}"
        else:
            response["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:80]}"

    return response


@app.get("/schema")
def get_schema():
    # Expose minimal schema information for viewers/tools
    models: Dict[str, Any] = {}
    models["product"] = Product.model_json_schema()
    return {"models": models}


# -------- Products Endpoints --------
class ProductCreate(Product):
    pass


def product_collection():
    return "product"


@app.get("/api/products", response_model=List[Dict[str, Any]])
def list_products(limit: Optional[int] = 20):
    docs = get_documents(product_collection(), {}, limit=limit)
    # Normalize ObjectId to string
    for d in docs:
        if "_id" in d:
            d["id"] = str(d.pop("_id"))
    return docs


@app.get("/api/products/{slug}", response_model=Dict[str, Any])
def get_product(slug: str):
    doc = db[product_collection()].find_one({"slug": slug})
    if not doc:
        raise HTTPException(status_code=404, detail="Product not found")
    doc["id"] = str(doc.pop("_id"))
    return doc


@app.post("/api/products", response_model=Dict[str, str])
def create_product(payload: ProductCreate):
    # Ensure unique slug
    exists = db[product_collection()].find_one({"slug": payload.slug})
    if exists:
        raise HTTPException(status_code=400, detail="Slug already exists")
    new_id = create_document(product_collection(), payload)
    return {"id": new_id}


@app.post("/seed")
def seed_demo_products():
    count = db[product_collection()].count_documents({}) if db else 0
    if count > 0:
        return {"status": "ok", "message": "Products already present"}

    demo: List[Product] = [
        Product(
            title="Specter Series X1",
            slug="specter-series-x1",
            description="Monolithic precision. Forged for power.",
            price=1299,
            compare_at_price=1499,
            category="hardware",
            images=[
                "https://images.unsplash.com/photo-1527443154391-507e9dc6c5cc?q=80&w=1600&auto=format&fit=crop",
                "https://images.unsplash.com/photo-1542751371-adc38448a05e?q=80&w=1600&auto=format&fit=crop",
            ],
            model_url="https://prod.spline.design/8J9sS3L8q1sV9t8A/scene.splinecode",
            variants=[
                Variant(name="Finish", options=["Obsidian Black", "Liquid Silver"]),
                Variant(name="Capacity", options=["256GB", "512GB", "1TB"]),
            ],
            badges=["2-Year Warranty", "Free Express Shipping", "30-Day Returns"],
            rating=4.9,
            review_count=312,
            in_stock=True,
            specs={"CPU": "NeonCore M3", "GPU": "RayFlux 8G", "Weight": "1.2kg"},
        ),
        Product(
            title="Nebula Pro V",
            slug="nebula-pro-v",
            description="Zero compromise. Ultra light.",
            price=999,
            compare_at_price=1199,
            category="hardware",
            images=[
                "https://images.unsplash.com/photo-1555617981-dac3880d511d?q=80&w=1600&auto=format&fit=crop",
                "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?q=80&w=1600&auto=format&fit=crop",
            ],
            model_url="https://prod.spline.design/G8j2l6m1y7X2m6xD/scene.splinecode",
            variants=[
                Variant(name="Finish", options=["Chrome", "Graphite"]),
                Variant(name="Capacity", options=["128GB", "256GB", "512GB"]),
            ],
            badges=["Premium Support", "Insured Delivery"],
            rating=4.8,
            review_count=198,
            in_stock=True,
            specs={"CPU": "IonDrive X", "Display": "120Hz OLED", "Weight": "0.98kg"},
        ),
    ]

    for p in demo:
        create_document(product_collection(), p)

    return {"status": "ok", "message": "Seeded demo products"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
