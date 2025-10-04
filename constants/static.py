import secrets
import json

from starlette.templating import Jinja2Templates
from pathlib import Path

from enums.permissions import Permissions
from utils.config import Config

SECRET_KEY = json.loads((Path(__file__).parent.parent / "config.json").read_text()).get("secretKey") if Config().exists() else secrets.token_hex(64)
API_UPLOAD_KEY = secrets.token_urlsafe(64)

templates = Jinja2Templates(directory='templates', context_processors=[lambda request: {"csrf_token": request.session["csrf_token"],
                                                                                        "PermissionsEnum": Permissions,
                                                                                        "API_UPLOAD_KEY": API_UPLOAD_KEY}])