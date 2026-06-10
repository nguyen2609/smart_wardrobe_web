from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from bson import ObjectId
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from app.auth import get_current_user
from app.config import UPLOAD_DIR
from app.database import items_collection
from app.model_service import classifier

router = APIRouter(prefix="/items", tags=["Wardrobe Items"])

ALLOWED_CATEGORIES = {"tops", "bottoms", "shoes", "accessories"}
CATEGORY_VI = {
    "tops": "Áo",
    "bottoms": "Quần",
    "shoes": "Giày",
    "accessories": "Phụ kiện",
}

@router.post("")
async def upload_item(
    category: str = Form(...),
    name: str = Form(""),
    image: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
):
    if category not in ALLOWED_CATEGORIES:
        raise HTTPException(status_code=400, detail="Invalid wardrobe category")

    if not image.content_type or not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files are allowed")

    upload_dir = Path(UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)

    extension = Path(image.filename or "item.jpg").suffix.lower() or ".jpg"
    filename = f"{current_user['id']}_{uuid4().hex}{extension}"
    file_path = upload_dir / filename

    content = await image.read()
    file_path.write_bytes(content)

    ai_label, ai_confidence = classifier.predict(str(file_path))

    doc = {
        "user_id": current_user["id"],
        "category": category,
        "category_name": CATEGORY_VI[category],
        "name": name.strip() or None,
        "image_url": f"/uploads/{filename}",
        "ai_label": ai_label,
        "ai_confidence": ai_confidence,
        "created_at": datetime.now(timezone.utc),
    }
    result = await items_collection.insert_one(doc)
    doc["id"] = str(result.inserted_id)
    doc.pop("_id", None)
    return doc

@router.get("")
async def get_my_items(current_user: dict = Depends(get_current_user)):
    cursor = items_collection.find({"user_id": current_user["id"]}).sort("created_at", -1)
    items = []
    async for doc in cursor:
        doc["id"] = str(doc["_id"])
        doc.pop("_id", None)
        items.append(doc)
    return items

@router.delete("/{item_id}")
async def delete_item(item_id: str, current_user: dict = Depends(get_current_user)):
    result = await items_collection.delete_one({"_id": ObjectId(item_id), "user_id": current_user["id"]})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"message": "Item deleted"}
