# py_JobAutomation

**AI-Powered Job Application Automation System**

Live demo: [py-jobautomation.onrender.com](https://py-jobautomation.onrender.com)

[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.2.7-green.svg)](https://www.djangoproject.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## Overview

py_JobAutomation is a Django web application that streamlines the job application process. It analyzes job postings against a candidate's CV using an AI provider, calculates a match score, and generates professional cover letters (German *Anschreiben* or English cover letter).

---

## Features

- **CV management** — Create and maintain multiple CV profiles per user, each with education, work experience, skills, certifications, languages, and administrative processes (work permit, diploma evaluation, etc.).
- **AI-powered job matching** — Paste a job posting and the system compares it against the user's CV, returns a match score (0–100), and recommends `apply`, `review`, or `skip`.
- **Automatic cover letter generation** — Produces a localised cover letter (default: German) based on the matched CV and job posting.
- **Application history** — All analyses and generated cover letters are saved and browsable.
- **Per-user AI provider settings** — Each user configures their own API key and preferred AI provider (OpenAI, Google Gemini, or Groq). Keys are stored encrypted (Fernet).
- **Heuristic fallback** — If the AI call fails or no key is configured, a keyword-based heuristic produces a score without making external API calls.
- **User authentication** — Standard Django registration and login.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Django 5.2.7, Python 3.13 |
| AI providers | OpenAI (GPT-4o-mini default), Google Gemini (gemini-1.5-flash default), Groq (llama-3.3-70b-versatile default) |
| Database | SQLite (default) |
| Frontend | Bootstrap 5, Font Awesome |
| Server | Gunicorn |
| Testing | pytest, pytest-django, pytest-cov |

---

## Project Structure

```
py_JobAutomation/       # Django project settings & root URLs
users/                  # Registration, login, logout
cv_manager/             # CV profiles and sub-models (Education, Experience, Skill, …)
job_analyzer/           # Job posting analysis and quick-apply workflow
applicant_letters/      # Cover letter / Anschreiben generation and drafts
ai_bridge/              # AI provider abstraction, per-user settings, encrypted keys
```

---

## Requirements

- Python 3.13
- pip

AI features require an API key for at least one supported provider (OpenAI, Google Gemini, or Groq). The application functions without an API key — matching falls back to heuristic scoring and no cover letter is generated.

---

## Installation

```bash
git clone https://github.com/mhilmicicek07/py_JobAutomation.git
cd py_JobAutomation

python -m venv venv
# Windows
venv\Scripts\activate
# Linux / macOS
source venv/bin/activate

pip install -r requirements.txt
cp env.example .env          # edit .env with your values
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

The application is available at `http://127.0.0.1:8000/`.

---

## Docker

```bash
docker compose up -d --build
```

The container exposes port `8000`. The SQLite database and media files are mounted as volumes (`./db.sqlite3`, `./media`).

---

## Configuration

Copy `env.example` to `.env` and set the variables relevant to your deployment.

| Variable | Default | Description |
|---|---|---|
| `SECRET_KEY` | insecure default | Django secret key — **must** be changed in production |
| `DEBUG` | `True` | Set to `False` in production |
| `ALLOWED_HOSTS` | `*` | Comma-separated list of allowed hostnames |
| `AI_PROVIDER` | `openai` | Global fallback AI provider (`openai`, `gemini`, `groq`) |
| `OPENAI_DEFAULT_MODEL` | `gpt-4o-mini` | Default OpenAI model |
| `OPENAI_MODEL_CV` | `gpt-4o-mini` | Model for CV extraction |
| `OPENAI_MODEL_POSTING` | `gpt-4o-mini` | Model for job posting extraction |
| `OPENAI_MODEL_LETTER` | `gpt-4o-mini` | Model for cover letter generation |
| `AI_COVER_LETTER_PROVIDER` | `openai` | Provider used specifically for cover letters |
| `JOB_MATCH_THRESHOLD_APPLY` | `80` | Score threshold for `apply` recommendation |
| `JOB_MATCH_THRESHOLD_REVIEW` | `50` | Score threshold for `review` recommendation |

Per-user AI provider and API key are configured via the in-app settings page (`/ai/settings/`). User-level settings take precedence over the global defaults above.

---

## Usage

1. Register an account and log in.
2. Go to **CV** (`/cv/`) and create a CV profile. Add education, experience, skills, and other sections as needed.
3. Optionally configure your AI provider at **AI Settings** (`/ai/settings/`).
4. Go to **Quick Apply** (`/jobs/quick-apply/`), paste a job posting, and submit.
5. Review the match score, decision, and generated cover letter.
6. Browse past analyses at **History** (`/jobs/history/`).

---

## Testing

```bash
pytest
```

To include a coverage report:

```bash
pytest --cov=. --cov-report=html
```

Coverage configuration is in `.coveragerc`. Test discovery follows `pytest.ini`.

---

## License

MIT — see [LICENSE](LICENSE).

## Developer

**Mehmet Hilmi Çiçek**
GitHub: [@mhilmicicek07](https://github.com/mhilmicicek07)
LinkedIn: [@mhilmicicek](https://linkedin.com/in/mhilmicicek)
Email: m.hilmicicek07@gmail.com
