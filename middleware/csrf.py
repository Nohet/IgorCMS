import secrets

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import PlainTextResponse
from urllib.parse import parse_qs

SAFE_METHODS = {"GET", "HEAD", "OPTIONS", "TRACE"}


class CSRFMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if "csrf_token" not in request.session:
            request.session["csrf_token"] = secrets.token_urlsafe(128)

        response = await call_next(request)
        return response


class VerifyCSRFTokenMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.method in SAFE_METHODS:
            return await call_next(request)

        cookie_csrf_token = request.session.get("csrf_token")

        body = await request.body()
        content_type = request.headers.get("content-type", "")

        form_csrf_token = None
        if content_type.startswith("application/x-www-form-urlencoded"):
            parsed = parse_qs(body.decode("utf-8"))
            vals = parsed.get("csrf_token")
            form_csrf_token = vals[0] if vals else None

        header_csrf_token = request.headers.get("X-CSRF-Token")
        candidate = form_csrf_token or header_csrf_token

        if not candidate or candidate != cookie_csrf_token:
            return PlainTextResponse("CSRF validation failed!", status_code=403)

        async def receive():
            return {"type": "http.request", "body": body, "more_body": False}

        new_request = Request(request.scope, receive)
        return await call_next(new_request)
