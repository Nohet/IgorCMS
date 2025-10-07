import base64
import os
from pathlib import Path

from starlette.requests import Request
from starlette.responses import JSONResponse

from constants.static import API_UPLOAD_KEY
from utils.responses import response_message
from utils.text_utils import sanitize_filename

ALLOWED_IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "gif", "bmp", "webp"}


async def api_save_image_from_data_uri(request: Request):
    try:
        data = await request.json()

        upload_key = data.get("uploadKey")

        if upload_key != API_UPLOAD_KEY:
            return response_message("error", "Upload key is invalid!", code=400)

        data_uri = data.get("image")
        filename = data.get("filename")

        if not data_uri or not data_uri.startswith("data:image/"):
            return response_message("error", "Invalid or missing image data URI.", code=400)

        header, base64_data = data_uri.split(",", 1)
        header_parts = header.split(":", 1)[-1].split("/", 1)
        mime_extension = header_parts[1].split(";")[0].lower() if len(header_parts) > 1 else ''

        image_data = base64.b64decode(base64_data)

        storage_dir = Path(__file__).resolve().parent.parent.parent / "static" / "image_storage"
        storage_dir.mkdir(parents=True, exist_ok=True)

        safe_filename = sanitize_filename(filename)
        name, ext = os.path.splitext(safe_filename)
        extension = ext.lstrip('.').lower()

        if not extension and mime_extension:
            extension = mime_extension
            ext = f".{extension}"

        if extension not in ALLOWED_IMAGE_EXTENSIONS:
            return response_message("error", "File extension is not allowed.", code=400)

        if not name:
            name = sanitize_filename('', fallback=None)

        candidate_path = storage_dir / f"{name}{ext}"
        suffix = 1
        while candidate_path.exists():
            candidate_path = storage_dir / f"{name}_{suffix}{ext}"
            suffix += 1

        with open(candidate_path, "wb") as file_handle:
            file_handle.write(image_data)

        return JSONResponse({"path": f"/static/image_storage/{candidate_path.name}"})

    except Exception as e:
        print(e)
        return response_message("error", str(e), code=400)
