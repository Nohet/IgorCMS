from starlette.requests import Request

from constants.static import SECRET_KEY, templates
from models.user import UserJWT
from utils.text_utils import sanitize_text
from factories.user_factory import get_user
from utils.dependency_injection import dependency_injection


@dependency_injection(get_user)
async def admin_homepage(request: Request, user: UserJWT):
    form_data = await request.form()

    if form_data.get("title") and form_data.get("content"):
        author_id = user.user_id if user else None
        await request.app.state.crud.homepage.create_post_draft(
            author_id, form_data.get("title"), sanitize_text(form_data.get("title")), form_data.get("content")
        )

    post_count, pages_count, comments_count = await request.app.state.crud.homepage.counts()
    last_post = await request.app.state.crud.homepage.last_post()
    last_comment = await request.app.state.crud.homepage.last_comment_with_post()

    return templates.TemplateResponse("admin/homepage/admin_homepage.html",
                                      {"request": request, "post_count": post_count,
                                       "pages_count": pages_count, "comments_count": comments_count,

                                       "last_post": {"date": last_post[0] if last_post else "",
                                                     "title": last_post[1] if last_post else "",
                                                     "exists": last_post},

                                       "last_comment": {"author": last_comment[0] if last_comment else "",
                                                        "content": last_comment[1] if last_comment else "",
                                                        "published_at": last_comment[2] if last_comment else "",
                                                        "post_title": last_comment[3] if last_comment else "",
                                                        "exists": last_comment},

                                       "firstname": getattr(user, "firstname", ""), "lastname": getattr(user, "lastname", ""),
                                       "permissions": getattr(user, "permissions", "")})
