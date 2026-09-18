# Farm Management Platform — Version 1

A production-ready Django web application for goat/animal farm management:
staff & RBAC, animal registry, breeding & kidding, health (vaccination /
deworming / treatment), weight & growth (ADG), feed, sales, purchases,
expenses, a farm dashboard, basic reports, search/filtering, and an audit
trail. Built exactly to the scope in the project's implementation plan
(Sections 1–27), with the schema designed to expand later into full farm
management + AI without a rebuild.

## Stack

- **Backend:** Django 5/6, Django REST Framework (available for future API
  work), Django Admin (full CRUD today for every module)
- **Frontend:** Django Templates + HTML + CSS + vanilla JS (no SPA framework)
- **Database:** Neon PostgreSQL in production, SQLite automatically for local
  dev/demo (no `DATABASE_URL` needed to try it out)
- **File/object storage:** Supabase, with local `media/` fallback when not
  configured
- **Deployment:** Docker + gunicorn, no AWS dependency

## Quick start (local, SQLite, no external accounts needed)

```bash
python -m venv venv
source venv/bin/activate          # venv\Scripts\activate on Windows
pip install -r requirements.txt

cp .env.example .env               # defaults work out of the box

python manage.py migrate
python manage.py seed_demo_data    # optional: creates a demo farm + owner login
python manage.py createsuperuser   # or use the seeded "owner" login below
python manage.py runserver
```

Open http://127.0.0.1:8000/ — you'll be redirected to the dashboard (or the
login page if not authenticated).

If you ran `seed_demo_data`, log in with:

- **Owner:** `owner` / `ChangeMe123!`
- **Vet staff:** `vet_amit` / `ChangeMe123!`

**Change these passwords immediately** — they're for demo purposes only.

## Connecting the real Neon database

1. Create a project at https://neon.tech and copy its connection string.
2. In `.env`, set:
   ```
   DATABASE_URL=postgresql://<user>:<password>@<host>/<dbname>?sslmode=require
   ```
3. Run `python manage.py migrate` again against the new database.

No code changes are needed — `config/settings/base.py` automatically uses
Postgres when `DATABASE_URL` is present and falls back to SQLite otherwise.

## Connecting Supabase storage

Set `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`, and `SUPABASE_BUCKET` in `.env`.
Until these are set, uploaded animal photos and documents are stored under
`media/` on the local filesystem so the app is fully usable without a
Supabase account during development.

## Docker

```bash
cp .env.example .env   # fill in real DATABASE_URL / SUPABASE_* for production
docker compose up --build
```

This runs migrations and starts gunicorn on port 8000.

## Project structure

```
apps/
  tenants/        Organization tenant, farm-scoping middleware & base models
  accounts/       Custom User, Role (RBAC)
  farms/          Farm, Location/Shed
  staff/          StaffMembership (staff CRUD + role assignment)
  animals/        Species, Breed, Animal, AnimalMovement, AnimalWeight (ADG)
  breeding/       BreedingRecord (heat/mating/pregnancy), KiddingRecord, Kid
  health/         Vaccination, Deworming, Treatment
  feed/           Feed master, FeedConsumption, stock alerts
  procurement/    Supplier, Purchase
  sales/          Customer, AnimalSale (auto total + SOLD status transition)
  finance/        Expense
  dashboard/      Farm Command Center KPIs + alerts (apps/dashboard/services.py)
  notifications/  Due-date notification records
  reports/        Basic reports (reads other apps' data, no models of its own)
  audit/          Generic signal-based AuditLog covering every business model
templates/        Django templates (base.html + per-app templates)
static/           CSS/JS
```

## What's implemented in Version 1

Everything in Section 4–15 of the plan: auth, staff & RBAC, the full animal
lifecycle (birth → weight → vaccination/deworming/treatment → breeding →
pregnancy → kidding → offspring → sale/death/culling), feed management,
sales/purchases/expenses, the farm dashboard, basic reports, search &
filtering (tag/ID/name + gender/breed/age/status/location/pregnancy/health
filters), and an audit trail covering create/update/delete on every
business-critical table.

**Owner-facing UI** is provided for the two highest-traffic screens
(Dashboard, Animal list/profile with the full lifecycle timeline, Reports).
**Every other module (staff, breeding, health, feed, sales, purchases,
expenses) is fully usable today through Django Admin**, which was
intentionally used for full CRUD everywhere to keep V1 deliverable — the
same models can be given dedicated templated views in a follow-up phase
without any database change.

## Multi-tenancy & security

- Every business table carries `farm`, `created_at`, `updated_at`,
  `created_by`, `updated_by` (see `apps/tenants/base_models.py`).
- `CurrentFarmMiddleware` resolves `request.farm` from the authenticated
  user's active `StaffMembership` — the frontend never supplies `farm_id`.
- RBAC roles (OWNER, ADMIN, FARM_STAFF, VETERINARY, INVENTORY_MANAGER,
  ACCOUNTANT) wrap Django's built-in permission system via `accounts.Role`.
- Staff are deactivated, never deleted, so historical records (who
  vaccinated an animal, who recorded a sale) remain intact.
- `apps/audit` automatically logs create/update/delete for every tracked
  model with user, timestamp, farm, and before/after values.

## Deliberately deferred (per Section 23 of the plan)

Advanced accounting, payroll, mobile app, AI assistant/forecasting, and
similar features are out of scope for V1 by design. The schema (Section
24–25) is ready for an AI layer to be added later without restructuring
the database — AI should call into `apps/dashboard/services.py`-style
deterministic functions rather than recomputing numbers itself.

## Running tests

```bash
python manage.py test
```

## Handover checklist

- [ ] Change the seeded `owner` / `vet_amit` passwords (or delete the seed
      users and create real ones)
- [ ] Point `DATABASE_URL` at your real Neon database and re-run `migrate`
- [ ] Configure `SUPABASE_*` if you want photos/documents off local disk
- [ ] Set `SECRET_KEY` to a real random value and `DEBUG=False` in production
- [ ] Set up a scheduled Neon/Postgres backup (Neon supports point-in-time
      restore natively; document your retention policy)
- [ ] Deploy via `docker compose up --build` (or any Docker host) behind
      HTTPS
