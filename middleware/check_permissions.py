import jwt
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import RedirectResponse

from definitions.static import SECRET_KEY


class CheckPermissions(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if not request.url.path.startswith("/admin") or request.url.path == "/admin/login":
            return await call_next(request)

        try:
            token = jwt.decode(request.cookies.get("access_token"), SECRET_KEY, algorithms=["HS256"])

            if token.get("permissions") == 2 and any(i in request.url.path for i in ["categories", "pages", "users"]):
                return RedirectResponse("/admin/homepage")

        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            return RedirectResponse("/admin/login")

        return await call_next(request)
