from starlette.requests import Request
from starlette.responses import RedirectResponse
from constants.static import templates


async def post_page(request: Request):
    category = request.path_params['category'] if request.path_params['category'] != "bez-kategorii" else ""
    slug = request.path_params['slug']

    index_page_info = await request.app.state.crud.pages.get_index_meta()
    pages = await request.app.state.crud.pages.get_menu_pages()

    post = await request.app.state.crud.posts.get_with_category_author_by_slug(slug, category)

    if not post:
        return RedirectResponse("/")

    form_data = await request.form()

    if form_data:
        author = form_data.get("author")
        email = form_data.get("email")
        content = form_data.get("content")

        post_id = post[7]

        await request.app.state.crud.comments.add_comment(author, email, content, post_id)

    comments = await request.app.state.crud.comments.list_for_post(post[7])

    pages_center = [p for p in pages if p[3] == 'center']
    pages_right = [p for p in pages if p[3] == 'right']

    return templates.TemplateResponse("index/post.html", {"request": request,
                                                          "post": post,
                                                          "comments": comments,
                                                          "pages_center": pages_center,
                                                          "pages_right": pages_right,
                                                          "info": index_page_info})
