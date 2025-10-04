import random
import string
from urllib.parse import unquote

import jwt
from starlette.requests import Request
from starlette.responses import RedirectResponse

from constants.static import SECRET_KEY


async def admin_generate_api_key(request: Request):
    token = jwt.decode(request.cookies.get("access_token"), SECRET_KEY, algorithms=["HS256"])

    user_id = token.get("user_id")
    api_key = ''.join(random.choices(string.ascii_letters + string.digits + string.punctuation, k=25))

    await request.app.state.crud.settings.create_api_key(user_id, api_key)

    return RedirectResponse("/admin/settings")


async def admin_delete_api_key(request: Request):
    key = unquote(request.query_params.get("key"))
    await request.app.state.crud.settings.delete_api_key(key)
    return RedirectResponse("/admin/settings")
