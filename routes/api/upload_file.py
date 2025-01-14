import base64
import os
from pathlib import Path

from starlette.requests import Request
from starlette.responses import JSONResponse

from definitions.static import API_UPLOAD_KEY
from utils.responses import response_message


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

        image_data = base64.b64decode(base64_data)

        file_path = os.path.join(Path(__file__).resolve().parent.parent.parent / "./static/image_storage", filename)

        with open(file_path, "wb") as f:
            f.write(image_data)

        return JSONResponse(
            {"path": f"/static/image_storage/{filename}"})

    except Exception as e:
        print(e)
        return response_message("error", str(e), code=400)
