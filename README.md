# 🚀 Real-Time Order Tracking System

A full-stack Order Tracking System built using FastAPI and React.

---

## 🔥 Features

* 🔐 Authentication (Login/Register)
* 📦 Product Management
* 🧾 Order Creation
* 🚚 Live Order Tracking (WebSocket)
* 🔔 Notifications
* 👑 Admin Dashboard (Revenue + Orders)

---

## 🏗️ Tech Stack

* Backend: FastAPI
* Frontend: React.js
* Database: SQLite
* Auth: JWT

---

## ⚙️ Backend Setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

---

## 🎨 Frontend Setup

```bash
cd frontend
npm install
npm start
```

---

## 🌐 API Docs

http://127.0.0.1:8000/docs

---

## 📡 WebSocket

ws://127.0.0.1:8000/ws/orders/{order_id}

---

## 🧪 Sample Order API

```json
{
  "user_email": "aarthi@gmail.com",
  "items": [
    {
      "product_id": "p1",
      "quantity": 2
    }
  ],
  "key": "order001"
}
```

---

## 👩‍💻 Author

Aarthi
Python Backend Developer

---

⭐ If you like this project, give it a star!
