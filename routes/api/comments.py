from starlette.requests import Request

from utils.responses import response_message


async def api_list_comments(request: Request):
    """Retrieves all comments."""
    async with request.app.state.db_pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("SELECT * FROM comments")
            rows = await cursor.fetchall()

            columns = [desc[0] for desc in cursor.description]
            results = [dict(zip(columns, row)) for row in rows]

            return response_message("success", "Comments retrieved successfully", results)


async def api_delete_comment(request: Request):
    """Deletes comment based on ID."""
    comment_id = request.path_params["id"]
    async with request.app.state.db_pool.acquire() as conn:
        async with conn.cursor() as cursor:
            sql = "DELETE FROM comments WHERE id = %s"
            await cursor.execute(sql, (comment_id,))

            return response_message("success", "Comment deleted successfully")
