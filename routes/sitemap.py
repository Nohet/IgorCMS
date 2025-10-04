import os
from datetime import datetime, UTC

from jinja2 import Template
from starlette.requests import Request
from starlette.responses import Response

from utils.text_utils import sanitize_text


async def sitemap(request: Request):
    xml_template_path = os.path.join(os.path.dirname(__file__), '../static/sitemap.template.xml')
    xml_template_path = os.path.abspath(xml_template_path)

    crud_sitemap = getattr(request.app.state.crud, "sitemap", None)
    if crud_sitemap is None:
        return Response(status_code=503, content="Sitemap is not available while the database is offline.")

    raw_posts = await crud_sitemap.list_posts_with_categories()
    posts = [
        [
            sanitize_text(post[0]) if post[0] else 'bez-kategorii',
            post[1],
            post[2].strftime("%Y-%m-%d") if post[2] else datetime.now(UTC).strftime("%Y-%m-%d")
        ]
        for post in raw_posts
    ]

    raw_custom_pages = await crud_sitemap.list_custom_pages()
    custom_pages = [
        [page[0], page[1].strftime("%Y-%m-%d") if page[1] else datetime.now(UTC).strftime("%Y-%m-%d")]
        for page in raw_custom_pages
    ]

    template = Template(open(xml_template_path).read())
    rendered_xml = template.render(today=datetime.now(UTC).strftime("%Y-%m-%d"), custom_pages=custom_pages,
                                   posts=posts, baseUrl=("https://" if request.url.is_secure else "http://")
                                   + request.url.hostname + f":{request.url.port}")

    return Response(content=rendered_xml, media_type="application/xml")
