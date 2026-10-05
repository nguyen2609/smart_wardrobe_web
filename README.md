# Smart Wardrobe Web

Smart Wardrobe Web is a web application that allows users to manage their personal wardrobe and use an AI model to classify uploaded clothing images.

The project consists of two main parts:

- `frontend/`: React + Vite frontend for the wardrobe user interface
- `backend/`: FastAPI + MongoDB + PyTorch backend with an AI classification model

---

## Main Features

1. User registration and login.
2. Upload clothing images.
3. The backend uses the `smart_wardrobe_resnet50.pt` model to classify uploaded images into AI labels:
   - `men_hot`
   - `men_cold`
   - `women_hot`
   - `women_cold`
4. Since the current model cannot classify clothing types such as tops, bottoms, shoes, or accessories, users manually select the wardrobe category before saving an item.
5. Wardrobe items are stored in MongoDB and linked to each logged-in user.
6. The frontend displays wardrobe items in four categories:
   - Tops
   - Bottoms
   - Shoes
   - Accessories

---

## Project Structure

```txt
smart_wardrobe_web/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── auth.py
│   │   ├── model_service.py
│   │   ├── routes_auth.py
│   │   ├── routes_items.py
│   │   └── schemas.py
│   ├── uploads/
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    ├── src/
    │   ├── App.jsx
    │   ├── api.js
    │   ├── main.jsx
    │   ├── pages/
    │   │   ├── AuthPage.jsx
    │   │   └── WardrobePage.jsx
    │   └── styles/
    │       └── global.css
    ├── package.json
    └── index.html
```

---

## MongoDB Setup

There are two ways to configure MongoDB.

### Option 1: Local MongoDB

Install MongoDB Community Server and run MongoDB locally at:

```txt
mongodb://localhost:27017
```

### Option 2: MongoDB Atlas

Create a cluster on MongoDB Atlas and replace the `MONGO_URI` value in your `.env` file with your Atlas connection string.

---

## Running the Backend

Navigate to the backend directory:

```bash
cd backend
```

Create a Python virtual environment:

```bash
python -m venv venv
```

Activate the virtual environment.

### Windows

```bash
venv\Scripts\activate
```

### macOS/Linux

```bash
source venv/bin/activate
```

Install the required Python packages:

```bash
pip install -r requirements.txt
```

Create a `.env` file from the provided example.

### Windows

```bash
copy .env.example .env
```

### macOS/Linux

```bash
cp .env.example .env
```

Place the trained model file inside the `backend/` directory:

```txt
backend/smart_wardrobe_resnet50.pt
```

Start the FastAPI backend:

```bash
uvicorn app.main:app --reload
```

The backend will be available at:

```txt
http://localhost:8000
```

FastAPI API documentation is available at:

```txt
http://localhost:8000/docs
```

---

## Running the Frontend

Open a new terminal and navigate to the frontend directory:

```bash
cd frontend
```

Install the required dependencies:

```bash
npm install
```

Start the Vite development server:

```bash
npm run dev
```

The frontend will be available at:

```txt
http://localhost:5173
```

---

## PyTorch Model Notes

The file:

```txt
backend/app/model_service.py
```

currently supports two common ways of saving a PyTorch model.

### 1. Saving the Entire Model

```python
torch.save(model, "smart_wardrobe_resnet50.pt")
```

### 2. Saving Only the `state_dict`

```python
torch.save(model.state_dict(), "smart_wardrobe_resnet50.pt")
```

If your ResNet50 model was trained with a different number of classes or a different label order, update the `LABELS` variable in:

```txt
backend/app/model_service.py
```

The current configuration is:

```python
LABELS = ["men_hot", "men_cold", "women_hot", "women_cold"]
```

The order of these labels must match the class order used when training the model.

If the order is incorrect, the model may return the wrong label even if the prediction itself is correct.

---

## MongoDB Database

The default database name is:

```txt
smart_wardrobe
```

The application uses two main collections:

```txt
users
wardrobe_items
```

### Example Wardrobe Item

A wardrobe item stored in MongoDB has a structure similar to:

```json
{
  "user_id": "...",
  "category": "tops",
  "category_name": "Tops",
  "name": "White Shirt",
  "image_url": "/uploads/filename.jpg",
  "ai_label": "women_hot",
  "ai_confidence": 0.93,
  "created_at": "..."
}
```

---

## Technology Stack

### Frontend

- React
- Vite
- JavaScript
- CSS

### Backend

- Python
- FastAPI
- PyTorch
- MongoDB

### AI Model

- ResNet50
- PyTorch `.pt` model

---

## Application Workflow

The basic workflow of the application is:

```txt
User
  ↓
Register / Login
  ↓
Upload Clothing Image
  ↓
Select Wardrobe Category
  ↓
FastAPI Backend
  ↓
PyTorch ResNet50 Model
  ↓
AI Classification
  ↓
Save Item to MongoDB
  ↓
Display Item in User's Wardrobe
```

Each wardrobe item belongs to the currently logged-in user, allowing multiple users to maintain separate wardrobes in the same application.
