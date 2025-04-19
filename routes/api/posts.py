from starlette.requests import Request

from utils.responses import response_message
from utils.text_utils import sanitize_text


async def api_get_posts(request: Request):
    """Wyświetla listę postów."""
    async with request.app.state.db_pool.acquire() as conn:
        async with conn.cursor() as cursor:
            sql = "SELECT * FROM posts"
            await cursor.execute(sql)
            posts = await cursor.fetchall()
            return response_message("success", "Posts retrieved successfully", posts)


async def api_create_post(request: Request):
    """Tworzy nowy post."""
    data = await request.json()
    async with request.app.state.db_pool.acquire() as conn:
        async with conn.cursor() as cursor:
            sql = """
                INSERT INTO posts (slug, title, content, excerpt, author_id, editor_id, created_at, updated_at, published_at, status, tags, featured_image, comments_enabled, category_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            params = (
                sanitize_text(data.get("title")),
                data.get("title"),
                data.get("content"),
                data.get("excerpt"),
                data.get("author_id"),
                data.get("editor_id"),
                data.get("created_at"),
                data.get("updated_at"),
                data.get("published_at"),
                data.get("status"),
                data.get("tags"),
                data.get("featured_image"),
                data.get("comments_enabled"),
                data.get("category_id")
            )
            await cursor.execute(sql, params)

            return response_message("success", "Post created successfully")


async def api_update_post(request: Request):
    """Aktualizuje istniejący post."""
    data = await request.json()
    post_id = request.path_params["id"]
    async with request.app.state.db_pool.acquire() as conn:
        async with conn.cursor() as cursor:
            sql = """
                UPDATE posts
                SET slug = %s, title = %s, content = %s, excerpt = %s, author_id = %s, editor_id = %s, updated_at = %s, published_at = %s, status = %s, tags = %s, featured_image = %s, comments_enabled = %s, category_id = %s
                WHERE id = %s
            """
            params = (
                sanitize_text(data.get("title")),
                data.get("title"),
                data.get("content"),
                data.get("excerpt"),
                data.get("author_id"),
                data.get("editor_id"),
                data.get("updated_at"),
                data.get("published_at"),
                data.get("status"),
                data.get("tags"),
                data.get("featured_image"),
                data.get("comments_enabled"),
                data.get("category_id"),
                post_id
            )
            await cursor.execute(sql, params)

            return response_message("success", "Post updated successfully")


async def api_delete_post(request: Request):
    """Usuwa post na podstawie ID."""
    post_id = request.path_params["id"]
    async with request.app.state.db_pool.acquire() as conn:
        async with conn.cursor() as cursor:
            sql = "DELETE FROM posts WHERE id = %s"
            await cursor.execute(sql, (post_id,))

            return response_message("success", "Post deleted successfully")
