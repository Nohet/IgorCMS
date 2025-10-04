from starlette.requests import Request
from utils.responses import response_message


async def api_list_categories(request: Request):
    """Retrieves all categories."""
    results = await request.app.state.crud.categories.api_list()
    return response_message("success", "Categories retrieved successfully", results)


async def api_create_category(request: Request):
    """Creates new category."""
    data = await request.json()
    await request.app.state.crud.categories.create(
        data.get("name"), data.get("description"), data.get("parent_id")
    )
    return response_message("success", "Category created successfully")


async def api_update_category(request: Request):
    """Updates existing category."""
    data = await request.json()
    category_id = request.path_params["id"]
    await request.app.state.crud.categories.update(
        int(category_id), data.get("name"), data.get("description"), data.get("parent_id")
    )
    return response_message("success", "Category updated successfully")
