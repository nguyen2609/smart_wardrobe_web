from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from bson import ObjectId
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from app.auth import get_current_user
from app.config import UPLOAD_DIR
from app.database import items_collection
from app.model_service import item_classifier, attribute_classifier

router = APIRouter(prefix="/items", tags=["Wardrobe Items"])

ALLOWED_CATEGORIES = {"tops", "bottoms", "shoes"}

CATEGORY_VI = {
    "tops": "Áo",
    "bottoms": "Quần",
    "shoes": "Giày",
}

GENDER_VI = {
    "men": "Nam",
    "women": "Nữ",
    "unisex": "Unisex",
    "unknown": "Không rõ",
}

SEASON_VI = {
    "spring": "Xuân",
    "summer": "Hè",
    "fall": "Thu",
    "winter": "Đông",
    "unknown": "Không rõ",
}

WEATHER_GROUP_VI = {
    "hot": "Thời tiết nóng",
    "cold": "Thời tiết lạnh",
    "all_season": "Dùng quanh năm",
    "unknown": "Không rõ",
}


@router.post("")
async def upload_item(
    name: str = Form(""),
    image: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
):
    if not image.content_type or not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files are allowed")

    upload_dir = Path(UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)

    extension = Path(image.filename or "item.jpg").suffix.lower() or ".jpg"
    filename = f"{current_user['id']}_{uuid4().hex}{extension}"
    file_path = upload_dir / filename

    content = await image.read()
    file_path.write_bytes(content)

    item_prediction = item_classifier.predict(str(file_path))
    attribute_prediction = attribute_classifier.predict(str(file_path))

    category = item_prediction["item_type"]

    if category not in ALLOWED_CATEGORIES:
        category = "tops"

    gender = attribute_prediction["gender"]
    season = attribute_prediction["season"]
    weather_group = attribute_prediction["weather_group"]

    doc = {
        "user_id": current_user["id"],

        "category": category,
        "category_name": CATEGORY_VI.get(category, category),

        "name": name.strip() or None,
        "image_url": f"/uploads/{filename}",

        "item_type": category,
        "item_confidence": item_prediction["confidence"],
        "item_probabilities": item_prediction["all_probabilities"],

        "gender": gender,
        "gender_name": GENDER_VI.get(gender, gender),
        "gender_confidence": attribute_prediction["gender_confidence"],
        "gender_probabilities": attribute_prediction["gender_probabilities"],

        "season": season,
        "season_name": SEASON_VI.get(season, season),
        "season_confidence": attribute_prediction["season_confidence"],
        "season_probabilities": attribute_prediction["season_probabilities"],

        "weather_group": weather_group,
        "weather_group_name": WEATHER_GROUP_VI.get(weather_group, weather_group),

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
    result = await items_collection.delete_one({
        "_id": ObjectId(item_id),
        "user_id": current_user["id"]
    })

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Item not found")

    return {"message": "Item deleted"}