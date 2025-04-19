import jwt
from starlette.requests import Request
from starlette.responses import RedirectResponse
from starlette.templating import Jinja2Templates

from definitions.static import SECRET_KEY, API_UPLOAD_KEY
from utils.text_utils import sanitize_text

templates = Jinja2Templates(directory='templates')


async def admin_edit_page(request: Request):
    messages = []

    async with request.app.state.db_pool.acquire() as conn:
        async with conn.cursor() as cursor:
            token = jwt.decode(request.cookies.get("access_token"), SECRET_KEY, algorithms=["HS256"])
            page_id = request.query_params.get("id")

            form_data = await request.form()

            if form_data:
                title = form_data.get("title")
                page_content = form_data.get("page_content")
                navbar_title = form_data.get("navbar_title")
                meta_title = form_data.get("meta_title")
                meta_description = form_data.get("meta_description")
                meta_keywords = form_data.get("meta_keywords")
                redirect_url = form_data.get("redirect_url")
                language = form_data.get("language")
                display = form_data.get("display")
                meta_robots = form_data.get("meta_robots")
                category = eval(form_data.get("category"))
                show_in_menu = int(form_data.get("show_in_menu"))
                site_icon = form_data.get("site_icon")

                await cursor.execute("""UPDATE pages SET title=%s,slug=%s,content=%s,navbar_title=%s,
                meta_title=%s,meta_description=%s,meta_keywords=%s,redirect_url=%s,
                language=%s,display=%s,meta_robots=%s,category_id=%s,show_in_menu=%s,
                image=%s,updated_at=CURRENT_TIMESTAMP()
                WHERE id = %s""", (title, sanitize_text(title), page_content, navbar_title, meta_title,
                                   meta_description, meta_keywords, redirect_url, language, display, meta_robots, category,
                                   show_in_menu, site_icon, page_id))

                messages.append("Pomyslnie zapisano zmiany!")

            await cursor.execute("SELECT id, name FROM `categories`")
            categories = await cursor.fetchall()

            await cursor.execute("""
            SELECT title, content, navbar_title,
            meta_title, meta_description, meta_keywords,
            redirect_url, language, image
            FROM `pages` WHERE id = %s
            """, (page_id,))
            page_data = await cursor.fetchone()

            return templates.TemplateResponse("admin/pages/edit/edit_page.html", {"request": request,
                                                                                  "categories": categories,
                                                                                  "data": page_data,
                                                                                  "messages": messages,
                                                                                  "API_UPLOAD_KEY": API_UPLOAD_KEY,
                                                                                  "firstname": token.get("firstname"),
                                                                                  "lastname": token.get("lastname"),
                                                                                  "permissions": token.get(
                                                                                      "permissions")})


async def admin_delete_page(request: Request):
    async with request.app.state.db_pool.acquire() as conn:
        async with conn.cursor() as cursor:
            page_id = request.query_params.get("id")

            await cursor.execute("DELETE FROM pages WHERE id = %s", (page_id,))

            return RedirectResponse("/admin/pages/view")


async def admin_show_pages(request: Request):
    async with request.app.state.db_pool.acquire() as conn:
        async with conn.cursor() as cursor:
            token = jwt.decode(request.cookies.get("access_token"), SECRET_KEY, algorithms=["HS256"])

            await cursor.execute("""SELECT pages.id, pages.slug, pages.title,
                                    CONCAT(users.firstname, ' ', users.lastname), pages.created_at,
                                    pages.meta_title, pages.meta_description, pages.meta_keywords,
                                    pages.meta_robots, pages.redirect_url, pages.parent_id,
                                    pages.show_in_menu, categories.name  FROM `pages`
                                    LEFT JOIN users ON author_id = users.id
                                    LEFT JOIN categories ON category_id = categories.id
                                    WHERE pages.id != 1""")

            pages = await cursor.fetchall()

            return templates.TemplateResponse("admin/pages/view/show_pages.html", {"request": request,
                                                                                   "pages": pages,
                                                                                   "firstname": token.get("firstname"),
                                                                                   "lastname": token.get("lastname"),
                                                                                   "permissions": token.get(
                                                                                       "permissions")})


async def admin_add_page(request: Request):
    messages = []

    async with request.app.state.db_pool.acquire() as conn:
        async with conn.cursor() as cursor:
            token = jwt.decode(request.cookies.get("access_token"), SECRET_KEY, algorithms=["HS256"])

            form_data = await request.form()

            if form_data:
                title = form_data.get("title")
                icon = form_data.get("icon")
                page_content = form_data.get("page_content")
                navbar_title = form_data.get("navbar_title")
                meta_title = form_data.get("meta_title")
                meta_description = form_data.get("meta_description")
                meta_keywords = form_data.get("meta_keywords")
                redirect_url = form_data.get("redirect_url")
                display = form_data.get("display")
                meta_robots = form_data.get("meta_robots")
                language = form_data.get("language")
                category = eval(form_data.get("category"))
                show_in_menu = int(form_data.get("show_in_menu"))

                await cursor.execute("""INSERT INTO pages (slug, image, title, content, display, author_id,
                                        navbar_title, meta_title, meta_description, meta_keywords, meta_robots,
                                         language, redirect_url, show_in_menu, category_id)
                                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                                     (sanitize_text(title), icon, title, page_content, display,
                                      token.get("user_id"),
                                      navbar_title, meta_title, meta_description, meta_keywords, meta_robots, language,
                                      redirect_url, show_in_menu, category))
                messages.append("Pomyślnie dodano nową stronę!")

            await cursor.execute("SELECT id, name FROM `categories`")
            categories = await cursor.fetchall()

            return templates.TemplateResponse("admin/pages/add/add_page.html", {"request": request,
                                                                                "categories": categories,
                                                                                "messages": messages,
                                                                                "API_UPLOAD_KEY": API_UPLOAD_KEY,
                                                                                "firstname": token.get("firstname"),
                                                                                "lastname": token.get("lastname"),
                                                                                "permissions": token.get(
                                                                                    "permissions")})
