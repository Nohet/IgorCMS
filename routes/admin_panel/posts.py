from starlette.requests import Request
from starlette.responses import RedirectResponse

from constants.static import templates
from factories.user_factory import get_user
from models.user import UserJWT
from utils.dependency_injection import dependency_injection
from enums.permissions import Permissions
from utils.text_utils import sanitize_text


@dependency_injection(get_user)
async def admin_edit_post(request: Request, user: UserJWT):
    messages = []

    post_id = int(request.query_params.get("id"))

    form_data = await request.form()

    if form_data:
        title = form_data.get("title")
        post_content = form_data.get("post_content")
        excerpt = form_data.get("excerpt")
        tags = form_data.get("tags")
        featured_image = form_data.get("featured_image")
        comments_enabled = int(form_data.get("comments_enabled"))
        category = int(form_data.get("category")) if form_data.get("category") and form_data.get("category").isdigit() else None
        status = form_data.get("status")

        await request.app.state.crud.posts.admin_update(
            post_id,
            title=title,
            slug=sanitize_text(title),
            content=post_content,
            excerpt=excerpt,
            tags=tags,
            featured_image=featured_image,
            comments_enabled=comments_enabled,
            category_id=category,
            status=status,
            editor_id=getattr(user, "user_id", None),
        )
        messages.append("Successfully saved changes!")

    data = await request.app.state.crud.posts.admin_get_details(post_id)
    categories = await request.app.state.crud.categories.list_all_basic()

    return templates.TemplateResponse("admin/posts/edit/edit_post.html", {"request": request,
                                                                        "data": data,
                                                                        "messages": messages,
                                                                        "firstname": getattr(user, "firstname", ""),
                                                                        "categories": categories,
                                                                        "lastname": getattr(user, "lastname", ""),
                                                                        "permissions": getattr(user, "permissions", "")})


@dependency_injection(get_user)
async def admin_delete_post(request: Request, user: UserJWT):
    if getattr(user, 'permissions', None) != Permissions.ADMINISTRATOR:
        return RedirectResponse('/admin/posts/view', status_code=303)

    form_data = await request.form()
    post_id = form_data.get('post_id')

    if not post_id or not str(post_id).isdigit():
        return RedirectResponse('/admin/posts/view', status_code=303)

    await request.app.state.crud.posts.admin_delete(int(post_id))
    return RedirectResponse('/admin/posts/view', status_code=303)


@dependency_injection(get_user)
async def admin_show_posts(request: Request, user: UserJWT):

    posts = await request.app.state.crud.posts.admin_list_posts()

    return templates.TemplateResponse("admin/posts/view/show_posts.html", {"request": request,
                                                                         "sanitize_text": sanitize_text,
                                                                         "posts": posts,
                                                                         "firstname": getattr(user, "firstname", ""),
                                                                         "lastname": getattr(user, "lastname", ""),
                                                                         "permissions": getattr(user, "permissions", ""),
                                                                         })


@dependency_injection(get_user)
async def admin_add_post(request: Request, user: UserJWT):
    messages = []

    form_data = await request.form()

    if form_data:
        title = form_data.get("title")
        content = form_data.get("post_content")
        excerpt = form_data.get("excerpt")
        tags = form_data.get("tags")
        featured_image = form_data.get("featured_image")
        comments_enabled = int(form_data.get("comments_enabled"))
        category_id = int(form_data.get("category")) if form_data.get("category") and form_data.get("category").isdigit() else None
        status = form_data.get("status")

        await request.app.state.crud.posts.admin_create(
            slug=sanitize_text(title), title=title, content=content, excerpt=excerpt,
            author_id=getattr(user, "user_id", None), status=status, tags=tags, featured_image=featured_image,
            comments_enabled=comments_enabled, category_id=category_id
        )
        messages.append("Successfully added a new post!")

    categories = await request.app.state.crud.categories.list_all_basic()

    return templates.TemplateResponse("admin/posts/add/create_post.html", {"request": request,
                                                                         "firstname": getattr(user, "firstname", ""),
                                                                         "messages": messages,
                                                                         "categories": categories,
                                                                         "lastname": getattr(user, "lastname", ""),
                                                                         "permissions": getattr(user, "permissions", "")})
