# SmartHire AI 🚀

SmartHire AI is a modern, web-based Django application that serves as an intelligent resume analyzer. It extracts technical skills, matches candidate profiles against curated job roles, computes comprehensive match scores, and fetches GitHub profile insights for deep technical analysis.

This application is built with a dual-database architecture, supporting fallback to SQLite for local development and PostgreSQL / MongoDB for production-grade persistent hosting.

---

## Key Features

- **🔐 Safe Authentication & Session Management**: Secure user registration, sign-in, and sign-out pages with robust password hashing.
- **📄 Robust Resume Parsing**: Direct text extraction from PDF resumes utilizing the modern `pypdf` library with automated fallback to `PyPDF2`.
- **🎯 Dynamic Skill Matching**: Automatically analyzes resume text to extract technical skills and cross-checks them against 15+ curated job role profiles.
- **📊 Interactive Scoring Dashboard**: Detailed candidate reports showing matched skills, missing skill gaps, recommended learning pathways, and visual charts representing skill category concentrations.
- **🐙 GitHub Profile Integration**: Fetches repository counts, follower counts, primary languages, and top repositories for technical profile validation. Features a robust parser accepting full profile URLs, trailing slashes, or usernames.
- **💾 Dual-Database Hybrid Storage**: Uses Django ORM with SQLite (local) or PostgreSQL (production) for auth/sessions, and automatically saves resumes/scores to MongoDB Atlas (if configured) or the local SQL database.

---

## Technology Stack

- **Backend**: Python 3.13 / Django 4.2.13
- **Primary Database**: PostgreSQL (Production) / SQLite (Development)
- **Secondary Database**: MongoDB Atlas (Optional; fallbacks to relational tables automatically if not set)
- **Libraries**:
  - `pypdf` & `PyPDF2` (PDF text extraction)
  - `dj-database-url` (Dynamic database configuration)
  - `psycopg2-binary` (PostgreSQL client)
  - `requests` (API communications)
  - `whitenoise` (Optimized static asset serving)
- **Frontend**: HTML5, CSS3 (Custom Glassmorphism styling), Bootstrap Icons, Chart.js

---

## Local Setup

### 1. Prerequisites
- Python 3.10+ installed.
- Git installed.

### 2. Clone and Setup Environment
```bash
# Clone the repository
git clone https://github.com/Sumitkate55/smarthire-ai.git
cd smarthire-ai

# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Variables Setup
Copy the example environment file:
```bash
cp .env.example .env
```
Open `.env` and fill in the required keys.

### 4. Run Migrations & Start Server
```bash
# Apply database schema migrations
python manage.py migrate

# Collect static assets
python manage.py collectstatic --no-input

# Run the local server
python manage.py runserver
```
Navigate to `http://127.0.0.1:8000` in your web browser.

---

## Production Deployment (e.g., Render, Heroku)

> [!IMPORTANT]
> To deploy this application live and prevent data/session loss on container restarts:
> 1. Provision a **PostgreSQL** database (e.g., a free database on Render or Neon).
> 2. Set the `DATABASE_URL` environment variable in your deployment platform's dashboard. The application will automatically detect it, connect to it, and run migrations dynamically.
> 3. Add your external web app domain to the `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS` variables.

### Environment Variable Config

| Variable | Description | Example / Default |
| :--- | :--- | :--- |
| `SECRET_KEY` | Django secret key | `your-production-secret-key` |
| `DEBUG` | Toggle debug mode | `False` |
| `DATABASE_URL` | PostgreSQL Connection URI | `postgres://user:pass@host:port/dbname` |
| `ALLOWED_HOSTS` | Domains allowed to connect | `smarthire-ai.onrender.com` |
| `CSRF_TRUSTED_ORIGINS` | Trusted origins for CSRF validation | `https://smarthire-ai.onrender.com` |
| `MONGODB_URI` | Optional MongoDB Atlas URI | `mongodb+srv://...` |
| `GITHUB_TOKEN` | Optional GitHub Personal Access Token (prevents rate limits) | `ghp_yourTokenHere` |

---

## Testing

Verify that all systems are functioning properly by running the Django unit tests:
```bash
python manage.py test
```
The test suite includes validation of:
- Resume size constraints.
- Session and redirect workflows.
- Robust GitHub username extraction from URLs.
