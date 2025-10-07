import jwt

from constants.static import SECRET_KEY
from models.user import UserJWT


def get_user(request):
    token = request.cookies.get("access_token")
    if not token:
        return None

    data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

    return UserJWT.model_validate(data)
