import random
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException

from app.db import execute, fetch_all, fetch_one
from app.schemas import PaymentCreate
from app.security import require_api_key

router = APIRouter(dependencies=[Depends(require_api_key)])


@router.post("/api/payments", status_code=201)
def create_payment(payload: PaymentCreate):
    customer = fetch_one("SELECT id FROM customers WHERE customer_ref = %s", (payload.customer_ref,))
    if not customer:
        raise HTTPException(status_code=404, detail="customer not found")

    ref = payload.transaction_ref or f"TXN{uuid.uuid4().hex[:8].upper()}"

    # Idempotency: if a client resubmits the same transaction_ref (e.g. after
    # a timed-out response), return the existing record instead of creating
    # a second one. This is what requirements/05's "duplicate/idempotent
    # payment submission" test should exercise.
    existing = fetch_one(
        "SELECT id, transaction_ref, customer_id, amount, status, created_at, completed_at, failure_code "
        "FROM transactions WHERE transaction_ref = %s",
        (ref,),
    )
    if existing:
        return existing

    created = datetime.utcnow()
    outcome = random.random()
    if outcome < 0.85:
        status_, failure_code = "SUCCESS", None
    else:
        status_, failure_code = "FAILED", "UPSTREAM_ERROR"
    completed = created

    row = execute(
        "INSERT INTO transactions "
        "(transaction_ref, customer_id, amount, status, created_at, completed_at, failure_code) "
        "VALUES (%s,%s,%s,%s,%s,%s,%s) "
        "RETURNING id, transaction_ref, customer_id, amount, status, created_at, completed_at, failure_code",
        (ref, customer["id"], str(payload.amount), status_, created, completed, failure_code),
        returning=True,
    )
    execute(
        "INSERT INTO callbacks (transaction_id, attempt_no, http_status, callback_status, attempted_at) "
        "VALUES (%s,%s,%s,%s,%s)",
        (
            row["id"],
            1,
            200 if status_ == "SUCCESS" else 502,
            "SUCCESS" if status_ == "SUCCESS" else "FAILED",
            created,
        ),
    )
    return row


@router.get("/api/payments/{ref}")
def get_payment(ref: str):
    rows = fetch_all(
        "SELECT id, transaction_ref, customer_id, amount, status, created_at, completed_at, failure_code "
        "FROM transactions WHERE transaction_ref = %s",
        (ref,),
    )

    # --- INTENTIONALLY INJECTED DEFECT -- see incidents/INCIDENT-001 ---
    # This assumes transaction_ref is unique. It is NOT enforced in
    # schema.sql, and db/generate_data.py deliberately seeds some duplicate
    # refs (and db/seed_small.sql seeds one too, on purpose). A ref with 0
    # matches (typo/unknown ref) or 2+ matches (duplicate) blows up here
    # with an unhandled AssertionError -> 500, while a ref with exactly one
    # match works fine. That's the "some transaction IDs work while others
    # fail" behaviour in INCIDENT-001. Left in place deliberately for you to
    # reproduce, diagnose, and fix as part of your investigation writeup --
    # do not "accidentally" fix this before you've written the RCA.
    assert len(rows) == 1, f"expected exactly one transaction for ref={ref!r}, found {len(rows)}"
    row = rows[0]
    # --- END INJECTED DEFECT ---

    callbacks = fetch_all(
        "SELECT attempt_no, http_status, callback_status, attempted_at FROM callbacks "
        "WHERE transaction_id = %s ORDER BY attempt_no",
        (row["id"],),
    )
    row = dict(row)
    row["callbacks"] = callbacks
    return row
