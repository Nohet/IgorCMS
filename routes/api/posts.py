from starlette.requests import Request

from utils.responses import response_message
from utils.text_utils import sanitize_text


async def api_get_posts(request: Request):
    """Retrieves all posts."""
    posts = await request.app.state.crud.posts.api_list()
    return response_message("success", "Posts retrieved successfully", posts)


async def api_create_post(request: Request):
    """Creates a new post."""
    data = await request.json()
    data = {**data, "slug": sanitize_text(data.get("title"))}
    await request.app.state.crud.posts.api_create(data)
    return response_message("success", "Post created successfully")


async def api_update_post(request: Request):
    """Updates existing post."""
    data = await request.json()
    post_id = request.path_params["id"]
    data = {**data, "slug": sanitize_text(data.get("title"))}
    await request.app.state.crud.posts.api_update(int(post_id), data)
    return response_message("success", "Post updated successfully")


async def api_delete_post(request: Request):
    """Deletes a post based on ID."""
    post_id = request.path_params["id"]
    await request.app.state.crud.posts.admin_delete(int(post_id))
    return response_message("success", "Post deleted successfully")
