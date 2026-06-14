from pathlib import Path

import torch
import torch.nn as nn
from PIL import Image
from torchvision import models, transforms

from app.config import ITEM_MODEL_PATH, ATTRIBUTE_MODEL_PATH


def season_to_weather_group(season: str) -> str:
    if season == "summer":
        return "hot"
    elif season == "winter":
        return "cold"
    elif season in ["spring", "fall"]:
        return "all_season"
    return "unknown"


class ItemClassifier:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = None
        self.class_names = ["bottoms", "shoes", "tops"]

        self.transform = transforms.Compose([
            transforms.Resize((256, 256)),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            ),
        ])

        self._load_model()

    def _build_model(self):
        model = models.resnet50(weights=None)
        num_features = model.fc.in_features

        model.fc = nn.Sequential(
            nn.Dropout(0.3),
            nn.Linear(num_features, 256),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(256, len(self.class_names))
        )

        return model

    def _load_model(self):
        path = Path(ITEM_MODEL_PATH)

        if not path.exists():
            print(f"WARNING: Item model not found at {path}")
            return

        checkpoint = torch.load(path, map_location=self.device)

        if isinstance(checkpoint, dict):
            self.class_names = checkpoint.get("class_names", self.class_names)
            state_dict = checkpoint.get("model_state_dict", checkpoint)
        else:
            raise ValueError("Item model checkpoint format is not supported.")

        self.model = self._build_model()
        self.model.load_state_dict(state_dict, strict=True)
        self.model.to(self.device)
        self.model.eval()

        print("Item model loaded:", self.class_names)

    def predict(self, image_path: str):
        if self.model is None:
            return {
                "item_type": "unknown",
                "confidence": 0.0,
                "all_probabilities": {}
            }

        image = Image.open(image_path).convert("RGB")
        tensor = self.transform(image).unsqueeze(0).to(self.device)

        with torch.no_grad():
            outputs = self.model(tensor)
            probabilities = torch.softmax(outputs, dim=1)[0]

        confidence, predicted_idx = torch.max(probabilities, dim=0)
        predicted_idx = int(predicted_idx.item())

        all_probabilities = {
            self.class_names[i]: float(probabilities[i].item())
            for i in range(len(self.class_names))
        }

        return {
            "item_type": self.class_names[predicted_idx],
            "confidence": float(confidence.item()),
            "all_probabilities": all_probabilities
        }


class AttributeClassifier:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = None

        self.gender_classes = ["men", "women", "unisex"]
        self.season_classes = ["spring", "summer", "fall", "winter"]

        self.transform = transforms.Compose([
            transforms.Resize((256, 256)),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            ),
        ])

        self._load_model()

    def _build_model(self):
        model = models.resnet50(weights=None)
        num_features = model.fc.in_features
        model.fc = nn.Identity()

        class AttributeClassifierResNet50(nn.Module):
            def __init__(self, backbone, num_features, num_gender_classes, num_season_classes):
                super().__init__()

                self.backbone = backbone

                self.shared = nn.Sequential(
                    nn.Linear(num_features, 512),
                    nn.ReLU(),
                    nn.Dropout(0.3)
                )

                self.gender_head = nn.Linear(512, num_gender_classes)
                self.season_head = nn.Linear(512, num_season_classes)

            def forward(self, x):
                features = self.backbone(x)
                features = self.shared(features)

                gender_logits = self.gender_head(features)
                season_logits = self.season_head(features)

                return gender_logits, season_logits

        return AttributeClassifierResNet50(
            backbone=model,
            num_features=num_features,
            num_gender_classes=len(self.gender_classes),
            num_season_classes=len(self.season_classes)
        )

    def _load_model(self):
        path = Path(ATTRIBUTE_MODEL_PATH)

        if not path.exists():
            print(f"WARNING: Attribute model not found at {path}")
            return

        checkpoint = torch.load(path, map_location=self.device)

        if isinstance(checkpoint, dict):
            self.gender_classes = checkpoint.get("gender_classes", self.gender_classes)
            self.season_classes = checkpoint.get("season_classes", self.season_classes)
            state_dict = checkpoint.get("model_state_dict", checkpoint)
        else:
            raise ValueError("Attribute model checkpoint format is not supported.")

        self.model = self._build_model()
        self.model.load_state_dict(state_dict, strict=True)
        self.model.to(self.device)
        self.model.eval()

        print("Attribute model loaded:")
        print("Gender classes:", self.gender_classes)
        print("Season classes:", self.season_classes)

    def predict(self, image_path: str):
        if self.model is None:
            return {
                "gender": "unknown",
                "gender_confidence": 0.0,
                "season": "unknown",
                "season_confidence": 0.0,
                "weather_group": "unknown",
                "gender_probabilities": {},
                "season_probabilities": {}
            }

        image = Image.open(image_path).convert("RGB")
        tensor = self.transform(image).unsqueeze(0).to(self.device)

        with torch.no_grad():
            gender_logits, season_logits = self.model(tensor)

            gender_probs = torch.softmax(gender_logits, dim=1)[0]
            season_probs = torch.softmax(season_logits, dim=1)[0]

        gender_confidence, gender_idx = torch.max(gender_probs, dim=0)
        season_confidence, season_idx = torch.max(season_probs, dim=0)

        gender_idx = int(gender_idx.item())
        season_idx = int(season_idx.item())

        gender_result = self.gender_classes[gender_idx]
        season_result = self.season_classes[season_idx]

        gender_probabilities = {
            self.gender_classes[i]: float(gender_probs[i].item())
            for i in range(len(self.gender_classes))
        }

        season_probabilities = {
            self.season_classes[i]: float(season_probs[i].item())
            for i in range(len(self.season_classes))
        }

        return {
            "gender": gender_result,
            "gender_confidence": float(gender_confidence.item()),
            "season": season_result,
            "season_confidence": float(season_confidence.item()),
            "weather_group": season_to_weather_group(season_result),
            "gender_probabilities": gender_probabilities,
            "season_probabilities": season_probabilities
        }


item_classifier = ItemClassifier()
attribute_classifier = AttributeClassifier()