from starlette.requests import Request

from utils.responses import response_message
from utils.text_utils import sanitize_text


async def api_get_pages(request: Request):
    """Wyświetla listę stron."""
    async with request.app.state.db_pool.acquire() as conn:
        async with conn.cursor() as cursor:
            sql = "SELECT * FROM pages"
            await cursor.execute(sql)
            pages = await cursor.fetchall()
            return response_message("success", "Pages retrieved successfully", pages)


async def api_create_page(request: Request):
    """Tworzy nową stronę."""
    data = await request.json()
    async with request.app.state.db_pool.acquire() as conn:
        async with conn.cursor() as cursor:
            sql = """
                INSERT INTO pages (slug, image, title, content, display, author_id, created_at, updated_at, navbar_title, meta_title, meta_description, meta_keywords, meta_robots, language, redirect_url, parent_id, show_in_menu, category_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            params = (
                sanitize_text(data.get("title")),
                data.get("image"),
                data.get("title"),
                data.get("content"),
                data.get("display"),
                data.get("author_id"),
                data.get("created_at"),
                data.get("updated_at"),
                data.get("navbar_title"),
                data.get("meta_title"),
                data.get("meta_description"),
                data.get("meta_keywords"),
                data.get("meta_robots"),
                data.get("language"),
                data.get("redirect_url"),
                data.get("parent_id"),
                data.get("show_in_menu"),
                data.get("category_id")
            )
            await cursor.execute(sql, params)
            await conn.commit()
            return response_message("success", "Page created successfully")


async def api_update_page(request: Request):
    """Aktualizuje istniejącą stronę."""
    data = await request.json()
    page_id = request.path_params["id"]
    async with request.app.state.db_pool.acquire() as conn:
        async with conn.cursor() as cursor:
            sql = """
                UPDATE pages
                SET slug = %s, image = %s, title = %s, content = %s, display = %s, author_id = %s, updated_at = %s, navbar_title = %s, meta_title = %s, meta_description = %s, meta_keywords = %s, meta_robots = %s, language = %s, redirect_url = %s, parent_id = %s, show_in_menu = %s, category_id = %s
                WHERE id = %s
            """
            params = (
                sanitize_text(data.get("title")),
                data.get("image"),
                data.get("title"),
                data.get("content"),
                data.get("display"),
                data.get("author_id"),
                data.get("updated_at"),
                data.get("navbar_title"),
                data.get("meta_title"),
                data.get("meta_description"),
                data.get("meta_keywords"),
                data.get("meta_robots"),
                data.get("language"),
                data.get("redirect_url"),
                data.get("parent_id"),
                data.get("show_in_menu"),
                data.get("category_id"),
                page_id
            )
            await cursor.execute(sql, params)
            await conn.commit()
            return response_message("success", "Page updated successfully")


async def api_delete_page(request: Request):
    """Usuwa stronę na podstawie ID."""
    page_id = request.path_params["id"]
    async with request.app.state.db_pool.acquire() as conn:
        async with conn.cursor() as cursor:
            sql = "DELETE FROM pages WHERE id = %s"
            await cursor.execute(sql, (page_id,))
            await conn.commit()
            return response_message("success", "Page deleted successfully")
