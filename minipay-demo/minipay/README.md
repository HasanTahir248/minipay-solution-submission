# MiniPay (demo app)

A minimal payment-processing app — web UI + REST API + PostgreSQL — built to
satisfy `requirements/05-web-services-api-tests.md` and
`requirements/06-ui-automation.md` from the Paysys L2 assessment, and to give
you real data/behaviour to point the SQL, Python CLI, Kubernetes and incident
investigation work at.

It is a starting point, not the finished submission — you're expected to
extend, harden, and explain it (per `INSTRUCTIONS.md` §6 and §7).

## Quick start

```bash
cp .env.example .env      # only needed if you run api.py outside docker-compose
docker compose up --build
```

- UI: http://localhost:8080/login (admin / admin123)
- API docs (Swagger): http://localhost:8080/docs
- Health: http://localhost:8080/health

The `db` service auto-loads `db/schema.sql` then `db/seed_small.sql` on first
boot (via Postgres's `docker-entrypoint-initdb.d`). To reset, `docker compose
down -v` and `up` again.

## API

All `/api/*` routes require header `X-API-Key: demo-api-key` (see `.env` / `docker-compose.yml`).

```
POST /api/customers                        {"customer_ref": "CUST000009", "name": "Jane Doe"}
POST /api/payments                         {"customer_ref": "CUST000001", "amount": 250.00}
GET  /api/payments/{transaction_ref}
GET  /api/customers/{customer_ref}/payments
GET  /health                               (no auth required)
```

Example:

```bash
curl -s -X POST localhost:8080/api/payments \
  -H "X-API-Key: demo-api-key" -H "Content-Type: application/json" \
  -d '{"customer_ref":"CUST000001","amount":99.50}'
```

## Generating the ~50k-row dataset for INCIDENT-003

```bash
cd db
python3 generate_data.py > seed_large.sql
# then either mount seed_large.sql in place of seed_small.sql and recreate
# the db container, or: docker compose exec -T db psql -U minipay -d minipay < seed_large.sql
```

## Two things left in here on purpose — read before you "fix" them

1. **`app/routers/payments.py` — `GET /api/payments/{ref}`** has an
   intentionally unguarded `assert len(rows) == 1`. `transaction_ref` is not
   unique in `schema.sql`, and `db/generate_data.py` / `db/seed_small.sql`
   both seed duplicate refs on purpose. Searching a duplicate or nonexistent
   ref currently throws an unhandled 500 instead of a clean 200/404 — that's
   **INCIDENT-001**, wired up for you to reproduce, diagnose and fix as part
   of `investigation/INCIDENT-001-RCA.md`. Don't fix it before you've written
   the RCA — that's the actual assessment.
2. **`db/schema.sql` has minimal indexing on purpose** (per the assessment).
   Once you've loaded the 50k-row dataset, that's your material for
   **INCIDENT-003** and the SQL performance requirement — find the slow
   access pattern yourself and document before/after in
   `investigation/INCIDENT-003-RCA.md` / `sql/PERFORMANCE.md`.

## Layout

```
app/
  main.py           FastAPI app + router wiring
  config.py          env-based settings
  db.py               psycopg2 connection pool + query helpers
  security.py          API key auth dependency
  schemas.py            pydantic request models
  routers/
    health.py    customers.py    payments.py    ui.py
  templates/      Jinja2 HTML (data-testid attrs throughout, for Playwright/Selenium)
  static/style.css
db/
  schema.sql            (copied verbatim from the assessment repo)
  generate_data.py      (copied verbatim from the assessment repo)
  seed_small.sql        hand-written small seed for fast local dev
```

## Suggested placement in your submission repo

Drop this whole folder in as `app/` (or `src/`) alongside the required
top-level `sql/`, `kubernetes/`, `python/`, `tests/api/`, `tests/ui/`,
`investigation/`, `evidence/` folders from `INSTRUCTIONS.md`.
