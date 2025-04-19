from starlette.requests import Request
from starlette.responses import RedirectResponse
from definitions.static import templates


async def custom_page(request: Request):
    async with request.app.state.db_pool.acquire() as conn:
        async with conn.cursor() as cursor:
            slug = request.path_params['slug']

            if slug in ["admin", "post", "static"]:
                return

            await cursor.execute("""SELECT title, image, meta_title, meta_description, 
                                    meta_keywords, meta_robots, language, content, redirect_url
                                    FROM `pages` WHERE slug = %s""", (slug,))
            page_info = await cursor.fetchone()

            if not page_info:
                return RedirectResponse("/")

            if page_info[8]:
                return RedirectResponse(page_info[8])

            await cursor.execute("""SELECT navbar_title 
                                    FROM `pages` WHERE id = 1""")
            index_info = await cursor.fetchone()

            await cursor.execute("""SELECT id, navbar_title, slug, display FROM `pages` 
                                    WHERE show_in_menu = 1""")
            pages = await cursor.fetchall()

            pages_center = [p for p in pages if p[3] == 'center']
            pages_right = [p for p in pages if p[3] == 'right']

            return templates.TemplateResponse("index/custom_page.html", {"request": request,
                                                                         "index_info": index_info,
                                                                         "page_info": page_info,
                                                                         "pages_center": pages_center,
                                                                         "pages_right": pages_right, })
