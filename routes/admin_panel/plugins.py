import jwt
from starlette.requests import Request

from constants.static import SECRET_KEY, templates


async def admin_show_plugins(request: Request):
    token = jwt.decode(request.cookies.get("access_token"), SECRET_KEY, algorithms=["HS256"])

    return templates.TemplateResponse("admin/plugins/plugins.html", {"request": request,
                                                                     "plugins": request.app.state.plugins,
                                                                     "firstname": token.get("firstname"),
                                                                     "lastname": token.get("lastname"),
                                                                     "permissions": token.get(
                                                                         "permissions")})
