from starlette.requests import Request

from utils.responses import response_message
from utils.text_utils import sanitize_text


async def api_get_pages(request: Request):
    """Retrieves all pages."""
    pages = await request.app.state.crud.pages.api_list()
    return response_message("success", "Pages retrieved successfully", pages)


async def api_create_page(request: Request):
    """Creates a new page."""
    data = await request.json()
    data = {**data, "slug": sanitize_text(data.get("title"))}
    await request.app.state.crud.pages.api_create(data)
    return response_message("success", "Page created successfully")


async def api_update_page(request: Request):
    """Updates existing page."""
    data = await request.json()
    page_id = request.path_params["id"]
    data = {**data, "slug": sanitize_text(data.get("title"))}
    await request.app.state.crud.pages.api_update(int(page_id), data)
    return response_message("success", "Page updated successfully")


async def api_delete_page(request: Request):
    """Deletes a page based on ID."""
    page_id = request.path_params["id"]
    await request.app.state.crud.pages.delete(int(page_id))
    return response_message("success", "Page deleted successfully")
