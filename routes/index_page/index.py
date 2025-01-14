from itertools import islice

from starlette.requests import Request
from starlette.templating import Jinja2Templates

from utils.text_utils import title_to_slug

templates = Jinja2Templates(directory='templates')


async def index_page(request: Request):
    async with request.app.state.db_pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("""SELECT title, image, meta_title, meta_description, 
                                    meta_keywords, meta_robots, language, navbar_title 
                                    FROM `pages` WHERE id = 1""")
            index_page_info = await cursor.fetchone()

            await cursor.execute("""SELECT posts.title, posts.updated_at, posts.featured_image,
                                    categories.name, posts.id, posts.slug, status
                                    FROM `posts` 
                                    LEFT JOIN categories ON categories.id = posts.category_id 
                                    HAVING status = 'published'
                                    ORDER BY posts.updated_at DESC
                                """)
            posts = await cursor.fetchall()

            await cursor.execute("""SELECT id, navbar_title, slug, display FROM `pages` 
                                    WHERE show_in_menu = 1""")
            pages = await cursor.fetchall()

            pages_center = [p for p in pages if p[3] == 'center']
            pages_right = [p for p in pages if p[3] == 'right']

            iterator = iter(posts)
            posts = list(iter(lambda: list(islice(iterator, 5)), []))

            return templates.TemplateResponse("index/index.html", {"request": request,
                                                                   "title_to_slug": title_to_slug,
                                                                   "posts": posts,
                                                                   "pages_center": pages_center,
                                                                   "pages_right": pages_right,
                                                                   "info": index_page_info})
