from itertools import islice

from starlette.requests import Request

from utils.text_utils import sanitize_text
from constants.static import templates


async def index_page(request: Request):
    index_page_info = await request.app.state.crud.pages.get_index_page_for_index()

    posts = await request.app.state.crud.posts.list_published_for_index()
    pages = await request.app.state.crud.pages.get_menu_pages()

    pages_center = [p for p in pages if p[3] == 'center']
    pages_right = [p for p in pages if p[3] == 'right']

    iterator = iter(posts)
    posts = list(iter(lambda: list(islice(iterator, 5)), []))

    return templates.TemplateResponse("index/index.html", {"request": request,
                                                           "sanitize_text": sanitize_text,
                                                           "posts": posts,
                                                           "pages_center": pages_center,
                                                           "pages_right": pages_right,
                                                           "info": index_page_info})
