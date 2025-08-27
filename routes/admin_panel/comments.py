import jwt
from starlette.requests import Request
from starlette.responses import RedirectResponse

from constants.static import SECRET_KEY, templates


async def admin_delete_comment(request: Request):
    async with request.app.state.db_pool.acquire() as conn:
        async with conn.cursor() as cursor:
            comment_id = request.query_params.get("id")

            await cursor.execute("DELETE FROM comments WHERE id = %s", (comment_id,))

            return RedirectResponse("/admin/comments/view")


async def admin_comments_view(request: Request):
    async with request.app.state.db_pool.acquire() as conn:
        async with conn.cursor() as cursor:
            token = jwt.decode(request.cookies.get("access_token"), SECRET_KEY, algorithms=["HS256"])

            await cursor.execute("""SELECT comments.author, comments.content, posts.title, comments.published_at, comments.id
                            FROM `comments` 
                            INNER JOIN posts on posts.id = comments.post_id GROUP BY published_at;""")
            comments = await cursor.fetchall()

            return templates.TemplateResponse("admin/comments/comments.html", {"request": request, "comments": comments,
                                                                               "firstname": token.get("firstname"),
                                                                               "lastname": token.get("lastname"),
                                                                               "permissions": token.get("permissions")})
