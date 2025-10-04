from starlette.requests import Request
from starlette.responses import RedirectResponse

from utils.jwt_tokens import create_access_token
from constants.static import templates


async def logout(_: Request):
    response = RedirectResponse("/admin/login")

    try:
        response.delete_cookie(key="access_token", httponly=True)
    except Exception as e:
        print(e)

    return response


async def admin_login(request: Request):

    if request.method == "POST":
        form_data = await request.form()

        email = form_data.get("email")
        password = form_data.get("pass")

        user_info = await request.app.state.crud.auth.login(email, password)

        if not user_info:
            return templates.TemplateResponse("admin/login.html", {"request": request, "message": [
                "Password or email is invalid!"]})

        jwt_token = create_access_token({
            "access_token": user_info["password_hash"],
            "user_id": user_info["user_id"],
            "firstname": user_info["firstname"],
            "lastname": user_info["lastname"],
            "permissions": user_info["permissions"],
        })

        res = RedirectResponse("/admin/homepage")
        res.set_cookie("access_token", jwt_token, expires=7200, httponly=True)

        return res

    return templates.TemplateResponse("admin/login.html", {"request": request})
