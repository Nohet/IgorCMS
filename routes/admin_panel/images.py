import itertools
import os
import glob

from starlette.requests import Request

from constants.static import API_UPLOAD_KEY, templates
from factories.user_factory import get_user
from models.user import UserJWT
from utils.dependency_injection import dependency_injection


@dependency_injection(get_user)
async def admin_image_gallery(request: Request, user: UserJWT):
    image_storage_path = os.path.join(os.path.dirname(__file__), '../../static/image_storage')
    image_storage_path = os.path.abspath(image_storage_path)

    exts = ["jpg", "jpeg", "png", "gif", "bmp", "webp"]
    patterns = [os.path.join(image_storage_path, f"**/*.{e}") for e in exts] + \
               [os.path.join(image_storage_path, f"**/*.{e.upper()}") for e in exts]

    images = sorted({os.path.basename(p) for p in itertools.chain.from_iterable(
        glob.glob(patt, recursive=True) for patt in patterns
    )})

    return templates.TemplateResponse("admin/image_gallery/image_gallery.html",
                                      {"request": request,
                                       "images": images,
                                       "firstname": getattr(user, "firstname", ""),
                                       "lastname": getattr(user, "lastname", ""),
                                       "permissions": getattr(user, "permissions", "")})
