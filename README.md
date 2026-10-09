# PathGen — Personalized Career Roadmap Generator

A Django + DRF app that onboards a user with a short questionnaire (education,
known skills, career goal, daily study time), auto-generates a personalized
learning roadmap by diffing the target career's required skills against what
the user already knows, and tracks progress on a dashboard with charts —
finishing with a congratulations banner once the roadmap is 100% complete.

## Who is it for?
PathGen supports **both technical students** (BCA, B.Sc CS/IT, B.Tech ...) **and non-technical / business
students** (BBA, B.Com, BMS, BA, MBA ...) who may have no idea what a career roadmap even looks like.

For non-technical students it adds:
- Business education options in the questionnaire (BBA, B.Com, BMS, BA, MBA, 12th Commerce/Arts ...).
- **8 business careers, no coding needed:** Digital Marketing, Business Analyst, HR Management, Finance &
  Financial Analyst, Sales & Business Development, Product Management, Operations & Supply Chain,
  Entrepreneurship. Defined in `roadmap/management/commands/business_data.py`.
- A **"Not sure? Help me choose" quiz** (5 questions) that recommends the top 3 careers.
- Career cards with a plain-language tagline and example job titles, split into
  *Business & Management* vs *Technical* (the default tab follows the education chosen).
- Plain-language **"what is this?"** description under every roadmap step (`Skills.description`).
- Beginner-friendly experience wording ("Complete beginner" is clearly marked as a normal answer).
- The "known skills" step shows **only the skills of the chosen career**, and can simply be skipped by beginners.
- Every business roadmap ends with *Resume, LinkedIn & Interview Prep* so students finish job-ready.

## Stack
- Backend: Django 6, Django REST Framework
- Auth: **Phone number + OTP** (no passwords) on top of Django sessions
- Frontend: Django templates + vanilla JS (fetch) + Chart.js
- DB: SQLite (default, swap easily via `DATABASES` in `core/settings.py`)

## Project layout
```
pathgen/
├── core/            # project settings, root urls
├── accounts/        # signup / login / logout (forms + views)
├── roadmap/         # models, questionnaire, roadmap generation, roadmap API
│   └── management/commands/seed_data.py   # sample Skills/Careers seed
├── dashboard/       # dashboard page + summary API (charts, progress)
├── templates/        # login.html, signup.html, questionnaire.html, dashboard.html
└── static/css/style.css
```

## Setup

```bash
python -m venv venv
source venv/bin/activate        # venv\Scripts\activate on Windows

pip install -r requirements.txt

python manage.py migrate          # includes 0005_business_stream
python manage.py seed_data        # loads technical + business skills and careers (safe to re-run)
python manage.py createsuperuser   # optional, for /admin/

python manage.py runserver
```

Visit `http://127.0.0.1:8000/` — you'll land on the login page.

## Flow
1. **Sign up** → enter name + mobile number → receive OTP by SMS → enter OTP → account created and logged in.
   **Log in** works the same way: mobile number → OTP → logged in.
2. Redirected to **`/questionnaire/`** (a 6-step wizard: education → experience →
   career goal (with the help-me-choose quiz) → known skills (filtered to that career) → daily hours → days per week).
3. On submit, `roadmap/services.py::generate_learning_path()` builds a
   `LearningPath` containing only the skills the user doesn't already have,
   ordered by the career's skill priority.
4. Redirected to **`/dashboard/`**, which shows:
   - Career, total hours logged, % complete, skills completed
   - A bar chart (hours per subject) and a doughnut chart (completion split)
   - A "trail" list of roadmap topics — click **Mark complete** to log hours
     and complete a step
   - A 🎉 congratulations banner once every topic is completed

## Phone + OTP authentication (`accounts/`)
- `PhoneNumber` links one verified number to one user (the user's username is the number in `+91XXXXXXXXXX` form;
  there is no password). `PhoneOTP` stores each OTP as an HMAC hash (never the plain code).
- Security rules (all configurable in `core/settings.py`): OTP valid 5 min, 5 wrong attempts then locked,
  30 s resend cooldown, max 5 OTPs per number per hour, single-use codes, constant-time comparison.
- **SMS delivery is pluggable** (`accounts/sms.py`). Local development defaults to
  `ConsoleBackend`, which prints the OTP and displays it on the verification page while
  `DEBUG=True`. For real Indian mobile delivery, PathGen includes the Fast2SMS OTP API
  backend. It sends the same code PathGen verifies, using your Fast2SMS OTP template.

### Enable real OTP SMS (India / Fast2SMS)

1. Create a Fast2SMS account and obtain its API authorization key and OTP template ID.
   Complete any sender, template, or DLT registration required for your account.
