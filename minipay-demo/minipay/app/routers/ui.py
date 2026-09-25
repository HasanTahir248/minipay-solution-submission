import random
import uuid
from datetime import datetime

from fastapi import APIRouter, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from app.config import settings
from app.db import execute, fetch_all, fetch_one

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


def _logged_in(request: Request) -> bool:
    return bool(request.session.get("user"))


@router.get("/login")
def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": None})


@router.post("/login")
def login_submit(request: Request, username: str = Form(...), password: str = Form(...)):
    if username == settings.LOGIN_USER and password == settings.LOGIN_PASS:
        request.session["user"] = username
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse(
        "login.html", {"request": request, "error": "Invalid username or password"}
    )


@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=303)


@router.get("/")
def dashboard(request: Request):
    if not _logged_in(request):
        return RedirectResponse(url="/login", status_code=303)
    recent = fetch_all(
        "SELECT transaction_ref, amount, status, created_at FROM transactions "
        "ORDER BY created_at DESC LIMIT 10"
    )
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "recent": recent, "result": None, "error": None, "query": ""},
    )


@router.get("/search")
def search(request: Request, ref: str = ""):
    if not _logged_in(request):
        return RedirectResponse(url="/login", status_code=303)

    result, error = None, None
    ref = ref.strip()
    if ref:
        rows = fetch_all(
            "SELECT transaction_ref, amount, status, created_at, completed_at, failure_code "
            "FROM transactions WHERE transaction_ref = %s ORDER BY created_at DESC",
            (ref,),
        )
        if not rows:
            error = f"No transaction found for reference '{ref}'."
        else:
            # NOTE: shown as a list on purpose -- a known duplicate ref (see
            # db/seed_small.sql / db/generate_data.py) will render more than
            # one row here rather than crashing. Contrast with the JSON API's
            # GET /api/payments/{ref}, which does NOT handle this (see
            # app/routers/payments.py -> INCIDENT-001).
            result = rows

    recent = fetch_all(
        "SELECT transaction_ref, amount, status, created_at FROM transactions "
        "ORDER BY created_at DESC LIMIT 10"
    )
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "recent": recent, "result": result, "error": error, "query": ref},
    )


@router.get("/payments/new")
def new_payment_form(request: Request):
    if not _logged_in(request):
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse("new_payment.html", {"request": request, "error": None, "success": None})


@router.post("/payments/new")
def new_payment_submit(request: Request, customer_ref: str = Form(...), amount: str = Form(...)):
    if not _logged_in(request):
        return RedirectResponse(url="/login", status_code=303)

    customer = fetch_one("SELECT id FROM customers WHERE customer_ref = %s", (customer_ref.strip(),))
    if not customer:
        # This is the built-in negative scenario for requirements/06-ui-automation.md
        return templates.TemplateResponse(
            "new_payment.html",
            {"request": request, "error": f"Unknown customer reference '{customer_ref}'.", "success": None},
        )

    try:
        amount_val = float(amount)
        if amount_val <= 0:
            raise ValueError
    except ValueError:
        return templates.TemplateResponse(
            "new_payment.html",
            {"request": request, "error": "Amount must be a positive number.", "success": None},
        )

    ref = f"TXN{uuid.uuid4().hex[:8].upper()}"
    created = datetime.utcnow()
    outcome = random.random()
    status_, failure_code = ("SUCCESS", None) if outcome < 0.85 else ("FAILED", "UPSTREAM_ERROR")

    row = execute(
        "INSERT INTO transactions "
        "(transaction_ref, customer_id, amount, status, created_at, completed_at, failure_code) "
        "VALUES (%s,%s,%s,%s,%s,%s,%s) RETURNING id, transaction_ref, status",
        (ref, customer["id"], amount_val, status_, created, created, failure_code),
        returning=True,
    )
    execute(
        "INSERT INTO callbacks (transaction_id, attempt_no, http_status, callback_status, attempted_at) "
        "VALUES (%s,%s,%s,%s,%s)",
        (row["id"], 1, 200 if status_ == "SUCCESS" else 502, "SUCCESS" if status_ == "SUCCESS" else "FAILED", created),
    )
    return templates.TemplateResponse("new_payment.html", {"request": request, "error": None, "success": row})
