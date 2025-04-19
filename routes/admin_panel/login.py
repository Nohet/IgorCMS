import bcrypt

from starlette.requests import Request
from starlette.responses import RedirectResponse

from utils.jwt_tokens import create_access_token
from definitions.static import templates


async def logout(_: Request):
    response = RedirectResponse("/admin/login")

    try:
        response.delete_cookie(key="access_token", httponly=True)
    except Exception as e:
        print(e)

    return response


async def admin_login(request: Request):
    form_data = await request.form()

    if form_data.get("email") and form_data.get("pass"):
        try:
            async with request.app.state.db_pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(
                        "SELECT password_hash, id, firstname, lastname, permissions from users WHERE email = %s",
                        (form_data.get("email"),))
                    row = await cursor.fetchone()

            password_hash = row[0]
            user_id = row[1]
            firstname = row[2]
            lastname = row[3]
            permissions = row[4]

            if bcrypt.checkpw(bytes(form_data.get("pass").encode("utf-8")), bytes(password_hash.encode("utf-8"))):
                jwt_token = create_access_token(
                    {"access_token": password_hash, "user_id": user_id, "firstname": firstname,
                     "lastname": lastname, "permissions": permissions})

                res = RedirectResponse("/admin/homepage")
                res.set_cookie("access_token", jwt_token, expires=7200, httponly=True)

                return res

            else:
                return templates.TemplateResponse("admin/login.html", {"request": request, "message": [
                    "Password or email is invalid!"]})

        except Exception as e:
            print(e)
            return templates.TemplateResponse("admin/login.html", {"request": request, "message": [
                "Something went wrong! Maybe this email address does not exist in the database."]})

    return templates.TemplateResponse(request, "admin/login.html")
