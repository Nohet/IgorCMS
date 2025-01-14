import os

import jwt

from starlette.requests import Request
from starlette.templating import Jinja2Templates

from definitions.static import SECRET_KEY, API_UPLOAD_KEY

templates = Jinja2Templates(directory='templates')


async def admin_image_gallery(request: Request):
    token = jwt.decode(request.cookies.get("access_token"), SECRET_KEY, algorithms=["HS256"])

    image_storage_path = os.path.join(os.path.dirname(__file__), '../../static/image_storage')
    image_storage_path = os.path.abspath(image_storage_path)

    images = os.listdir(image_storage_path)

    return templates.TemplateResponse("admin/image_gallery/image_gallery.html",
                                              {"request": request,
                                               "images": images,
                                               "API_UPLOAD_KEY": API_UPLOAD_KEY,
                                               "firstname": token.get("firstname"),
                                               "lastname": token.get("lastname"),
                                               "permissions": token.get("permissions")})
