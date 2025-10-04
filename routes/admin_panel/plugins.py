from starlette.requests import Request

from constants.static import templates
from factories.user_factory import get_user
from models.user import UserJWT
from utils.dependency_injection import dependency_injection


@dependency_injection(get_user)
async def admin_show_plugins(request: Request, user: UserJWT):

    return templates.TemplateResponse("admin/plugins/plugins.html", {"request": request,
                                                                     "plugins": request.app.state.plugins,
                                                                     "firstname": getattr(user, "firstname", ""),
                                                                     "lastname": getattr(user, "lastname", ""),
                                                                     "permissions": getattr(user, "permissions", "")})
