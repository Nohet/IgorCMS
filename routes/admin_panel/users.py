
import bcrypt

import jwt
from starlette.requests import Request
from starlette.responses import RedirectResponse

from definitions.static import SECRET_KEY, templates


async def admin_delete_user(request: Request):
    async with request.app.state.db_pool.acquire() as conn:
        async with conn.cursor() as cursor:
            user_id = request.query_params.get("id")

            await cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))

            return RedirectResponse("/admin/users/view")


async def admin_users_view(request: Request):
    async with request.app.state.db_pool.acquire() as conn:
        async with conn.cursor() as cursor:
            token = jwt.decode(request.cookies.get("access_token"), SECRET_KEY, algorithms=["HS256"])

            await cursor.execute("""SELECT users.firstname, users.lastname, users.email, permissions, COUNT(posts.id), users.id
                            FROM users
                            LEFT JOIN posts 
                            ON posts.author_id = users.id
                            GROUP BY users.id;
    """)

            users = await cursor.fetchall()
            permissions_to_text = {3: "Administrator", 2: "Autor"}

            return templates.TemplateResponse("admin/users/view/admin_show_users.html", {"request": request,
                                                                                         "permissions_to_text": permissions_to_text,
                                                                                         "users": users,
                                                                                         "firstname": token.get(
                                                                                             "firstname"),
                                                                                         "lastname": token.get(
                                                                                             "lastname"),
                                                                                         "permissions": token.get(
                                                                                             "permissions")})


async def admin_users_add(request: Request):
    token = jwt.decode(request.cookies.get("access_token"), SECRET_KEY, algorithms=["HS256"])
    messages = []

    form_data = await request.form()

    if form_data:
        async with request.app.state.db_pool.acquire() as conn:
            async with conn.cursor() as cursor:
                first_name = form_data.get("firstname")
                last_name = form_data.get("lastname")
                email = form_data.get("email")
                password = form_data.get("pass")
                permissions = form_data.get("permissions")

                await cursor.execute(
                    "INSERT INTO USERS(firstname, lastname, email, password_hash, permissions) VALUES(%s, "
                    "%s, %s, %s, %s)",
                    (first_name, last_name, email,
                     bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8"),
                     int(permissions)))
                messages.append("Successfully added a new user!")

    return templates.TemplateResponse("admin/users/add/admin_add_user.html", {"request": request,
                                                                              "messages": messages,
                                                                              "firstname": token.get("firstname"),
                                                                              "lastname": token.get("lastname"),
                                                                              "permissions": token.get("permissions")})
