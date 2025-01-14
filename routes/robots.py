import os.path

from jinja2 import Template
from starlette.requests import Request
from starlette.responses import FileResponse, Response


def robots_txt(request: Request):
    robots_txt_path = os.path.join(os.path.dirname(__file__), '../static/robots.template.txt')
    robots_txt_path = os.path.abspath(robots_txt_path)

    template = Template(open(robots_txt_path).read())
    rendered_txt = template.render(baseUrl=("https://" if request.url.is_secure else "http://")
                                            + request.url.hostname + f":{request.url.port}")

    return Response(content=rendered_txt, media_type="text/plain")
