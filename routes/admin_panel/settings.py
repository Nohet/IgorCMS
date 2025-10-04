import urllib.parse

import bcrypt

from starlette.requests import Request
from starlette.responses import RedirectResponse
from constants.static import API_UPLOAD_KEY, templates
from factories.user_factory import get_user
from utils.dependency_injection import dependency_injection
from enums.permissions import Permissions


@dependency_injection(get_user)
async def admin_settings(request: Request, user):
    messages = []

    form_data = await request.form()

    if form_data and form_data.get("form_type") == "general_settings" and getattr(user, "permissions", None) == Permissions.ADMINISTRATOR:
        site_name = form_data.get("site_name")
        site_icon = form_data.get("site_icon")
        meta_title = form_data.get("meta_title")
        meta_desc = form_data.get("meta_desc")
        meta_keywords = form_data.get("meta_keywords")
        meta_robots = form_data.get("meta_robots")
        site_language = form_data.get("site_language")

        await request.app.state.crud.settings.update_general_settings(
            site_name=site_name, site_icon=site_icon, meta_title=meta_title, meta_desc=meta_desc,
            meta_keywords=meta_keywords, meta_robots=meta_robots, site_language=site_language
        )

        messages.append("Successfully saved changes!")

    elif form_data.get("form_type") == "password_settings":
        old_pass = form_data.get("old_pass")
        new_pass = form_data.get("new_pass")

        if user and bcrypt.checkpw(bytes(old_pass.encode("utf-8")), bytes(user.access_token.encode("utf-8"))):
            await request.app.state.crud.users.update_password_if_old_matches(user.user_id, user.access_token, new_pass)

            return RedirectResponse("/admin/logout")

    index_page = await request.app.state.crud.settings.get_index_page_basic()
    api_keys = await request.app.state.crud.settings.list_api_keys(getattr(user, "user_id", None))

    return templates.TemplateResponse("admin/settings/settings.html", {"request": request,
                                                                       "messages": messages,
                                                                       "api_keys": api_keys,
                                                                       "quote_plus": urllib.parse.quote_plus,
                                                                       "index_page": index_page,
                                                                       "firstname": getattr(user, "firstname", ""),
                                                                       "lastname": getattr(user, "lastname", ""),
                                                                       "permissions": getattr(user, "permissions", "")})