2. Set these environment variables in the same terminal before starting Django (PowerShell):
   ```powershell
   $env:OTP_SMS_BACKEND = "accounts.sms.Fast2SMSBackend"
   $env:FAST2SMS_API_KEY = "your-api-key"
   $env:FAST2SMS_OTP_TEMPLATE_ID = "your-otp-template-id"
   python manage.py runserver
   ```
   For deployment, configure these as secret environment variables in the hosting service.
   Do not commit API keys to source control. Your provider may charge for messages.
3. Enter an Indian mobile number and confirm the received SMS. The app expires the OTP
   after five minutes and continues to apply its resend and attempt limits.

For Twilio, select `accounts.sms.TwilioBackend` and set `TWILIO_ACCOUNT_SID`,
`TWILIO_AUTH_TOKEN`, and `TWILIO_FROM_NUMBER`. Set `DJANGO_DEBUG=false` and a unique
`DJANGO_SECRET_KEY` in production; startup is blocked if the console-only SMS backend
is selected.

## Key models (`roadmap/models.py`)
- `UserProfile` — education, experience level, daily study time, onboarding flag
- `Skills` — the master skill catalog (with a plain-language `description`)
- `UserSkills` — skills a user already knows, and at what level
- `Career` / `CareerSkill` — a career (with `stream`, `tagline`, `example_roles`, `requires_coding`) and the skills (+ level + priority) it requires
- `LearningPath` / `PathSkill` — the generated roadmap and its ordered steps
- `StudyLog` — hours logged against a specific roadmap step (powers the charts)
- `SkillSubtopic` — the detailed syllabus under a skill (a "major topic"), grouped by
  a sub-heading (e.g. Skill "Python Basics" → group "Core Python" → topics like
  "Variables", "Functions", "OOP basics"). This is what lets the dashboard show a
  real curriculum per roadmap step instead of just a title.
- `SubtopicProgress` — per-user checkbox state for each `SkillSubtopic`. Checking off
  every subtopic under a skill automatically marks that roadmap step `COMPLETED`
  (and unchecking one re-opens it) — see `ToggleSubtopicAPIView` in `roadmap/views.py`.

## How "known skills" are handled in the roadmap

The questionnaire (`templates/questionnaire.html`) is a 6-step wizard: education →
experience → career goal → known skills (with subtopic-level detail, filtered to the chosen
career) → daily hours → days per week.

For the skills step, every skill's real subtopics are shown (e.g. "HTML & CSS" →
Semantic elements, Forms, Box model, Flexbox, Grid, Responsive design). The user
checks off only what they actually know — so "I've learned basic HTML/CSS" naturally
becomes checking 1–2 boxes, not the whole skill.

Critically, **`generate_learning_path()` (in `roadmap/services.py`) always adds every
skill the target career requires to the roadmap** — it no longer skips a skill just
because the user marked it as "known" at all. Instead:
- Any subtopic the user checked is pre-marked complete on the new roadmap.
- If *all* subtopics under a skill end up checked (or the user ticks "I know all of
  this already"), that roadmap step is auto-completed from the start.
- If only *some* are checked, the step shows up `IN_PROGRESS` with a partial
  checklist — exactly matching "I only know basic HTML/CSS" scenarios.

This means the full curriculum for a career is always visible on the dashboard, with
prior knowledge reflected as a head start rather than an invisible skip.

## API endpoints
```
POST   /accounts/signup/          (name + phone -> sends OTP)
POST   /accounts/login/           (phone -> sends OTP)
POST   /accounts/verify/          (OTP -> authenticates the phone number)
POST   /accounts/verify/resend/
GET    /accounts/logout/

GET    /api/skills/
GET    /api/careers/
POST   /api/questionnaire/submit/
GET    /api/roadmap/mine/
PATCH  /api/roadmap/skill/<id>/complete/     { "hours_logged": 4 }
PATCH  /api/roadmap/subtopic/<id>/toggle/    { "completed": true }
POST   /api/roadmap/log-hours/               { "path_skill": 1, "hours": 2 }
GET    /api/dashboard/summary/
```

All API endpoints (except signup/login) require an authenticated session —
the templates handle this automatically via cookies; if you call the API
from a separate tool (Postman, curl), log in first and pass the session
cookie + `X-CSRFToken` header on POST/PATCH requests.

## Extending it
- Add more business careers/skills: edit `roadmap/management/commands/business_data.py`
  (add the career to `Career.CAREER_OPTIONS` in `models.py` and run `makemigrations`), then re-run `seed_data`.
- Add more technical careers/skills: edit `roadmap/management/commands/seed_data.py` and
  re-run `python manage.py seed_data`, or use `/admin/`.
- Want JWT instead of session auth for a fully decoupled SPA frontend? Swap
  `DEFAULT_AUTHENTICATION_CLASSES` in `core/settings.py` for
  `rest_framework_simplejwt.authentication.JWTAuthentication` and add token
  endpoints — the DRF views won't need to change.
- Want email verification, password reset, or social login? Consider
  `django-allauth` on top of the existing `accounts` app.
