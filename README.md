# PocketSmart AI: Your Smart Budget & Recommendation Assistant

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Google Gemini](https://img.shields.io/badge/AI%20Model-Gemini%201.5%20Flash%20Pro-4285F4.svg?logo=google&logoColor=white)](https://ai.google.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**PocketSmart AI** is an intelligent, full-stack AI-powered personal budget planner and personalized shopping recommendation assistant. Built in strict accordance with the official **SmartBridge / SmartInternz Project Specification (39 Pages)** and designed with modern, responsive UI/UX inspired by the reference walkthrough video.

Powered by **FastAPI** and **Google Gemini 1.5 Flash Pro**, PocketSmart AI optimizes user allocations across three dedicated real-world scenarios, generates itemized calculation tables in INR (₹), and integrates direct search links to leading Indian commerce platforms including **Amazon, Flipkart, IKEA, Pepperfry, Swiggy, Zomato, OYO, CaratLane, Tanishq, and BlueStone**.

---

## 🌟 Key Features

### 1. Home Interior Budget Planner
- **Intelligent Allocation**: Room-by-room budgeting (Living Room, Kitchen, Bedroom, Bathroom) tailored to Indian households.
- **Specific Requirement Inputs**: Captures lighting fixtures, ceiling fans, furniture count, and dining table requirements.
- **Budget Calculation Table**: Mathematically accurate category-wise cost allocation with item count, total price, and percentage share.
- **Vendor Integrations**: Direct search links for **IKEA**, **Amazon India**, and **Flipkart**.

### 2. Party Budget Planner
- **Event Specialization**: Supports Birthdays, Weddings, Anniversaries, Corporate Events, and Dinners.
- **Venue Recommendations**: Recommends appropriate venues (banquet halls, lawns, rooftop lounges, private villas) with guest capacities and estimated costs.
- **Catering & Hospitality**: Allocates budget for buffet/plated dining, mocktails, thematic decor, and entertainment (DJ, photo booth).
- **Vendor Integrations**: Direct links to **Swiggy**, **Zomato**, and **OYO Rooms & Venues**.

### 3. Jewelry Budget Planner (Multimodal AI)
- **Occasion-Based Styling**: Bridal, engagement, festive celebrations, cocktail galas, and daily wear.
- **Outfit Image Upload & Multimodal Analysis**: Upload an outfit photo (JPEG/PNG) to analyze color palettes, embroidery tones, and neckline styles via Gemini 1.5 Pro multimodal vision.
- **Curated Recommendations**: Recommends necklaces, earrings (Jhumkas/Chandbalis), bangles, and rings in gold, silver, diamond, or kundan.
- **Vendor Integrations**: Direct search links to **Tanishq**, **CaratLane**, **BlueStone**, and **Myntra**.

### 4. Robust User Authentication & Session Management
- **Security**: Password hashing using SHA-256 PBKDF2/Bcrypt and stateless JWT tokens (`HS256`).
- **Dual Auth Support**: Supports both HTTP Bearer authorization headers and secure `HttpOnly` browser cookies.
- **Active Session Tracking**: Tracks login timestamps, last activity, and stored session data with automatic background expiration (30 minutes).

### 5. Recommendation History Log & Dashboard
- **History Tracking**: Automatically persists every generated home, party, and jewelry plan with unique IDs.
- **Interactive Dashboard**: High-level metrics (total planned budget, remaining budget savings, distribution by planner).
- **Modal Inspection**: Full detail inspection for each saved plan directly from the Dashboard or History view.

### 6. Resilient Offline Fallback Engine
- When no Google Gemini API key is configured or during internet/API disruptions, PocketSmart AI automatically switches to a comprehensive mathematical offline recommendation engine to ensure 100% uptime and realistic Indian market estimates.

---

## 🛠 Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Backend Framework** | **FastAPI** (`FastAPI(title="PocketSmart: AI Budget Planner")`) |
| **ASGI Server** | **Uvicorn** (`uvicorn app:app --host 0.0.0.0 --port 8000 --reload`) |
| **AI / LLM Engine** | **Google Gemini 1.5 Flash Pro** (`gemini-1.5-flash`) via `google-generativeai` |
| **Multimodal Processing** | **Pillow (PIL)** for outfit photo analysis and visual feature extraction |
| **Authentication & Tokens** | **Python-Jose** (JWT tokens), **Passlib** / **PBKDF2** password hashing |
| **Frontend Templates** | **Jinja2** Server-Side Rendered Templates with dynamic client-side JS |
| **Styling & UX** | Pure **Vanilla CSS** (`static/styles.css`) — Dark glassmorphic design system |
| **Data Persistence** | JSON-backed local storage (`users_db.json`, `history_db.json`, `active_sessions`) |

---

## 📁 Project Folder Structure

```
PocketSmart AI/
│
├── app.py                      # Main FastAPI application instance and middleware setup
├── main.py                     # Entry point running Uvicorn server on port 8000
├── gemini_utils.py             # Gemini 1.5 Flash Pro integration, prompts & offline fallbacks
├── requirements.txt            # Python dependencies
├── test_app.py                 # Automated 8-module test suite
├── .env.example                # Example environment variables template
├── .env                        # Local environment variables (API keys & JWT secret)
├── .gitignore                  # Git ignore rules
│
├── models/                     # Pydantic schemas (PDF contract)
│   ├── __init__.py
│   ├── user.py                 # User authentication and registration models
│   ├── home.py                 # Home Interior Planner request/response schemas
│   ├── party.py                # Party Budget Planner request/response schemas
│   ├── jewelry.py              # Jewelry Planner request/response schemas
│   ├── session.py              # User session state models
│   └── history.py              # History log persistence models
│
├── routes/                     # Modular FastAPI routers
│   ├── __init__.py
│   ├── auth_routes.py          # /login, /register, /logout, /token
│   ├── session_routes.py       # /session-info, /session-data
│   ├── home_routes.py          # GET /home-budget, POST /generate-home
│   ├── party_routes.py         # GET /party-budget, POST /generate-party
│   ├── jewelry_routes.py       # GET /jewelry-budget, POST /generate-jewelry
│   ├── history_routes.py       # GET /history, /recommendation-history, /recommendation-details/{id}
│   └── page_routes.py          # GET /, /dashboard, /testimonials, /startup
│
├── services/                   # Business logic and platform integrations
│   ├── __init__.py
│   ├── auth_service.py         # JWT generation, token verification, session tracking
│   ├── gemini_service.py       # Gemini API client wrapper
│   ├── history_service.py      # Recommendation history CRUD
│   ├── platform_service.py     # Search links for Amazon, IKEA, Swiggy, Zomato, etc.
│   └── recommendation_service.py # Budget aggregation logic
│
├── static/                     # Static frontend assets
│   ├── styles.css              # Custom responsive CSS design system
│   └── uploads/                # Directory for uploaded outfit images
│
└── templates/                  # Jinja2 HTML templates
    ├── index.html              # Landing page (Hero, Planner cards, Testimonials preview)
    ├── login.html              # User Sign In
    ├── register.html           # User Registration
    ├── dashboard.html          # User Analytics & recent recommendations
    ├── home_planner.html       # Home Interior Planner with calculation table
    ├── party_planner.html      # Party Budget Planner with venue suggestions
    ├── jewelry_planner.html    # Jewelry Planner with outfit photo upload
    ├── history.html            # Past recommendations history & filter
    └── testimonials.html       # User reviews & testimonials page
```

---

## 🚀 Installation & Setup

### 1. Prerequisites
- **Python 3.10+** (Python 3.10, 3.11, 3.12, 3.13, or 3.14)
- **pip** package installer
- **Git**

### 2. Clone the Repository
```bash
git clone <repository-url>
cd "PocketSmart AI"
```

### 3. Create and Activate Virtual Environment (Recommended)
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Open `.env` and configure your credentials:
```env
# Google Gemini API Key (Get free key from https://aistudio.google.com/)
GEMINI_API_KEY=your_gemini_api_key_here

# JWT Security
SECRET_KEY=your_super_secret_jwt_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Server Binding
HOST=0.0.0.0
PORT=8000
DEBUG=True
```
> **Note**: If `GEMINI_API_KEY` is not provided or invalid, PocketSmart AI will gracefully and seamlessly utilize its built-in realistic offline fallback generator.

---

## 🏃 Running the Application

### Option A: Using `main.py`
```bash
python main.py
```

### Option B: Using Uvicorn Directly
```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

Once running, access the web application in your browser:
- **Landing Page**: [http://localhost:8000/](http://localhost:8000/)
- **Interactive API Documentation (Swagger UI)**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Alternative API Documentation (ReDoc)**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **System Startup Verification**: [http://localhost:8000/startup](http://localhost:8000/startup)

---

## 🔑 Default Demo Account
A demonstration user is pre-configured for instant evaluation:
- **Username**: `demouser`
- **Password**: `password123`

You can also click **"Create Account"** on the registration page to register any new user.

---

## 🧪 Running the Verification Test Suite

PocketSmart AI includes an automated end-to-end test suite (`test_app.py`) verifying:
1. `GET /startup` system status
2. All 7 HTML pages (`/`, `/home-budget`, `/party-budget`, `/jewelry-budget`, `/testimonials`, `/login`, `/register`)
3. Full Authentication flow (`/register`, `/login`, `/dashboard`, `/session-info`)
4. `POST /generate-home` with calculation table and item breakdown
5. `POST /generate-party` with venue suggestions and categories
6. `POST /generate-jewelry` with budget and styling options
7. `POST /generate-jewelry` with real binary outfit image upload
8. `GET /history` and `GET /recommendation-details/{id}` persistence

Run the test suite with:
```bash
python test_app.py
```
Expected output:
```text
=== Starting PocketSmart AI Verification Suite ===
PASS: GET /startup verified successfully.
PASS: All public HTML pages (/, /home-budget, /party-budget, /jewelry-budget, /testimonials, /login, /register) verified.
PASS: Auth flow (/register, /login, /dashboard, /session-info) verified.
PASS: POST /generate-home verified with 5 categories and calculation table.
PASS: POST /generate-party verified with 4 budget categories and 2 venue suggestions.
PASS: POST /generate-jewelry verified with 3 items and styling advice.
PASS: POST /generate-jewelry with outfit image upload verified.
PASS: GET /history and GET /recommendation-history verified.
PASS: GET /recommendation-details/{id} verified.

ALL 8 CORE TEST MODULES PASSED SUCCESSFULLY! 100% SPEC COMPLIANCE VERIFIED.
```

---

## 📑 Required Endpoints Reference (PDF Contract)

| HTTP Method | Route | Description |
| :--- | :--- | :--- |
| `GET` | `/startup` | Verifies system startup, framework, and AI model |
| `POST` | `/generate-home` | Home Interior Planner recommendation engine |
| `POST` | `/generate-party` | Party Budget Planner recommendation engine |
| `POST` | `/generate-jewelry` | Jewelry Planner recommendation engine (supports multipart photo upload) |
| `GET` | `/home-budget` | Serves Home Interior Planner UI |
| `GET` | `/party-budget` | Serves Party Budget Planner UI |
| `GET` | `/jewelry-budget` | Serves Jewelry Planner UI |
| `POST` | `/register` | Registers new user account |
| `POST` | `/login` | Authenticates user and returns JWT |
| `POST` | `/logout` | Invalidates token and clears cookie session |
| `POST` | `/token` | OAuth2 standard password flow |
| `GET` | `/session-info` | Returns current active session metadata |
| `POST` | `/session-data` | Updates personalized user session preferences |
| `GET` | `/dashboard` | User dashboard showing savings, totals, and recent recommendations |
| `GET` | `/history` | Full recommendation history page |
| `GET` | `/recommendation-history` | JSON endpoint for user recommendation history log |
| `GET` | `/recommendation-details/{id}` | Detailed recommendation inspection by path parameter |
| `GET` | `/recommendations-details` | Detailed recommendation inspection by query parameter |
| `GET` | `/testimonials` | User reviews and testimonial showcases |

---

## 🛡 Security Best Practices
- **No Hardcoded Secrets**: All API keys and secrets reside in `.env`.
- **Safe Session Storage**: JWT tokens stored in `HttpOnly`, `SameSite=Lax` cookies.
- **Input Sanitization**: Pydantic input models enforce type validation and positive budget limits.
- **Fail-Safe Fallbacks**: Zero exposure of raw internal stack traces to client requests.

---

## 📜 License
This project is developed for educational and demonstration purposes following the official SmartInternz AI curriculum. Licensed under the MIT License.
