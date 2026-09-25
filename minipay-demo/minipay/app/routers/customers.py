from fastapi import APIRouter, Depends, HTTPException

from app.db import execute, fetch_all, fetch_one
from app.schemas import CustomerCreate
from app.security import require_api_key

router = APIRouter(dependencies=[Depends(require_api_key)])


@router.post("/api/customers", status_code=201)
def create_customer(payload: CustomerCreate):
    existing = fetch_one("SELECT id FROM customers WHERE customer_ref = %s", (payload.customer_ref,))
    if existing:
        raise HTTPException(status_code=409, detail="customer_ref already exists")

    row = execute(
        "INSERT INTO customers (customer_ref, name) VALUES (%s, %s) "
        "RETURNING id, customer_ref, name, created_at",
        (payload.customer_ref, payload.name),
        returning=True,
    )
    return row


@router.get("/api/customers/{customer_ref}/payments")
def list_customer_payments(customer_ref: str):
    customer = fetch_one("SELECT id FROM customers WHERE customer_ref = %s", (customer_ref,))
    if not customer:
        raise HTTPException(status_code=404, detail="customer not found")

    rows = fetch_all(
        "SELECT transaction_ref, amount, status, created_at, completed_at, failure_code "
        "FROM transactions WHERE customer_id = %s ORDER BY created_at DESC",
        (customer["id"],),
    )
    return rows
