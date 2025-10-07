from starlette.requests import Request
from starlette.responses import RedirectResponse

from constants.static import templates
from factories.user_factory import get_user
from models.user import UserJWT
from utils.dependency_injection import dependency_injection
from utils.text_utils import sanitize_text


@dependency_injection(get_user)
async def admin_edit_page(request: Request, user: UserJWT):
    messages = []
    page_id = int(request.query_params.get("id"))

    form_data = await request.form()

    if form_data:
        title = form_data.get("title")
        page_content = form_data.get("page_content")
        navbar_title = form_data.get("navbar_title")
        meta_title = form_data.get("meta_title")
        meta_description = form_data.get("meta_description")
        meta_keywords = form_data.get("meta_keywords")
        redirect_url = form_data.get("redirect_url")
        language = form_data.get("language")
        display = form_data.get("display")
        meta_robots = form_data.get("meta_robots")
        category = int(form_data.get("category")) if form_data.get("category") and form_data.get("category").isdigit() else None
        show_in_menu = int(form_data.get("show_in_menu"))
        site_icon = form_data.get("site_icon")

        await request.app.state.crud.pages.admin_update(
            page_id,
            title=title,
            slug=sanitize_text(title),
            content=page_content,
            navbar_title=navbar_title,
            meta_title=meta_title,
            meta_description=meta_description,
            meta_keywords=meta_keywords,
            redirect_url=redirect_url,
            language=language,
            display=display,
            meta_robots=meta_robots,
            category_id=category,
            show_in_menu=show_in_menu,
            image=site_icon
        )

        messages.append("Successfully saved changes!")

    categories = await request.app.state.crud.categories.list_all_basic()
    page_data = await request.app.state.crud.pages.admin_get_details(page_id)

    return templates.TemplateResponse("admin/pages/edit/edit_page.html", {"request": request,
                                                                        "categories": categories,
                                                                        "data": page_data,
                                                                        "messages": messages,
                                                                        "firstname": getattr(user, "firstname", ""),
                                                                        "lastname": getattr(user, "lastname", ""),
                                                                        "permissions": getattr(user, "permissions", "")})


async def admin_delete_page(request: Request):
    form_data = await request.form()
    page_id = form_data.get('page_id')

    if not page_id or not str(page_id).isdigit() or int(page_id) == 1:
        return RedirectResponse('/admin/pages/view', status_code=303)

    await request.app.state.crud.pages.delete(int(page_id))
    return RedirectResponse('/admin/pages/view', status_code=303)


@dependency_injection(get_user)
async def admin_show_pages(request: Request, user: UserJWT):

    pages = await request.app.state.crud.pages.admin_list_pages()

    return templates.TemplateResponse("admin/pages/view/show_pages.html", {"request": request,
                                                                         "pages": pages,
                                                                         "firstname": getattr(user, "firstname", ""),
                                                                         "lastname": getattr(user, "lastname", ""),
                                                                         "permissions": getattr(user, "permissions", "")})


@dependency_injection(get_user)
async def admin_add_page(request: Request, user: UserJWT):
    messages = []

    form_data = await request.form()

    if form_data:
        title = form_data.get("title")
        icon = form_data.get("icon")
        page_content = form_data.get("page_content")
        navbar_title = form_data.get("navbar_title")
        meta_title = form_data.get("meta_title")
        meta_description = form_data.get("meta_description")
        meta_keywords = form_data.get("meta_keywords")
        redirect_url = form_data.get("redirect_url")
        display = form_data.get("display")
        meta_robots = form_data.get("meta_robots")
        language = form_data.get("language")
        category = int(form_data.get("category")) if form_data.get("category") and form_data.get("category").isdigit() else None
        show_in_menu = int(form_data.get("show_in_menu"))

        await request.app.state.crud.pages.admin_create(
            slug=sanitize_text(title), image=icon, title=title, content=page_content, display=display,
            author_id=getattr(user, "user_id", None), navbar_title=navbar_title, meta_title=meta_title,
            meta_description=meta_description, meta_keywords=meta_keywords, meta_robots=meta_robots,
            language=language, redirect_url=redirect_url, show_in_menu=show_in_menu, category_id=category
        )
        messages.append("Successfully added a new page!")

    categories = await request.app.state.crud.categories.list_all_basic()

    return templates.TemplateResponse("admin/pages/add/add_page.html", {"request": request,
                                                                      "categories": categories,
                                                                      "messages": messages,
                                                                      "firstname": getattr(user, "firstname", ""),
                                                                      "lastname": getattr(user, "lastname", ""),
                                                                      "permissions": getattr(user, "permissions", "")})
