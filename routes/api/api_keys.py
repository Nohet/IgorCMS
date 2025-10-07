import secrets

import jwt
from starlette.requests import Request
from starlette.responses import RedirectResponse

from constants.static import SECRET_KEY
from enums.permissions import Permissions


async def admin_generate_api_key(request: Request):
    token_value = request.cookies.get("access_token")

    if not token_value:
        return RedirectResponse("/admin/settings", status_code=303)

    try:
        token = jwt.decode(token_value, SECRET_KEY, algorithms=["HS256"])
    except jwt.InvalidTokenError:
        response = RedirectResponse("/admin/login")
        response.delete_cookie("access_token", httponly=True)
        return response

    if token.get("permissions") != Permissions.ADMINISTRATOR:
        return RedirectResponse("/admin/settings", status_code=303)

    user_id = token.get("user_id")
    if not user_id:
        return RedirectResponse("/admin/settings", status_code=303)

    await request.form()

    api_key = secrets.token_urlsafe(32)
    await request.app.state.crud.settings.create_api_key(user_id, api_key)

    return RedirectResponse("/admin/settings", status_code=303)


async def admin_delete_api_key(request: Request):
    form_data = await request.form()
    api_key = form_data.get("api_key")

    if not api_key:
        return RedirectResponse("/admin/settings", status_code=303)

    await request.app.state.crud.settings.delete_api_key(api_key)
    return RedirectResponse("/admin/settings", status_code=303)
