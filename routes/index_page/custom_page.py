from starlette.requests import Request
from starlette.responses import RedirectResponse
from constants.static import templates


async def custom_page(request: Request):
    slug = request.path_params['slug']

    if slug in ["admin", "post", "static"]:
        return None

    page_info = await request.app.state.crud.pages.get_by_slug(slug)

    if not page_info:
        return RedirectResponse("/")

    if page_info[8]:
        return RedirectResponse(page_info[8])

    index_info = await request.app.state.crud.pages.get_index_navbar_title()
    pages = await request.app.state.crud.pages.get_menu_pages()

    pages_center = [p for p in pages if p[3] == 'center']
    pages_right = [p for p in pages if p[3] == 'right']

    return templates.TemplateResponse("index/custom_page.html", {"request": request,
                                                                 "index_info": index_info,
                                                                 "page_info": page_info,
                                                                 "pages_center": pages_center,
                                                                 "pages_right": pages_right, })
