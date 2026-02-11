"""FastAPI application entrypoint with secure defaults."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.core.config import get_settings
from app.core.security import get_rate_limit_key
from app.db.base import Base
from app.db.session import engine
from app.routes.user import router as user_router

settings = get_settings()

app = FastAPI(title=settings.app_name)

# Global rate limiter for all public endpoints.
limiter = Limiter(key_func=get_rate_limit_key, default_limits=[settings.default_rate_limit])
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)


@app.exception_handler(RateLimitExceeded)
def rate_limit_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    del exc
    retry_after = request.scope.get("view_rate_limit", (None, None))[1]
    return JSONResponse(
        status_code=429,
        content={
            "detail": "Rate limit exceeded. Please retry later.",
            "status_code": 429,
        },
        headers={"Retry-After": str(retry_after) if retry_after else "60"},
    )


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)


@app.get("/")
async def read_root() -> dict[str, str]:
    return {"message": "Hello, FastAPI"}


app.include_router(user_router)
