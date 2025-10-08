import os
from pathlib import Path

from starlette.requests import Request
from starlette.responses import JSONResponse

from constants.static import templates
from factories.user_factory import get_user
from models.user import UserJWT
from utils.dependency_injection import dependency_injection

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"}
IMAGE_STORAGE_PATH = Path(__file__).resolve().parents[2] / "static" / "image_storage"


def _iter_image_files():
    if not IMAGE_STORAGE_PATH.exists():
        return []

    return [
        path for path in IMAGE_STORAGE_PATH.rglob("*")
        if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
    ]


def _resolve_image_path(filename: str):
    sanitized = os.path.basename(filename)

    if sanitized != filename:
        return None

    for path in _iter_image_files():
        if path.name == sanitized:
            return path

    return None


@dependency_injection(get_user)
async def admin_image_gallery(request: Request, user: UserJWT):
    images = sorted({path.name for path in _iter_image_files()})

    return templates.TemplateResponse("admin/image_gallery/image_gallery.html",
                                      {"request": request,
                                       "images": images,
                                       "firstname": getattr(user, "firstname", ""),
                                       "lastname": getattr(user, "lastname", ""),
                                       "permissions": getattr(user, "permissions", "")})


@dependency_injection(get_user)
async def admin_delete_image(request: Request, user: UserJWT):
    if request.headers.get("content-type", "").startswith("application/json"):
        payload = await request.json()
        filename = payload.get("filename")
    else:
        form = await request.form()
        filename = form.get("filename")

    if not filename:
        return JSONResponse({"success": False, "message": "No filename provided."}, status_code=400)

    image_path = _resolve_image_path(filename)
    if not image_path or not image_path.exists():
        return JSONResponse({"success": False, "message": "Image not found."}, status_code=404)

    try:
        image_path.unlink()
    except PermissionError:
        return JSONResponse({"success": False, "message": "Permission denied."}, status_code=403)
    except OSError:
        return JSONResponse({"success": False, "message": "Failed to delete image."}, status_code=500)

    return JSONResponse({"success": True})
