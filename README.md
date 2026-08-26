<div align="center">

# 🖊️ Inkwell — Real-World Blog API

**A production-grade REST API built with FastAPI + PostgreSQL**

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-SQLAlchemy-336791?style=for-the-badge&logo=postgresql&logoColor=white)](https://postgresql.org)
[![Render](https://img.shields.io/badge/Deployed_on-Render-46E3B7?style=for-the-badge&logo=render&logoColor=white)](https://render.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)

**[🌐 Live Demo](https://real-world-blog-api-fastapi.onrender.com) · [📖 Swagger Docs](https://real-world-blog-api-fastapi.onrender.com/docs) · [🔁 ReDoc](https://real-world-blog-api-fastapi.onrender.com/redoc)**

</div>

---

## 📌 Overview

**Inkwell** is a fully-featured blogging REST API built step-by-step to mirror a real production workflow. It covers everything from database design and user authentication to caching, rate limiting, and cloud deployment — making it an ideal reference project for learning or showcasing backend skills.

> Built as a **14-step** structured learning project. Every feature maps to a real-world backend engineering concept.

---

## ✨ Features

| # | Feature | Tech Used |
|---|---------|-----------|
| 1 | PostgreSQL database connection | SQLAlchemy 2.0 |
| 2 | User registration with validation | Pydantic v2 |
| 3 | Secure password hashing | bcrypt + passlib |
| 4 | JWT authentication | PyJWT |
| 5 | Blog post creation | FastAPI routers |
| 6 | Full CRUD (posts & comments) | SQLAlchemy ORM |
| 7 | Author-only authorization | FastAPI dependencies |
| 8 | Nested comments system | Relational FK + cascade |
| 9 | Pagination | SQLAlchemy offset/limit |
| 10 | Full-text search & author filtering | SQLAlchemy `ilike` |
| 11 | In-memory TTL caching | cachetools |
| 12 | Rate limiting (60 req/min, 5/min login) | SlowAPI |
| 13 | Environment-based config | pydantic-settings |
| 14 | One-click cloud deployment | Render + render.yaml |

---

## 🗂️ Project Structure

```
real-world-blog-api/
│
├── app/
│   ├── main.py                # FastAPI app assembly + middleware + routes
│   ├── database.py            # SQLAlchemy engine, session factory, fallback logic
│   │
│   ├── models/                # SQLAlchemy ORM models
│   │   ├── user.py            #   User (id, username, email, hashed_password)
│   │   ├── post.py            #   Post (id, title, content, summary, author_id)
│   │   └── comment.py         #   Comment (id, body, post_id, author_id)
│   │
│   ├── schemas/               # Pydantic request/response schemas
│   │   ├── user.py            #   UserCreate, UserOut, UserProfile
│   │   ├── post.py            #   PostCreate, PostUpdate, PostOut, PaginatedPosts
│   │   ├── comment.py         #   CommentCreate, CommentOut, PaginatedComments
│   │   └── auth.py            #   Token
│   │
│   ├── routers/               # API route handlers
│   │   ├── auth.py            #   POST /auth/register, POST /auth/login, GET /auth/me
│   │   ├── posts.py           #   CRUD /posts/
│   │   ├── comments.py        #   CRUD /posts/{id}/comments
│   │   └── users.py           #   GET /users/{id}
│   │
│   ├── core/
│   │   ├── config.py          #   pydantic-settings (loads .env)
│   │   ├── security.py        #   hash_password, verify_password, JWT encode/decode
│   │   ├── dependencies.py    #   get_current_user FastAPI dependency
│   │   └── cache.py           #   TTL cache helpers (posts list + post detail)
│   │
│   └── middleware/
│       └── rate_limit.py      #   SlowAPI Limiter (60/min global, 5/min login)
│
├── static/
│   └── index.html             # Frontend SPA (Inkwell blog UI)
│
├── main.py                    # Root-level entry point (for Render/uvicorn)
├── render.yaml                # Render Blueprint (web service + PostgreSQL)
├── requirements.txt           # Python dependencies
├── .env.example               # Environment variable template
└── README.md
```

---

## 📡 API Reference

### 🔐 Authentication

| Method | Endpoint | Auth | Description |
|--------|----------|:----:|-------------|
| `POST` | `/auth/register` | — | Create a new user account |
| `POST` | `/auth/login` | — | Login → returns `access_token` (JWT) |
| `GET` | `/auth/me` | ✅ | Get the currently authenticated user |

### 📝 Posts

| Method | Endpoint | Auth | Description |
|--------|----------|:----:|-------------|
| `GET` | `/posts/` | — | List posts (paginated, searchable, cached) |
| `POST` | `/posts/` | ✅ | Create a new post |
| `GET` | `/posts/{id}` | — | Get a single post by ID (cached) |
| `PUT` | `/posts/{id}` | ✅ Author | Update post (title, content, summary) |
| `DELETE` | `/posts/{id}` | ✅ Author | Delete post + cascade delete comments |

**Query parameters for `GET /posts/`:**

| Param | Type | Default | Description |
|-------|------|:-------:|-------------|
| `page` | `int` | `1` | Page number |
| `limit` | `int` | `10` | Items per page (max `100`) |
| `search` | `string` | — | Full-text search on title + content |
| `author_id` | `int` | — | Filter posts by author |

### 💬 Comments

| Method | Endpoint | Auth | Description |
|--------|----------|:----:|-------------|
| `GET` | `/posts/{id}/comments` | — | List comments for a post (paginated) |
| `POST` | `/posts/{id}/comments` | ✅ | Add a comment to a post |
| `DELETE` | `/comments/{id}` | ✅ Author | Delete your comment |

### 👤 Users

| Method | Endpoint | Auth | Description |
|--------|----------|:----:|-------------|
| `GET` | `/users/{id}` | — | Get public user profile |
| `GET` | `/users/{id}/posts` | — | List all posts by a user |

### 🩺 Health

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Detailed service health (DB, cache, rate limit status) |
| `GET` | `/api` | JSON status check |
| `GET` | `/docs` | Swagger interactive API docs |
| `GET` | `/redoc` | ReDoc API documentation |

---

## 🔐 Authentication Flow

```
1. Register   →  POST /auth/register   { username, email, password }
                 ← 201 { id, username, email, created_at }

2. Login      →  POST /auth/login      { username, password }   (form-data)
                 ← 200 { access_token, token_type: "bearer" }

3. Use token  →  Authorization: Bearer <access_token>
                 (Add this header to all protected requests)
```

**Token expiry:** 30 minutes (configurable via `ACCESS_TOKEN_EXPIRE_MINUTES`)

---

## 🛠️ Local Development

### Prerequisites

- Python 3.11+
- PostgreSQL (or use the built-in SQLite fallback for quick testing)

### 1. Clone the repo

```bash
git clone https://github.com/isahilkumar/Real-World-Blog-Api-FastApi.git
cd Real-World-Blog-Api-FastApi
```

### 2. Create a virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

```bash
cp .env.example .env
```

Edit `.env`:

```env
DATABASE_URL=postgresql://blog_user:your_password@localhost:5432/blog_db
SECRET_KEY=your-super-secret-key-min-32-chars   # openssl rand -hex 32
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
APP_NAME=Real-World Blog API
DEBUG=False
```

> **No PostgreSQL?** Just leave `DATABASE_URL` unset — the app automatically falls back to a local `blog.db` SQLite file.

### 5. Set up the PostgreSQL database (optional)

```sql
CREATE DATABASE blog_db;
CREATE USER blog_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE blog_db TO blog_user;
```

### 6. Run the server

```bash
uvicorn app.main:app --reload
```

| URL | Description |
|-----|-------------|
| http://localhost:8000 | Blog frontend UI |
| http://localhost:8000/docs | Swagger interactive docs |
| http://localhost:8000/redoc | ReDoc docs |
| http://localhost:8000/health | Health check |

---

## 🧪 Quick API Test (curl)

```bash
# 1. Register
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","email":"alice@example.com","password":"secret123"}'

# 2. Login
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
  -d "username=alice&password=secret123" | python -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# 3. Create a post
curl -X POST http://localhost:8000/posts/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"My First Post","content":"Hello, World!","summary":"An intro post"}'

# 4. List posts
curl http://localhost:8000/posts/?page=1&limit=10&search=hello
```

---

## 🌐 Deploy to Render

This project includes a [`render.yaml`](render.yaml) Blueprint that provisions **both** the web service and a PostgreSQL database automatically.

### Steps

1. **Fork / push** this repo to your GitHub account
2. Go to [dashboard.render.com](https://dashboard.render.com) → **New → Blueprint**
3. Connect your GitHub repo
4. Render reads `render.yaml` and creates:
   - A **Web Service** (`blog-api`) running uvicorn
   - A **PostgreSQL database** (`blog-db`) with auto-injected `DATABASE_URL`
5. Click **Apply** — done! ✅

### Environment Variables (auto-configured)

| Variable | Source |
|----------|--------|
| `DATABASE_URL` | Auto-injected from `blog-db` |
| `SECRET_KEY` | Auto-generated by Render |
| `ALGORITHM` | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` |

> ⚠️ **Note:** Render's free PostgreSQL tier expires after **90 days**. Upgrade to a paid plan for production use.

---

## 📦 Tech Stack

| Layer | Technology |
|-------|-----------|
| **Framework** | [FastAPI](https://fastapi.tiangolo.com) 0.115 |
| **Server** | [Uvicorn](https://www.uvicorn.org) (ASGI) |
| **Database** | PostgreSQL via [SQLAlchemy](https://sqlalchemy.org) 2.0 |
| **Validation** | [Pydantic](https://docs.pydantic.dev) v2 |
| **Auth** | [PyJWT](https://pyjwt.readthedocs.io) + [passlib](https://passlib.readthedocs.io) bcrypt |
| **Rate Limiting** | [SlowAPI](https://slowapi.readthedocs.io) |
| **Caching** | [cachetools](https://cachetools.readthedocs.io) TTLCache |
| **Config** | [pydantic-settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) |
| **Deployment** | [Render](https://render.com) |

---

## 🏗️ Architecture Decisions

- **Synchronous SQLAlchemy** — chosen for simplicity and compatibility with Render's free tier. Swap to `asyncpg` + SQLAlchemy async for high-throughput production use.
- **In-memory TTL cache** — lightweight and zero-dependency. For multi-instance deployments, replace with Redis.
- **SQLite fallback** — the app gracefully degrades to SQLite if PostgreSQL is unavailable (useful for local dev without Docker).
- **Absolute static path resolution** — `__file__`-based path ensures the frontend is served correctly regardless of the uvicorn working directory.

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

<div align="center">

Made with ❤️ using **FastAPI** · [⭐ Star this repo](https://github.com/isahilkumar/Real-World-Blog-Api-FastApi) if you found it useful!

</div>
