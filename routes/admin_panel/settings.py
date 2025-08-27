import urllib.parse

import bcrypt
import jwt

from starlette.requests import Request
from starlette.responses import RedirectResponse
from constants.static import SECRET_KEY, API_UPLOAD_KEY, templates


async def admin_settings(request: Request):
    messages = []

    async with request.app.state.db_pool.acquire() as conn:
        async with conn.cursor() as cursor:
            token = jwt.decode(request.cookies.get("access_token"), SECRET_KEY, algorithms=["HS256"])

            form_data = await request.form()

            if form_data and form_data.get("form_type") == "general_settings" and token.get("permissions") == 3:
                site_name = form_data.get("site_name")
                site_icon = form_data.get("site_icon")
                meta_title = form_data.get("meta_title")
                meta_desc = form_data.get("meta_desc")
                meta_keywords = form_data.get("meta_keywords")
                meta_robots = form_data.get("meta_robots")
                site_language = form_data.get("site_language")

                await cursor.execute("""UPDATE pages 
                set title = %s, image = %s, meta_title = %s,
                meta_description = %s, meta_keywords = %s,
                meta_robots = %s, language = %s,
                updated_at = CURRENT_TIMESTAMP() WHERE id = 1;""", (site_name, site_icon, meta_title, meta_desc,
                                                                    meta_keywords, meta_robots, site_language))

                messages.append("Successfully saved changes!")

            elif form_data.get("form_type") == "password_settings":
                old_pass = form_data.get("old_pass")
                new_pass = form_data.get("new_pass")

                if bcrypt.checkpw(bytes(old_pass.encode("utf-8")), bytes(token.get("access_token").encode("utf-8"))):
                    await cursor.execute("UPDATE users SET password_hash = %s WHERE password_hash = %s and id = %s",
                                         (bcrypt.hashpw(new_pass.encode("utf-8"), bcrypt.gensalt()).decode("utf-8"),
                                          token.get("access_token"), token.get("user_id")))

                    return RedirectResponse("/admin/logout")

            await cursor.execute("""SELECT title, image, meta_title, meta_description, meta_keywords, language
                                FROM `pages`""")
            index_page = await cursor.fetchone()

            await cursor.execute("SELECT api_key FROM api_keys WHERE user_id = %s", (token.get("user_id")))
            api_keys = await cursor.fetchall()

            return templates.TemplateResponse("admin/settings/settings.html", {"request": request,
                                                                               "messages": messages,
                                                                               "api_keys": api_keys,
                                                                               "quote_plus": urllib.parse.quote_plus,
                                                                               "API_UPLOAD_KEY": API_UPLOAD_KEY,
                                                                               "index_page": index_page,
                                                                               "firstname": token.get(
                                                                                   "firstname"),
                                                                               "lastname": token.get(
                                                                                   "lastname"),
                                                                               "permissions": token.get(
                                                                                   "permissions")})
