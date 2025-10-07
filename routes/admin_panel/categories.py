from starlette.requests import Request
from starlette.responses import RedirectResponse

from constants.static import templates
from factories.user_factory import get_user
from models.user import UserJWT
from utils.dependency_injection import dependency_injection


@dependency_injection(get_user)
async def admin_edit_category(request: Request, user: UserJWT):
    messages = []
    category_id = int(request.query_params.get("id"))

    form_data = await request.form()

    if form_data:
        name = form_data.get("name")
        description = form_data.get("description")
        parent_id = int(form_data.get("parent_id")) if form_data.get("parent_id") and form_data.get("parent_id").isdigit() else None

        await request.app.state.crud.categories.update(category_id, name, description, parent_id)
        messages.append("Successfully saved changes!")

    categories = await request.app.state.crud.categories.list_all_basic()
    data = await request.app.state.crud.categories.get_details(category_id)

    return templates.TemplateResponse("admin/categories/edit/edit_category.html", {"request": request,
                                                                                 "data": data,
                                                                                 "messages": messages,
                                                                                 "categories": categories,
                                                                                 "firstname": getattr(user, "firstname", ""),
                                                                                 "lastname": getattr(user, "lastname", ""),
                                                                                 "permissions": getattr(user, "permissions", "")})


async def admin_delete_category(request: Request):
    form_data = await request.form()
    category_id = form_data.get('category_id')

    if not category_id or not str(category_id).isdigit():
        return RedirectResponse('/admin/categories/view', status_code=303)

    await request.app.state.crud.categories.delete(int(category_id))
    return RedirectResponse('/admin/categories/view', status_code=303)


@dependency_injection(get_user)
async def admin_add_category(request: Request, user: UserJWT):
    messages = []
    form_data = await request.form()

    if form_data:
        name = form_data.get("name")
        description = form_data.get("description")
        parent_id = int(form_data.get("parent_id")) if form_data.get("parent_id") and form_data.get("parent_id").isdigit() else None

        await request.app.state.crud.categories.create(name, description, parent_id)
        messages.append("Successfully added a new category!")

    categories = await request.app.state.crud.categories.list_all_basic()

    return templates.TemplateResponse("admin/categories/add/add_category.html", {"request": request,
                                                                                "messages": messages,
                                                                                "categories": categories,
                                                                                "firstname": getattr(user, "firstname", ""),
                                                                                "lastname": getattr(user, "lastname", ""),
                                                                                "permissions": getattr(user, "permissions", "")})


@dependency_injection(get_user)
async def admin_view_categories(request: Request, user: UserJWT):

    categories = await request.app.state.crud.categories.list_all_full()

    return templates.TemplateResponse("admin/categories/view/view_categories.html", {"request": request,
                                                                                     "categories": categories,
                                                                                     "firstname": getattr(user, "firstname", ""),
                                                                                     "lastname": getattr(user, "lastname", ""),
                                                                                     "permissions": getattr(user, "permissions", "")})
