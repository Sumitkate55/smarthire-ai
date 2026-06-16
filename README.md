# SmartHire AI

SmartHire AI is a Django web app that analyzes PDF resumes, extracts technical skills, matches them against curated job-role profiles, and generates a readable score report with optional GitHub profile insights.

## What works now

- User registration and login
- PDF resume upload with size validation
- Skill extraction and role matching
- Resume quality scoring and feedback
- Analysis history per user
- Persistent storage without MongoDB using Django's default database
- Optional MongoDB support when `MONGODB_URI` is configured

## Local Setup

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Copy the environment template:

```bash
cp .env.example .env
```

4. Run migrations:

```bash
python manage.py migrate
```

5. Start the app:

```bash
python manage.py runserver
```

Open `http://127.0.0.1:8000`.

## Environment Variables

Required for production:

- `SECRET_KEY`
- `DEBUG=False`
- `ALLOWED_HOSTS=your-domain.com`

Optional:

- `MONGODB_URI`
- `JSEARCH_API_KEY`
- `ADZUNA_APP_ID`
- `ADZUNA_APP_KEY`
- `GITHUB_TOKEN`
- `CSRF_TRUSTED_ORIGINS=https://your-domain.com`

## Deployment Notes

- The app runs with SQLite by default, so MongoDB is no longer required.
- `build.sh` installs dependencies, collects static assets, and runs migrations.
- On Render or other proxy-based hosts, `SECURE_PROXY_SSL_HEADER` is already configured.

## Tests

Run:

```bash
python manage.py test
```
