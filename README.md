# Smart Wardrobe Web

Project này gồm 2 phần rõ ràng:

- `frontend/`: React + Vite giao diện tủ đồ
- `backend/`: FastAPI + MongoDB + PyTorch model

## Chức năng chính

1. Đăng ký / đăng nhập tài khoản.
2. Upload ảnh quần áo.
3. Backend gọi model `smart_wardrobe_resnet50.pt` để phân loại nhãn AI:
   - `men_hot`
   - `men_cold`
   - `women_hot`
   - `women_cold`
4. Vì model hiện tại chưa phân loại được áo/quần/giày/phụ kiện, frontend cho người dùng tự chọn mục tủ đồ trước khi lưu.
5. Item được lưu vào MongoDB theo từng tài khoản đăng nhập.
6. Frontend hiển thị tủ đồ thành 4 nhóm:
   - Áo
   - Quần
   - Giày
   - Phụ kiện

---

## Cấu trúc thư mục

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

## Cài đặt MongoDB

Bạn có 2 cách:

### Cách 1: MongoDB local

Cài MongoDB Community Server rồi chạy MongoDB ở:

```txt
mongodb://localhost:27017
```

### Cách 2: MongoDB Atlas

Tạo cluster trên MongoDB Atlas rồi thay `MONGO_URI` trong file `.env`.

---

## Chạy backend

Vào thư mục backend:

```bash
cd backend
```

Tạo virtual environment:

```bash
python -m venv venv
```

Kích hoạt môi trường:

Windows:

```bash
venv\Scripts\activate
```

Mac/Linux:

```bash
source venv/bin/activate
```

Cài thư viện:

```bash
pip install -r requirements.txt
```

Tạo file `.env` từ mẫu:

```bash
copy .env.example .env
```

Nếu dùng Mac/Linux:

```bash
cp .env.example .env
```

Đặt file model của bạn vào thư mục `backend/`:

```txt
backend/smart_wardrobe_resnet50.pt
```

Chạy backend:

```bash
uvicorn app.main:app --reload
```

Backend chạy tại:

```txt
http://localhost:8000
```

API docs:

```txt
http://localhost:8000/docs
```

---

## Chạy frontend

Mở terminal mới:

```bash
cd frontend
npm install
npm run dev
```

Frontend chạy tại:

```txt
http://localhost:5173
```

---

## Lưu ý về model `.pt`

File `backend/app/model_service.py` đang hỗ trợ 2 kiểu model phổ biến:

1. Bạn save nguyên model:

```python
torch.save(model, "smart_wardrobe_resnet50.pt")
```

2. Bạn save `state_dict`:

```python
torch.save(model.state_dict(), "smart_wardrobe_resnet50.pt")
```

Nếu bạn train ResNet50 với số class khác hoặc thứ tự label khác, hãy sửa biến `LABELS` trong:

```txt
backend/app/model_service.py
```

Hiện tại:

```python
LABELS = ["men_hot", "men_cold", "women_hot", "women_cold"]
```

Nếu model của bạn dùng thứ tự khác, kết quả hiển thị sẽ bị sai nhãn.

---

## Database MongoDB

Database mặc định:

```txt
smart_wardrobe
```

Collections:

```txt
users
wardrobe_items
```

Một item được lưu dạng gần như sau:

```json
{
  "user_id": "...",
  "category": "tops",
  "category_name": "Áo",
  "name": "White shirt",
  "image_url": "/uploads/filename.jpg",
  "ai_label": "women_hot",
  "ai_confidence": 0.93,
  "created_at": "..."
}
```
