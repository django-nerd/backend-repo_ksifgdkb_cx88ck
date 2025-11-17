"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Variant(BaseModel):
    name: str = Field(..., description="Variant name, e.g., Color or Size")
    options: List[str] = Field(default_factory=list, description="Available options")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    slug: str = Field(..., description="URL-friendly identifier")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    compare_at_price: Optional[float] = Field(None, ge=0, description="Original price for comparison")
    category: str = Field(..., description="Product category")
    images: List[str] = Field(default_factory=list, description="Image URLs")
    model_url: Optional[str] = Field(None, description="3D model or Spline scene URL")
    variants: List[Variant] = Field(default_factory=list, description="Variant groups")
    badges: List[str] = Field(default_factory=list, description="Trust or feature badges")
    rating: float = Field(default=5.0, ge=0, le=5, description="Average rating")
    review_count: int = Field(default=0, ge=0, description="Number of reviews")
    in_stock: bool = Field(True, description="Whether product is in stock")
    specs: Dict[str, str] = Field(default_factory=dict, description="Key-value specs")

# Add your own schemas here:
# --------------------------------------------------

# Note: The Flames database viewer will automatically:
# 1. Read these schemas from GET /schema endpoint
# 2. Use them for document validation when creating/editing
# 3. Handle all database operations (CRUD) directly
# 4. You don't need to create any database endpoints!
