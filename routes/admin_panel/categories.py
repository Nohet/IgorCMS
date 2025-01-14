import jwt
from starlette.requests import Request
from starlette.responses import RedirectResponse
from starlette.templating import Jinja2Templates

from definitions.static import SECRET_KEY

templates = Jinja2Templates(directory='templates')


async def admin_edit_category(request: Request):
    messages = []

    async with request.app.state.db_pool.acquire() as conn:
        async with conn.cursor() as cursor:
            token = jwt.decode(request.cookies.get("access_token"), SECRET_KEY, algorithms=["HS256"])
            category_id = request.query_params.get("id")

            form_data = await request.form()

            if form_data:
                name = form_data.get("name")
                description = form_data.get("description")
                parent_id = eval(form_data.get("parent_id"))

                await cursor.execute("""UPDATE categories SET name=%s, description=%s, parent_id=%s, 
                updated_at=CURRENT_TIMESTAMP() WHERE id = %s""",
                                     (name, description, parent_id, category_id))
                messages.append("Pomyślnie zapisano zmiany!")

            await cursor.execute("SELECT id, name FROM `categories`")
            categories = await cursor.fetchall()

            await cursor.execute("SELECT name, description FROM `categories` WHERE id = %s", (category_id,))
            data = await cursor.fetchone()

            return templates.TemplateResponse("admin/categories/edit/edit_category.html", {"request": request,
                                                                                           "data": data,
                                                                                           "messages": messages,
                                                                                           "categories": categories,
                                                                                           "firstname": token.get(
                                                                                               "firstname"),
                                                                                           "lastname": token.get(
                                                                                               "lastname"),
                                                                                           "permissions": token.get(
                                                                                               "permissions")})


async def admin_delete_category(request: Request):
    async with request.app.state.db_pool.acquire() as conn:
        async with conn.cursor() as cursor:
            category_id = request.query_params.get("id")

            await cursor.execute("DELETE FROM categories WHERE id = %s", (category_id,))

            return RedirectResponse("/admin/categories/view")


async def admin_add_category(request: Request):
    messages = []

    async with request.app.state.db_pool.acquire() as conn:
        async with conn.cursor() as cursor:
            token = jwt.decode(request.cookies.get("access_token"), SECRET_KEY, algorithms=["HS256"])
            form_data = await request.form()

            if form_data:
                name = form_data.get("name")
                description = form_data.get("description")
                parent_id = eval(form_data.get("parent_id"))

                await cursor.execute("INSERT INTO categories(name, description, parent_id) VALUES (%s, %s, %s)",
                                     (name, description, parent_id))
                messages.append("Pomyślnie dodano nową kategorię!")

            await cursor.execute("SELECT id, name FROM `categories`")
            categories = await cursor.fetchall()

            return templates.TemplateResponse("admin/categories/add/add_category.html", {"request": request,
                                                                                         "messages": messages,
                                                                                         "categories": categories,
                                                                                         "firstname": token.get(
                                                                                             "firstname"),
                                                                                         "lastname": token.get(
                                                                                             "lastname"),
                                                                                         "permissions": token.get(
                                                                                             "permissions")})


async def admin_view_categories(request: Request):
    async with request.app.state.db_pool.acquire() as conn:
        async with conn.cursor() as cursor:
            token = jwt.decode(request.cookies.get("access_token"), SECRET_KEY, algorithms=["HS256"])

            await cursor.execute("SELECT id, name, description, created_at, parent_id FROM `categories`")
            categories = await cursor.fetchall()

            return templates.TemplateResponse("admin/categories/view/view_categories.html", {"request": request,
                                                                                             "categories": categories,
                                                                                             "firstname": token.get(
                                                                                                 "firstname"),
                                                                                             "lastname": token.get(
                                                                                                 "lastname"),
                                                                                             "permissions": token.get(
                                                                                                 "permissions")})
