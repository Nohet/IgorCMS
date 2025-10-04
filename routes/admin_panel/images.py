import os

from starlette.requests import Request

from constants.static import API_UPLOAD_KEY, templates
from factories.user_factory import get_user
from models.user import UserJWT
from utils.dependency_injection import dependency_injection


@dependency_injection(get_user)
async def admin_image_gallery(request: Request, user: UserJWT):

    image_storage_path = os.path.join(os.path.dirname(__file__), '../../static/image_storage')
    image_storage_path = os.path.abspath(image_storage_path)

    images = os.listdir(image_storage_path)

    return templates.TemplateResponse("admin/image_gallery/image_gallery.html",
                                      {"request": request,
                                       "images": images,
                                       "firstname": getattr(user, "firstname", ""),
                                       "lastname": getattr(user, "lastname", ""),
                                       "permissions": getattr(user, "permissions", "")})
