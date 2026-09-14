# SurakshaYatra — Full Setup Guide

The app runs in **three modes**, controlled entirely by environment variables —
no code changes needed to move from a laptop demo to a real deployment.

| Mode | Database | SOS alerts |
|---|---|---|
| Default (nothing set) | SQLite, auto-created + seeded | Simulated `[DEMO]` message |
| + MySQL env vars | Real MySQL | Simulated `[DEMO]` message |
| + MySQL and Twilio env vars | Real MySQL | **Real WhatsApp message sent** |

`pymysql` and `twilio` are only imported when their env vars are actually
set, so you don't need MySQL or a Twilio account to run the local demo.

---

## 1. Quick local demo (no setup)

```bash
pip install -r requirements.txt
python app.py
```
Open http://localhost:5000. Uses SQLite, SOS is simulated. This is what
you've been testing already.

---

## 2. Real MySQL

1. Get a MySQL database. Free options that work fine for a student project:
   - **Railway** (MySQL plugin, same dashboard as your app — recommended, see hosting below)
   - **Aiven** (free tier, 1 month trial)
   - Or your college's own MySQL server if available
2. Run the schema once:
   ```bash
   mysql -h <host> -P <port> -u <user> -p <db_name> < schema.sql
   ```
3. Set environment variables before starting the app:
   ```bash
   export MYSQL_HOST=<host>
   export MYSQL_PORT=3306
   export MYSQL_USER=<user>
   export MYSQL_PASSWORD=<password>
   export MYSQL_DB=<db_name>
   python app.py
   ```
   The app will now read/write real MySQL instead of SQLite — same API,
   same frontend, nothing else changes.

---

## 3. Real WhatsApp SOS via Twilio

1. Create a free Twilio account: https://www.twilio.com/try-twilio
2. Go to **Messaging → Try it out → Send a WhatsApp message** to activate
   the WhatsApp Sandbox. You'll get:
   - A Twilio **Account SID** and **Auth Token** (from your Twilio console)
   - A sandbox WhatsApp number, e.g. `whatsapp:+14155238886`
3. On the phone you want to receive alerts (stand-in for "local authority"
   during your demo), send the join code Twilio gives you to that sandbox
   number on WhatsApp once. This links your phone to the sandbox.
4. Set environment variables:
   ```bash
   export TWILIO_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   export TWILIO_AUTH_TOKEN=your_auth_token
   export TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
   python app.py
   ```
5. Trigger the SOS button in the app — a real WhatsApp message will land
   on the joined phone within a few seconds.

**Important for the demo:** Twilio Sandbox can only message numbers that
have joined the sandbox. For judges, either:
   - have your own phone (already joined) visibly receive the alert, or
   - get a teammate/judge to join the sandbox beforehand with the join code

For production beyond sandbox (messaging arbitrary numbers), you'd need
Twilio WhatsApp Business approval — out of scope for hackathon stage, but
worth mentioning in your pitch as "the roadmap."

If Twilio isn't configured, `/api/sos` automatically falls back to the
`[DEMO]` simulated message — nothing breaks if you skip this step.

---

## 4. Hosting

**Recommended: Railway** (https://railway.app) — because you need both a
running Flask app AND a MySQL database, and Railway lets you provision
both in the same project/dashboard.

1. Push this project to a GitHub repo (`.gitignore` already excludes the
   local SQLite file and any `.env`).
2. On Railway: **New Project → Deploy from GitHub repo**.
3. Add a **MySQL** plugin to the same project (Railway → New → Database → MySQL).
   Railway gives you the host/port/user/password/db name automatically.
4. In your web service's **Variables** tab, set:
   - `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DB`
     (copy from the MySQL plugin's connection info)
   - `TWILIO_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_WHATSAPP_FROM` (once ready)
5. Railway auto-detects the `Procfile` (`web: gunicorn app:app`) and deploys.
6. Run `schema.sql` against the Railway MySQL instance once (Railway gives
   you a connection string you can use with any MySQL client, or their
   built-in query console).
7. You'll get a public URL like `your-app.up.railway.app` — open it on your
   phone for the demo so SOS geolocation works naturally.

**Alternative: Render** (https://render.com) — simpler if you're staying on
SQLite for now and just want the web app hosted; you'd still need a
separate MySQL provider (e.g. Aiven) if you want real MySQL alongside it.

**Heads up either way:** free tiers usually spin down after inactivity
(~15 min) and take ~20–30s to wake on the next request — don't let a long
gap happen right before your live demo.

---

## Files

- `app.py` — Flask backend (routes, SOS logic, mode switching)
- `db.py` — database abstraction (SQLite ↔ MySQL)
- `schema.sql` — MySQL schema + seed data
- `templates/index.html` — frontend, wired with IDs for dynamic content
- `static/app.js` — fetches from the backend and renders live data
- `static/style.css` — unchanged
- `Procfile` — `web: gunicorn app:app`, used by Railway/Render
