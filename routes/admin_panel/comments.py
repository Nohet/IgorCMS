from starlette.requests import Request
from starlette.responses import RedirectResponse

from constants.static import templates
from factories.user_factory import get_user
from models.user import UserJWT
from utils.dependency_injection import dependency_injection


async def admin_delete_comment(request: Request):
    comment_id = int(request.query_params.get("id"))
    await request.app.state.crud.comments.delete(comment_id)
    return RedirectResponse("/admin/comments/view")


@dependency_injection(get_user)
async def admin_comments_view(request: Request, user: UserJWT):

    comments = await request.app.state.crud.comments.list_with_posts_for_admin()

    return templates.TemplateResponse("admin/comments/comments.html", {"request": request, "comments": comments,
                                                                       "firstname": getattr(user, "firstname", ""),
                                                                       "lastname": getattr(user, "lastname", ""),
                                                                       "permissions": getattr(user, "permissions", "")})
