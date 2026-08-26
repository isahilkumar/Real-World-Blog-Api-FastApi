# Frontend Blog SPA — Implementation Plan

## Goal
Build a beautiful, full-featured Single Page Application (SPA) served at `/ui` that consumes all API endpoints.

## Stack
- Pure HTML5 + Vanilla CSS + Vanilla JS (no frameworks, no build step)
- Served as `static/index.html` by FastAPI's StaticFiles

## Pages / Views
1. **Home** — paginated post feed with search
2. **Post Detail** — full post + comments + add comment
3. **Auth Modal** — register + login (JWT stored in localStorage)
4. **Write Post Modal** — create / edit post
5. **Profile** — user's posts

## API endpoints consumed
- GET /posts/ — list + search + paginate
- GET /posts/{id} — single post
- POST /posts/ — create post
- PUT /posts/{id} — update post
- DELETE /posts/{id} — delete post
- GET /posts/{id}/comments — paginated comments
- POST /posts/{id}/comments — add comment
- DELETE /comments/{id} — delete comment
- POST /auth/register — register
- POST /auth/login — login
- GET /auth/me — get current user
