import json
from pathlib import Path

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import RedirectResponse

base_dir = Path(__file__).resolve().parent.parent
config_path = base_dir / 'config.json'


class CheckSetUp(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        db_json = json.loads(open(config_path).read())

        if any(value is None for value in db_json["database"].values()) and "setup" not in str(request.url):
            return RedirectResponse("/setup/database")

        response = await call_next(request)
        return response
