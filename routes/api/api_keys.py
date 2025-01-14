import random
import string
from urllib.parse import unquote

import jwt
from starlette.requests import Request
from starlette.responses import RedirectResponse

from definitions.static import SECRET_KEY


async def admin_generate_api_key(request: Request):
    async with request.app.state.db_pool.acquire() as conn:
        async with conn.cursor() as cursor:
            token = jwt.decode(request.cookies.get("access_token"), SECRET_KEY, algorithms=["HS256"])

            user_id = token.get("user_id")
            api_key = ''.join(random.choices(string.ascii_letters + string.digits + string.punctuation, k=25))

            await cursor.execute("INSERT INTO api_keys(user_id, api_key) VALUES (%s, %s)", (user_id, api_key))

            return RedirectResponse("/admin/settings")


async def admin_delete_api_key(request: Request):
    async with request.app.state.db_pool.acquire() as conn:
        async with conn.cursor() as cursor:
            key = unquote(request.query_params.get("key"))

            await cursor.execute("DELETE FROM api_keys WHERE api_key = %s", (key,))

            return RedirectResponse("/admin/settings")
