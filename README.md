# ShopSmart — AI-Powered Price Comparison Platform

Full-stack e-commerce price comparison app: **Django 6 + DRF** backend + **React 18 + Vite 8** frontend. Compare offers across 8 Indian platforms with rule-based analysis, deal scoring, and decision reports.

---

## Features

- **8 Platform Support** — Amazon, Flipkart, Myntra, AJIO, Meesho, Croma, Reliance Digital, Tata CLiQ
- **Best Deal Score** — 8-factor weighted scoring (price, rating, reviews, offers, delivery, warranty, seller, freshness)
- **Rule-Based Analysis** — deterministic deal scoring with category insights, pros/cons, and recommendations (no external AI calls)
- **Decision Report** — Printable full-page report with radar charts, bar charts, price trends, and rule-based insights
- **Price History** — 30-day zigzag price tracking across platforms
- **Wishlists** — Guest + authenticated user wishlists
- **Price Alerts** — Set target prices, get notified when triggered
- **Admin Dashboard** — User management, product catalog, platform analytics
- **Dark/Light Theme** — Toggle with system preference detection
- **Mobile Responsive** — Hamburger menu, tablet breakpoints, skeleton loading

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Django 6.0.7, DRF 3.18.0, SimpleJWT, SQLite/PostgreSQL |
| Frontend | React 18, Vite 8, React Router 6, Axios, Recharts |
| AI | Rule-based deal analysis (deterministic, no external API calls) |
| Auth | JWT (30min access, 3-day refresh, rotation + blacklisting) |
| Security | SSRF protection, rate limiting, HSTS, CSRF, secure cookies |
| Testing | Django TestCase — 124 tests passing |
| Deploy | Docker, Gunicorn, WhiteNoise, Nginx |

---

## Monorepo Layout

```
ShopSmart/
├── backend/                  # Django + DRF
│   ├── config/               # settings, urls, wsgi
│   ├── products/             # 17 models, API views, services
│   │   ├── services/         # AI analysis, comparison, extraction
│   │   └── management/commands/  # seed_demo_products, fetch_images
│   ├── users/                # auth, profile, price alerts
│   ├── .env.example          # copy to .env
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                 # React + Vite
│   ├── src/
│   │   ├── components/       # AnalysisResult, Skeleton, ShareButton, etc.
│   │   ├── pages/            # Home, Analysis, ProductDetail, Admin, etc.
│   │   ├── context/          # AuthContext, ThemeContext
│   │   └── api/              # axios config
│   ├── .env.example          # copy to .env.development
│   └── Dockerfile
├── docker-compose.yml        # db + backend + frontend
└── README.md
```

---

## Quick Start (Local Development)

**Prerequisites:** Python 3.12+, Node.js 20+

### Option A: Manual Setup

**1. Backend**

```bash
cd backend
cp .env.example .env          # edit with your values (empty DB_* = SQLite)
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo_products   # seed 91 products + 352 offers
python manage.py createsuperuser      # admin login
python manage.py runserver 127.0.0.1:8000
```

**2. Frontend**

```bash
cd frontend
cp .env.example .env.development     # or just edit the file
npm install
npm run dev                          # http://localhost:5173
```

Health check: `GET http://127.0.0.1:8000/api/health/` → `{"status":"ok"}`

Admin login: `admin` / `Admin@123`

### Option B: Docker (one command)

```bash
cp backend/.env.example .env         # edit with real values
docker compose up --build
# Frontend → http://localhost:5173
# Backend  → http://localhost:8000/api/health/
```

---

## Environment Variables

### Backend (`backend/.env`)

| Variable | Required | Default | Description |
|---|---|---|---|
| `DJANGO_SECRET_KEY` | Yes | — | Django secret key |
| `DJANGO_DEBUG` | No | `False` | Debug mode |
| `DJANGO_ALLOWED_HOSTS` | No | `localhost,127.0.0.1` | Comma-separated hosts |
| `DB_NAME` | No | — | PostgreSQL database name (empty = SQLite) |
| `DB_USER` | No | — | PostgreSQL username |
| `DB_PASSWORD` | No | — | PostgreSQL password |
| `DB_HOST` | No | `localhost` | PostgreSQL host |
| `DB_PORT` | No | `5432` | PostgreSQL port |
| `CORS_ALLOWED_ORIGINS` | No | `http://localhost:5173` | Comma-separated origins |

### Frontend (`frontend/.env.development`)

| Variable | Required | Default | Description |
|---|---|---|---|
| `VITE_API_URL` | No | `http://127.0.0.1:8000/api` | Backend API URL |

---

## API Endpoints

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/api/health/` | — | Liveness probe |
| POST | `/api/analyze-url/` | — | Paste URL → rule-based comparison |
| GET | `/api/products/` | — | Paginated catalog |
| GET | `/api/products/:id/` | — | Product detail + offers |
| GET | `/api/products/:id/history/` | — | Price history |
| GET | `/api/categories/` | — | All categories |
| GET | `/api/supported-platforms/` | — | Supported platforms |
| GET/POST | `/api/wishlist/` | JWT | List / add to wishlist |
| POST | `/api/users/register/` | — | Register + JWT |
| POST | `/api/users/login/` | — | Login + JWT |
| GET/PATCH | `/api/users/me/` | JWT | Profile |
| POST | `/api/users/change-password/` | JWT | Change password |
| POST | `/api/users/forgot-password/` | — | Password reset |
| POST | `/api/users/reset-password/` | — | Confirm reset (uid/token) |
| GET/POST | `/api/users/alerts/` | JWT | Price alerts |
| GET | `/api/users/admin-stats/` | staff | Dashboard stats |
| POST | `/api/users/:id/promote/` | superuser | Promote/demote user |

---

## Testing

```bash
cd backend
python manage.py test products users --verbosity=2
```

124 tests covering: health check, products API, wishlist, URL analysis, AI scoring engine, comparison engine, extraction pipeline, variant matching, recommendation safety, coupon validity, auth (register/login/profile/password), admin stats, promote/demote, price alerts, forgot/reset password, token refresh.

---

## Deployment

### Render (Recommended for students)

**Backend:**
1. Push to GitHub
2. Create a new **Web Service** on Render
3. Build command: `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
4. Start command: `gunicorn config.wsgi:application --bind 0.0.0.0:$PORT`
5. Set environment variables: `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=False`, `DJANGO_ALLOWED_HOSTS`, `DB_*`, `CORS_ALLOWED_ORIGINS`

**Frontend:**
1. Create a new **Static Site** on Render
2. Build command: `npm install && npm run build`
3. Publish directory: `dist`
4. Set environment variable: `VITE_API_URL=https://<your-backend>.onrender.com/api`

### Railway

```bash
# Or use docker-compose.yml with Railway's Docker support
railway up
```

### Vercel (Frontend only)

```bash
cd frontend
npm run build
vercel deploy --prod
```

---

## Project Structure

- **17 Django models** — Product, ProductOffer, PriceHistory, Platform, Seller, Review, ReviewSummary, Coupon, ComparisonSession, SearchHistory, AIAnalysis, AIProviderLog, DataSource, AuditLog, URLAnalysis, ProductVariant, Wishlist
- **8 Platform extractors** — Amazon, Flipkart, Myntra, AJIO, Meesho, Croma, Reliance Digital, Tata CLiQ
- **8-factor scoring** — Price 35%, Rating 15%, Review Confidence 10%, Offers 10%, Delivery 10%, Warranty 10%, Seller 5%, Freshness 5%

---

## License

BCA Final Year Project — Punit Kumar
