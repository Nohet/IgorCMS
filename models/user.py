from pydantic import BaseModel, EmailStr
from enums.permissions import Permissions


class UserDatabase(BaseModel):
    id: int
    firstname: str
    lastname: str
    email: EmailStr
    password_hash: str
    permissions: Permissions
    profile_picture: str
    description: str


class UserJWT(BaseModel):
    access_token: str
    user_id: int
    firstname: str
    lastname: str
    permissions: Permissions