from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.config import settings
from app.routers import customers, health, payments, ui

app = FastAPI(title="MiniPay", version="1.0.0")
app.add_middleware(SessionMiddleware, secret_key=settings.SESSION_SECRET)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(health.router)
app.include_router(customers.router)
app.include_router(payments.router)
app.include_router(ui.router)
