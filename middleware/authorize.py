import jwt

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import RedirectResponse

from constants.static import SECRET_KEY


class CheckAuthorized(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        normalized_path = request.url.path.rstrip("/")
        if not normalized_path:
            normalized_path = "/"

        if not normalized_path.startswith("/admin") or normalized_path == "/admin/login":
            return await call_next(request)

        redirect_to_dashboard = normalized_path == "/admin"

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

        if redirect_to_dashboard:
            return RedirectResponse("/admin/homepage")

        return await call_next(request)
