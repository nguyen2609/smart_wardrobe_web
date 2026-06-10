from pathlib import Path
from typing import Tuple

import torch
import torch.nn as nn
from PIL import Image
from torchvision import models, transforms

from app.config import MODEL_PATH

LABELS = ["men_cold", "men_hot", "women_cold", "women_hot"]

class SmartWardrobeClassifier:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = None
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])
        self._load_model()

    def _build_resnet50(self):
        model = models.resnet50(weights=None)
        model.fc = nn.Linear(model.fc.in_features, len(LABELS))
        return model

    def _load_model(self):
        path = Path(MODEL_PATH)
        if not path.exists():
            print(f"WARNING: Model file not found at {path}. Classification will use fallback.")
            return

        checkpoint = torch.load(path, map_location=self.device)

        if isinstance(checkpoint, nn.Module):
            self.model = checkpoint
        elif isinstance(checkpoint, dict):
            state_dict = checkpoint.get("model_state_dict", checkpoint)
            self.model = self._build_resnet50()
            self.model.load_state_dict(state_dict, strict=False)
        else:
            raise ValueError("Unsupported model format. Save a full PyTorch model or a state_dict.")

        self.model.to(self.device)
        self.model.eval()

    def predict(self, image_path: str) -> Tuple[str, float]:
        if self.model is None:
            return "model_not_loaded", 0.0

        image = Image.open(image_path).convert("RGB")
        tensor = self.transform(image).unsqueeze(0).to(self.device)

        with torch.no_grad():
            outputs = self.model(tensor)
            probabilities = torch.softmax(outputs, dim=1)[0]
            confidence, predicted_idx = torch.max(probabilities, dim=0)

        idx = int(predicted_idx.item())
        label = LABELS[idx] if idx < len(LABELS) else f"class_{idx}"
        return label, float(confidence.item())

classifier = SmartWardrobeClassifier()
from pathlib import Path

import torch
from PIL import Image
from torchvision import transforms, models

from app.config import MODEL_PATH


LABELS = ["men_hot", "men_cold", "women_hot", "women_cold"]


class WardrobeClassifier:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = None
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])
        self._load_model()

    def _get_state_dict(self, checkpoint):
        if isinstance(checkpoint, dict):
            if "model_state_dict" in checkpoint:
                return checkpoint["model_state_dict"]
            elif "state_dict" in checkpoint:
                return checkpoint["state_dict"]
            else:
                return checkpoint
        return None

    def _load_model(self):
        path = Path(MODEL_PATH)

        print("MODEL_PATH:", MODEL_PATH)
        print("Absolute model path:", path.resolve())

        if not path.exists():
            print(f"WARNING: Model file not found at {path.resolve()}")
            self.model = None
            return

        try:
            checkpoint = torch.load(path, map_location=self.device)
            state_dict = self._get_state_dict(checkpoint)

            # Case 1: file .pt lưu nguyên model
            if state_dict is None:
                self.model = checkpoint
                self.model.to(self.device)
                self.model.eval()
                print("Loaded full PyTorch model successfully.")
                return

            # Case 2: file .pt lưu state_dict
            model = models.resnet50(weights=None)

            # Model của bạn có fc dạng:
            # fc.1, fc.3, fc.5
            if "fc.1.weight" in state_dict and "fc.5.weight" in state_dict:
                fc1_in = state_dict["fc.1.weight"].shape[1]
                fc1_out = state_dict["fc.1.weight"].shape[0]
                fc5_out = state_dict["fc.5.weight"].shape[0]

                print("Detected custom FC structure")
                print("fc.1 input:", fc1_in)
                print("fc.1 output:", fc1_out)
                print("fc.5 output/classes:", fc5_out)

                model.fc = torch.nn.Sequential(
                    torch.nn.Dropout(0.3),
                    torch.nn.Linear(fc1_in, fc1_out),
                    torch.nn.ReLU(),
                    torch.nn.BatchNorm1d(fc1_out),
                    torch.nn.Dropout(0.3),
                    torch.nn.Linear(fc1_out, fc5_out)
                )

            else:
                # fallback nếu sau này model khác chỉ có fc.weight/fc.bias
                num_classes = len(LABELS)
                model.fc = torch.nn.Linear(model.fc.in_features, num_classes)

            model.load_state_dict(state_dict)
            model.to(self.device)
            model.eval()

            self.model = model
            print("AI model loaded successfully from:", path.resolve())

        except Exception as e:
            print("ERROR loading model:", e)
            self.model = None

    def predict(self, image_path: str):
        if self.model is None:
            print("Model is not loaded. Returning fallback label.")
            return "model_not_loaded", 0.0

        try:
            image = Image.open(image_path).convert("RGB")
            image_tensor = self.transform(image).unsqueeze(0).to(self.device)

            with torch.no_grad():
                outputs = self.model(image_tensor)
                probabilities = torch.softmax(outputs, dim=1)
                confidence, predicted_idx = torch.max(probabilities, 1)

            predicted_idx = predicted_idx.item()
            confidence = confidence.item()

            if predicted_idx >= len(LABELS):
                return "unknown", confidence

            label = LABELS[predicted_idx]

            print("AI prediction:", label, confidence)

            return label, confidence

        except Exception as e:
            print("ERROR during prediction:", e)
            return "prediction_error", 0.0


classifier = WardrobeClassifier()