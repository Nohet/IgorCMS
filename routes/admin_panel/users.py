from starlette.requests import Request
from starlette.responses import RedirectResponse

from constants.static import templates
from factories.user_factory import get_user
from models.user import UserJWT
from utils.dependency_injection import dependency_injection


async def admin_delete_user(request: Request):
    user_id = int(request.query_params.get("id"))
    await request.app.state.crud.users.delete(user_id)
    return RedirectResponse("/admin/users/view")


@dependency_injection(get_user)
async def admin_users_view(request: Request, user: UserJWT):

    users = await request.app.state.crud.users.admin_list_users()
    permissions_to_text = {3: "Administrator", 2: "Autor"}

    return templates.TemplateResponse("admin/users/view/admin_show_users.html", {"request": request,
                                                                                 "permissions_to_text": permissions_to_text,
                                                                                 "users": users,
                                                                                 "firstname": getattr(user, "firstname", ""),
                                                                                 "lastname": getattr(user, "lastname", ""),
                                                                                 "permissions": getattr(user, "permissions", "")})


@dependency_injection(get_user)
async def admin_users_add(request: Request, user: UserJWT):
    messages = []

    form_data = await request.form()

    if form_data:
        first_name = form_data.get("firstname")
        last_name = form_data.get("lastname")
        email = form_data.get("email")
        password = form_data.get("pass")
        permissions = form_data.get("permissions")

        await request.app.state.crud.users.create(first_name, last_name, email, password, int(permissions))
        messages.append("Successfully added a new user!")

    return templates.TemplateResponse("admin/users/add/admin_add_user.html", {"request": request,
                                                                            "messages": messages,
                                                                            "firstname": getattr(user, "firstname", ""),
                                                                            "lastname": getattr(user, "lastname", ""),
                                                                            "permissions": getattr(user, "permissions", "")})
