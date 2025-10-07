import json

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from enums.permissions import Permissions
from utils.responses import response_message


class CheckAuthorizedApi(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if not request.url.path.startswith("/api/v1"):
            return await call_next(request)

        crud = getattr(request.app.state, "crud", None)
        settings_crud = getattr(crud, "settings", None) if crud else None

        if settings_crud is None:
            return response_message("error", "API is not available while the database is offline.", code=503)

        api_key = request.headers.get("X-API-Key") or request.query_params.get("api_key")
        body = None

        if not api_key and request.method not in {"GET", "DELETE"}:
            body = await request.body()
            scope = request.scope
            payload = {}
            if body:
                try:
                    payload = json.loads(body)
                except json.JSONDecodeError:
                    payload = {}
            api_key = payload.get("api_key")

            if body is not None:
                async def receive():
                    return {"type": "http.request", "body": body, "more_body": False}

                request = Request(scope, receive)
                request._body = body

        if not api_key:
            return response_message("error", "The API key that you provided is either invalid or you did not provide the key at all!", code=401)

        permissions_value = await settings_crud.fetch_api_key_permissions(api_key)

        if permissions_value is None:
            return response_message("error", "The API key that you provided is invalid!", code=401)

        if permissions_value == int(Permissions.AUTHOR) and (
                any(segment in request.url.path for segment in ["categories", "pages"]) or
                request.method == "DELETE"
        ):
            return response_message("error", "You do not have permissions to use this endpoint!", code=403)

        request.state.api_permissions = permissions_value

        return await call_next(request)
