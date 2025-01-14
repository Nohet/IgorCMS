import jwt

from starlette.requests import Request
from starlette.templating import Jinja2Templates

from definitions.static import SECRET_KEY
from utils.text_utils import title_to_slug, normalize_text

templates = Jinja2Templates(directory='templates')


async def admin_homepage(request: Request):
    form_data = await request.form()
    token = jwt.decode(request.cookies.get("access_token"), SECRET_KEY, algorithms=["HS256"])

    async with request.app.state.db_pool.acquire() as conn:
        async with conn.cursor() as cursor:
            if form_data.get("title") and form_data.get("content"):
                author_id = token["user_id"]

                await cursor.execute(
                    "INSERT INTO posts(author_id, title, slug, content, status) VALUES (%s, %s, %s, %s, 'draft')",
                    (
                        author_id, form_data.get("title"),
                        normalize_text(title_to_slug(form_data.get("title"))), form_data.get("content")))

            await cursor.execute("SELECT COUNT(*) from posts;")
            post_count = (await cursor.fetchone())[0]

            await cursor.execute("SELECT COUNT(*) from pages;")
            pages_count = (await cursor.fetchone())[0]

            await cursor.execute("SELECT COUNT(*) from comments;")
            comments_count = (await cursor.fetchone())[0]

            await cursor.execute("SELECT created_at, title FROM `posts` GROUP BY created_at DESC LIMIT 1")
            last_post = await cursor.fetchone()

            await cursor.execute("""SELECT comments.author, comments.content, comments.published_at, posts.title 
                            FROM `comments` 
                            INNER JOIN posts on posts.id = comments.post_id GROUP BY published_at DESC LIMIT 1;""")
            last_comment = await cursor.fetchone()

            return templates.TemplateResponse("admin/homepage/admin_homepage.html",
                                              {"request": request, "post_count": post_count,
                                               "pages_count": pages_count, "comments_count": comments_count,

                                               "last_post": {"date": last_post[0] if last_post else "",
                                                             "title": last_post[1] if last_post else "",
                                                             "exists": last_post},

                                               "last_comment": {"author": last_comment[0] if last_comment else "",
                                                                "content": last_comment[1] if last_comment else "",
                                                                "published_at": last_comment[2] if last_comment else "",
                                                                "post_title": last_comment[3] if last_comment else "",
                                                                "exists": last_comment},

                                               "firstname": token.get("firstname"), "lastname": token.get("lastname"),
                                               "permissions": token.get("permissions")})
