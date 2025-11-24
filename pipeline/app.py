from fastapi import FastAPI
from routers import english, finnish

app = FastAPI(
    title="User and forest data interface",
)

app.include_router(english.router)
app.include_router(finnish.router)