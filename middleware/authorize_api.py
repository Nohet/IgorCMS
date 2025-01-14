from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from utils.responses import response_message


class CheckAuthorizedApi(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if not request.url.path.startswith("/api/v1"):
            response = await call_next(request)
            return response

        if not await request.body():
            return response_message("error",
                                    "The api key that you provided is either invalid or you didn't provide the key at all!")

        json_data = await request.json()
        api_key = json_data.get("api_key")

        async with request.app.state.db_pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("""
                SELECT permissions FROM api_keys 
                INNER JOIN users ON api_keys.user_id = users.id
                WHERE api_key = %s
                """, (api_key,))
                permissions = await cursor.fetchone()

                if not permissions:
                    return response_message("error", "The api key that you provided is invalid!")

                if permissions[0] == 2 and (
                        any(i in request.url.path for i in ["categories", "pages"]) or
                        request.method == "DELETE"
                ):
                    return response_message("error", "You do not have permissions to use this endpoint!")

        response = await call_next(request)
        return response
