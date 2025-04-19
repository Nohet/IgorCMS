import jwt
from starlette.requests import Request
from starlette.responses import RedirectResponse

from definitions.static import SECRET_KEY, API_UPLOAD_KEY, templates
from utils.text_utils import sanitize_text


async def admin_edit_post(request: Request):
    token = jwt.decode(request.cookies.get("access_token"), SECRET_KEY, algorithms=["HS256"])
    messages = []

    async with request.app.state.db_pool.acquire() as conn:
        async with conn.cursor() as cursor:
            post_id = request.query_params.get("id")

            form_data = await request.form()

            if form_data:
                title = form_data.get("title")
                post_content = form_data.get("post_content")
                excerpt = form_data.get("excerpt")
                tags = form_data.get("tags")
                featured_image = form_data.get("featured_image")
                comments_enabled = int(form_data.get("comments_enabled"))
                category = int(form_data.get("category")) if form_data.get("category") and form_data.get("category").isdigit() else None
                status = form_data.get("status")

                await cursor.execute("""
                UPDATE posts SET title=%s, slug=%s,content=%s,
                excerpt=%s,tags=%s,featured_image=%s,comments_enabled=%s,
                category_id=%s,status=%s, updated_at=CURRENT_TIMESTAMP(),editor_id=%s
                WHERE id = %s
                """, (title, sanitize_text(title), post_content, excerpt, tags, featured_image,
                      comments_enabled,
                      category, status, token.get("user_id"), post_id))
                messages.append("Successfully saved changes!")

            await cursor.execute("SELECT title, content, excerpt, tags, featured_image FROM `posts` WHERE id = %s",
                                 (post_id,))
            data = await cursor.fetchone()

            await cursor.execute("SELECT id, name FROM `categories`")
            categories = await cursor.fetchall()

            return templates.TemplateResponse("admin/posts/edit/edit_post.html", {"request": request,
                                                                                  "data": data,
                                                                                  "messages": messages,
                                                                                  "firstname": token.get("firstname"),
                                                                                  "API_UPLOAD_KEY": API_UPLOAD_KEY,
                                                                                  "categories": categories,
                                                                                  "lastname": token.get("lastname"),
                                                                                  "permissions": token.get(
                                                                                      "permissions")})


async def admin_delete_post(request: Request):
    async with request.app.state.db_pool.acquire() as conn:
        async with conn.cursor() as cursor:
            post_id = request.query_params.get("id")

            await cursor.execute("DELETE FROM posts WHERE id = %s", (post_id,))

            return RedirectResponse("/admin/posts/view")


async def admin_show_posts(request: Request):
    async with request.app.state.db_pool.acquire() as conn:
        async with conn.cursor() as cursor:
            token = jwt.decode(request.cookies.get("access_token"), SECRET_KEY, algorithms=["HS256"])

            await cursor.execute("""SELECT posts.title, 
    CONCAT(users.firstname, " ", users.lastname) AS author_name, 
    COALESCE(categories.name, NULL) AS category_name, 
    posts.tags, 
    posts.updated_at, 
    posts.status,
    posts.id,
    posts.slug
    FROM posts
    LEFT JOIN users ON posts.author_id = users.id
    LEFT JOIN categories ON posts.category_id = categories.id;
    """)
            posts = await cursor.fetchall()

            return templates.TemplateResponse("admin/posts/view/show_posts.html", {"request": request,
                                                                                   "sanitize_text": sanitize_text,
                                                                                   "posts": posts,
                                                                                   "firstname": token.get("firstname"),
                                                                                   "lastname": token.get("lastname"),
                                                                                   "permissions": token.get(
                                                                                       "permissions"),
                                                                                   })


async def admin_add_post(request: Request):
    token = jwt.decode(request.cookies.get("access_token"), SECRET_KEY, algorithms=["HS256"])
    messages = []

    async with request.app.state.db_pool.acquire() as conn:
        async with conn.cursor() as cursor:
            form_data = await request.form()

            if form_data:
                title = form_data.get("title")
                content = form_data.get("post_content")
                excerpt = form_data.get("excerpt")
                tags = form_data.get("tags")
                featured_image = form_data.get("featured_image")
                comments_enabled = int(form_data.get("comments_enabled"))
                category_id = int(form_data.get("category")) if form_data.get("category") and form_data.get("category").isdigit() else None
                status = form_data.get("status")

                await cursor.execute("""INSERT INTO posts(slug, title, content, excerpt, author_id, status, tags, featured_image, comments_enabled, category_id) 
                                VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", (
                    sanitize_text(title), title, content, excerpt, token.get("user_id"), status, tags,
                    featured_image,
                    comments_enabled, category_id))
                messages.append("Successfully added a new post!")

            await cursor.execute("SELECT id, name FROM `categories`")
            categories = await cursor.fetchall()

            return templates.TemplateResponse("admin/posts/add/create_post.html", {"request": request,
                                                                                   "firstname": token.get("firstname"),
                                                                                   "messages": messages,
                                                                                   "API_UPLOAD_KEY": API_UPLOAD_KEY,
                                                                                   "categories": categories,
                                                                                   "lastname": token.get("lastname"),
                                                                                   "permissions": token.get(
                                                                                       "permissions")})
