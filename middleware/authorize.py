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
            response = RedirectResponse("/admin/login")
            response.delete_cookie("access_token", httponly=True)
            return response

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            response = RedirectResponse("/admin/login")
            response.delete_cookie("access_token", httponly=True)
            return response

        access_token = payload.get("access_token")
        user_id = payload.get("user_id")

        if not access_token or not user_id:
            response = RedirectResponse("/admin/login")
            response.delete_cookie("access_token", httponly=True)
            return response

        crud = getattr(request.app.state, "crud", None)
        auth_crud = getattr(crud, "auth", None) if crud else None

        if not auth_crud:
            response = RedirectResponse("/admin/login")
            response.delete_cookie("access_token", httponly=True)
            return response

        is_valid = await auth_crud.validate_access_token(user_id, access_token)
        if not is_valid:
            response = RedirectResponse("/admin/login")
            response.delete_cookie("access_token", httponly=True)
            return response

        return await call_next(request)
