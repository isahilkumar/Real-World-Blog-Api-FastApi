# 🚀 Real-World Blog API

A **production-grade Blog REST API** built with **FastAPI + PostgreSQL** following a structured 14-step learning path.

## ✨ Features

| Step | Feature |
|------|---------|
| 1 | FastAPI + PostgreSQL connection (SQLAlchemy) |
| 2 | User registration |
| 3 | Password hashing (bcrypt) |
| 4 | JWT authentication |
| 5 | Create blog posts |
| 6 | Full CRUD operations |
| 7 | Author-only authorization (403 for others) |
| 8 | Comments system |
| 9 | Pagination |
| 10 | Search & filtering |
| 11 | In-memory TTL caching |
| 12 | Rate limiting (60 req/min, 5/min login) |
| 13 | `.env` configuration (pydantic-settings) |
| 14 | Deploy to Render |

---

## 🗂️ Project Structure

```
blog-api/
├── app/
│   ├── main.py              # FastAPI app entry point
│   ├── database.py          # SQLAlchemy engine + session
│   ├── models/              # ORM models (User, Post, Comment)
│   ├── schemas/             # Pydantic validation schemas
│   ├── routers/             # API route handlers
│   ├── core/                # Security, config, cache, dependencies
│   └── middleware/          # Rate limiting
├── .env.example             # Environment variable template
├── requirements.txt         # Python dependencies
├── render.yaml              # Render deployment config
└── README.md
```

---

## 🛠️ Local Development Setup

### 1. Clone and create a virtual environment
```bash
git clone <your-repo-url>
cd blog-api
python -m venv venv
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure environment variables
```bash
cp .env.example .env
# Edit .env with your PostgreSQL credentials and a strong SECRET_KEY
```

### 4. Start PostgreSQL locally
Make sure PostgreSQL is running and the database exists:
```sql
CREATE DATABASE blog_db;
CREATE USER blog_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE blog_db TO blog_user;
```

### 5. Run the API
```bash
uvicorn app.main:app --reload
```

API will be live at: **http://localhost:8000**  
Interactive docs: **http://localhost:8000/docs**

---

## 📡 API Endpoints

### Authentication
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/auth/register` | No | Register new user |
| POST | `/auth/login` | No | Login → get JWT token |
| GET | `/auth/me` | ✅ | Get current user info |

### Posts
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/posts/` | No | List posts (paginated, searchable) |
| POST | `/posts/` | ✅ | Create a post |
| GET | `/posts/{id}` | No | Get a single post |
| PUT | `/posts/{id}` | ✅ Author only | Update a post |
| DELETE | `/posts/{id}` | ✅ Author only | Delete a post |

### Comments
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/posts/{id}/comments` | No | List comments (paginated) |
| POST | `/posts/{id}/comments` | ✅ | Add a comment |
| DELETE | `/comments/{id}` | ✅ Author only | Delete a comment |

### Users
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/users/{id}` | No | Get user profile |
| GET | `/users/{id}/posts` | No | Get user's posts |

### Query Parameters (GET /posts/)
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `page` | int | 1 | Page number |
| `limit` | int | 10 | Items per page (max 100) |
| `search` | string | — | Search in title + content |
| `author_id` | int | — | Filter by author |

---

## 🔐 Authentication Flow

1. **Register**: `POST /auth/register` with `username`, `email`, `password`
2. **Login**: `POST /auth/login` with `username`, `password` → receive `access_token`
3. **Use token**: Add header `Authorization: Bearer <access_token>` to protected requests

---

## 🌐 Deploying to Render

1. Push your code to GitHub
2. Connect your repo to [Render](https://render.com)
3. Select **"Use render.yaml"** — Render will auto-provision the database and web service
4. Set any secret env vars in the Render dashboard
5. Deploy! ✅

> ⚠️ Render's free PostgreSQL database expires after **90 days**. Upgrade to a paid plan for production use.

---

## 🧪 Testing with Swagger UI

1. Open **http://localhost:8000/docs**
2. Register a user → Login → copy `access_token`
3. Click **Authorize 🔓** → paste `Bearer <token>`
4. All protected endpoints are now available

---

## 📦 Tech Stack

- **FastAPI** — modern, fast web framework
- **SQLAlchemy** — ORM for PostgreSQL
- **pydantic-settings** — type-safe `.env` configuration
- **python-jose** — JWT creation and verification
- **passlib[bcrypt]** — secure password hashing
- **slowapi** — rate limiting
- **cachetools** — in-memory TTL caching
- **uvicorn** — ASGI server
- **Render** — cloud deployment platform

---

## 📄 License

MIT License
