import jwt

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import RedirectResponse

from constants.static import SECRET_KEY


class CheckAuthorized(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if not request.url.path.startswith("/admin") or request.url.path == "/admin/login":
            return await call_next(request)

        token = request.cookies.get("access_token")

        if not token:
            return RedirectResponse("/admin/login")

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            access_token = payload.get("access_token")

            if not access_token:
                return RedirectResponse("/admin/login")

        except jwt.ExpiredSignatureError:
            # Implement refreshing token later
            pass

        except jwt.InvalidTokenError:
            return RedirectResponse("/admin/login")

        return await call_next(request)
