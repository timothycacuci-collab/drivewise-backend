# DriveWise Backend 🚗

FastAPI backend for the DriveWise driving theory test app.

## Local Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create `.env` file (copy from `.env.example`):
   ```
   ANTHROPIC_API_KEY=your_key_here
   SECRET_KEY=any_random_string_here
   DATABASE_URL=sqlite:///./drivewise.db
   FRONTEND_URL=http://localhost:3000
   ```

4. Run the server:
   ```bash
   python main.py
   ```

API will be at: http://localhost:8000
Docs at: http://localhost:8000/docs

## Deploy to Railway (Free)

1. Push this folder to a GitHub repo
2. Go to railway.app → New Project → Deploy from GitHub
3. Add environment variables:
   - `ANTHROPIC_API_KEY` → get from console.anthropic.com
   - `SECRET_KEY` → any random string
   - `DATABASE_URL` → Railway will give you a PostgreSQL URL
   - `FRONTEND_URL` → your Vercel frontend URL
   - `ENV` → production
4. Railway auto-deploys!

## API Endpoints

- `POST /api/auth/register` — create account
- `POST /api/auth/login` — sign in
- `POST /api/auth/logout` — sign out
- `GET  /api/auth/me` — current user
- `GET  /api/countries` — list countries
- `GET  /api/languages` — list languages
- `POST /api/tests/generate` — generate AI test
- `POST /api/tests/submit` — submit answers
- `POST /api/tests/translate` — translate questions
- `GET  /api/tests/stats` — user stats
- `GET  /api/tests/history` — test history
