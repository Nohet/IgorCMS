import random
import string

from starlette.templating import Jinja2Templates

SECRET_KEY = ''.join(random.choices(string.ascii_letters + string.digits + string.punctuation, k=32))
API_UPLOAD_KEY = ''.join(random.choices(string.ascii_letters + string.digits, k=64))
templates = Jinja2Templates(directory='templates')