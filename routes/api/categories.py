from starlette.requests import Request
from utils.responses import response_message


async def api_list_categories(request: Request):
    """Retrieves all categories."""
    async with request.app.state.db_pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("SELECT * FROM categories")
            rows = await cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            results = str([dict(zip(columns, row)) for row in rows])

            return response_message("success", "Categories retrieved successfully", results)


async def api_create_category(request: Request):
    """Creates new category."""
    data = await request.json()
    async with request.app.state.db_pool.acquire() as conn:
        async with conn.cursor() as cursor:
            sql = """
                INSERT INTO categories (name, description, parent_id)
                VALUES (%s, %s, %s)
            """
            params = (
                data.get("name"),
                data.get("description"),
                data.get("parent_id")
            )
            await cursor.execute(sql, params)

            return response_message("success", "Category created successfully")


async def api_update_category(request: Request):
    """Updates existing category."""
    data = await request.json()
    category_id = request.path_params["id"]
    async with request.app.state.db_pool.acquire() as conn:
        async with conn.cursor() as cursor:
            sql = """
                UPDATE categories
                SET name = %s, description = %s, updated_at = CURRENT_TIMESTAMP(), parent_id = %s
                WHERE id = %s
            """
            params = (
                data.get("name"),
                data.get("description"),
                data.get("parent_id"),
                category_id
            )
            await cursor.execute(sql, params)

            return response_message("success", "Category updated successfully")
