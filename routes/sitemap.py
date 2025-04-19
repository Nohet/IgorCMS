import os
from datetime import datetime, UTC

from jinja2 import Template
from starlette.requests import Request
from starlette.responses import Response

from utils.text_utils import sanitize_text


async def sitemap(request: Request):
    async with request.app.state.db_pool.acquire() as conn:
        async with conn.cursor() as cursor:
            xml_template_path = os.path.join(os.path.dirname(__file__), '../static/sitemap.template.xml')
            xml_template_path = os.path.abspath(xml_template_path)

            await cursor.execute("""SELECT categories.name, slug, posts.updated_at
                                    FROM `posts` 
                                    LEFT JOIN categories ON categories.id = posts.category_id""")
            posts = await cursor.fetchall()
            posts = [[(sanitize_text(post[0]) if post[0] else 'bez-kategorii'), post[1], post[2].strftime("%Y-%m-%d")]
                     for post in posts]

            await cursor.execute("SELECT slug, updated_at FROM `pages` WHERE id != 1")
            custom_pages = await cursor.fetchall()
            custom_pages = [[custom_page[0], custom_page[1].strftime("%Y-%m-%d")] for custom_page in custom_pages]

            template = Template(open(xml_template_path).read())
            rendered_xml = template.render(today=datetime.now(UTC).strftime("%Y-%m-%d"), custom_pages=custom_pages,
                                           posts=posts, baseUrl=("https://" if request.url.is_secure else "http://")
                                           + request.url.hostname + f":{request.url.port}")

            return Response(content=rendered_xml, media_type="application/xml")
