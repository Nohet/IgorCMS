from starlette.requests import Request

from utils.responses import response_message


async def api_list_comments(request: Request):
    """Retrieves all comments."""
    results = await request.app.state.crud.comments.api_list()
    return response_message("success", "Comments retrieved successfully", results)


async def api_delete_comment(request: Request):
    """Deletes comment based on ID."""
    comment_id = request.path_params["id"]
    await request.app.state.crud.comments.delete(int(comment_id))
    return response_message("success", "Comment deleted successfully")
