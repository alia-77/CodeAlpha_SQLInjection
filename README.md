# SecureVault

A small FastAPI app built to demonstrate protection against SQL injection, along with a few other layers of security on top: encrypted sensitive data, hashed passwords, a capability code check, and session based auth.

## What it does

SecureVault is a basic employee record system. You log in, add employees with a name, email, SSN, and salary, and view them on a dashboard. The SSN and salary are encrypted before they ever touch the database, and the passwords are hashed, never stored as plain text.

There's also a `/sql-demo` page that walks through what a SQL injection attack looks like versus how this app avoids it by using an ORM instead of raw string-built queries.

## Security features

- Parameterized queries via SQLAlchemy, so user input never gets concatenated directly into SQL
- AES-256-GCM encryption for SSN and salary fields
- Bcrypt password hashing
- A capability code required at login in addition to username and password
- Session based authentication using signed cookies
- Cloud hosted Postgres database (Neon) instead of a local file, so credentials aren't sitting on a single machine

## Setup

Install dependencies:

```
pip install -r requirements.txt
```

Create a `.env` file in the project root with the following:

```
DATABASE_URL=your_neon_connection_string_here
SESSION_SECRET=your_random_secret_here
VAULT_SECRET=your_random_secret_here
CAPABILITY_CODE=your_chosen_code_here
```

Then run it:

```
uvicorn app:app --reload
```

The app will be available at `http://localhost:8000`.

## Placeholders you need to change

A few things in this repo are placeholders and should be swapped out before you rely on this anywhere beyond your own testing:

- **`SESSION_SECRET`, `VAULT_SECRET`, `CAPABILITY_CODE`** are read from environment variables with fallback defaults in the code. The fallbacks are not secure and are only there so the app doesn't crash if you forget to set them. Always set your own values as environment variables rather than relying on the defaults.
- **`DATABASE_URL`** has no fallback, the app will not start without it. Get this from your Neon dashboard under connection details.
- **The admin account** is created automatically the first time the app runs, using the username and password set in `app.py`. Take a look at that and make sure it's something you're comfortable with before deploying anywhere public.

## Deployment

This app is set up to be deployed on Render. The build command is `pip install -r requirements.txt` and the start command is `uvicorn app:app --host 0.0.0.0 --port $PORT`. Environment variables (`DATABASE_URL`, `SESSION_SECRET`, `VAULT_SECRET`, `CAPABILITY_CODE`) are set in Render's dashboard rather than locally.

Live demo link: https://codealpha-sqlinjection.onrender.com/

## Notes

This was built as a learning project focused on SQL injection prevention and basic data security practices, not as a production ready system. Things like rate limiting, password reset flows, and multi-user support were left out on purpose to keep the focus on the core security concepts.