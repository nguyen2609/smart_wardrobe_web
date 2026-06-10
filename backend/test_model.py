import torch
from torchvision import transforms, models
from PIL import Image
from pathlib import Path


# Thứ tự label đúng theo lúc train:
# ['Men_Cold', 'Men_Hot', 'Women_Cold', 'Women_Hot']
LABELS = ["men_cold", "men_hot", "women_cold", "women_hot"]

MODEL_PATH = "smart_wardrobe_resnet50.pt"
IMAGE_PATH = "test_image.jpg"


def get_state_dict(checkpoint):
    if isinstance(checkpoint, dict):
        if "model_state_dict" in checkpoint:
            return checkpoint["model_state_dict"]
        elif "state_dict" in checkpoint:
            return checkpoint["state_dict"]
        else:
            return checkpoint
    return None


def load_model():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    checkpoint = torch.load(MODEL_PATH, map_location=device)
    state_dict = get_state_dict(checkpoint)

    # Trường hợp file .pt lưu nguyên model
    if state_dict is None:
        model = checkpoint
        model.to(device)
        model.eval()
        return model, device

    print("Some checkpoint keys:")
    for key in list(state_dict.keys())[-10:]:
        value = state_dict[key]
        print(key, value.shape if hasattr(value, "shape") else "")

    model = models.resnet50(weights=None)

    # Model của bạn có fc dạng: fc.1, fc.3, fc.5
    if "fc.1.weight" in state_dict and "fc.5.weight" in state_dict:
        fc1_in = state_dict["fc.1.weight"].shape[1]
        fc1_out = state_dict["fc.1.weight"].shape[0]
        fc5_out = state_dict["fc.5.weight"].shape[0]

        print("\nDetected custom FC structure:")
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
        model.fc = torch.nn.Linear(model.fc.in_features, len(LABELS))

    model.load_state_dict(state_dict)
    model.to(device)
    model.eval()

    return model, device


def predict(image_path):
    model, device = load_model()

    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        )
    ])

    image = Image.open(image_path).convert("RGB")
    image_tensor = transform(image).unsqueeze(0).to(device)

    with torch.no_grad():
        outputs = model(image_tensor)
        probabilities = torch.softmax(outputs, dim=1)
        confidence, predicted_idx = torch.max(probabilities, 1)

    predicted_idx = predicted_idx.item()
    confidence = confidence.item()
    label = LABELS[predicted_idx]

    print("\n========== RESULT ==========")
    print("Image:", image_path)
    print("Predicted index:", predicted_idx)
    print("Predicted label:", label)
    print("Confidence:", round(confidence * 100, 2), "%")

    print("\nAll probabilities:")
    for i, prob in enumerate(probabilities[0]):
        print(f"{LABELS[i]}: {round(prob.item() * 100, 2)}%")

    print("============================")


if __name__ == "__main__":
    if not Path(MODEL_PATH).exists():
        print("Model not found:", MODEL_PATH)
    elif not Path(IMAGE_PATH).exists():
        print("Image not found:", IMAGE_PATH)
        print("Please put your image inside backend folder and rename it to test_image.jpg")
    else:
        predict(IMAGE_PATH)