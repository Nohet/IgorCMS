import secrets

from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.routing import Route, Mount
from starlette.staticfiles import StaticFiles

from crud.mysql import MySQLCRUD
from middleware.authorize import CheckAuthorized
from middleware.authorize_api import CheckAuthorizedApi
from middleware.check_permissions import CheckPermissions
from middleware.csrf import CSRFMiddleware, VerifyCSRFTokenMiddleware
from middleware.setup import CheckSetUp
from plugin_manager.manager import PluginManager

from routes.admin_panel.categories import admin_add_category, admin_view_categories, admin_delete_category, \
    admin_edit_category
from routes.admin_panel.comments import admin_comments_view, admin_delete_comment
from routes.admin_panel.images import admin_image_gallery
from routes.admin_panel.login import admin_login, logout
from routes.admin_panel.homepage import admin_homepage
from routes.admin_panel.pages import admin_show_pages, admin_add_page, admin_delete_page, admin_edit_page
from routes.admin_panel.plugins import admin_show_plugins
from routes.admin_panel.posts import admin_show_posts, admin_add_post, admin_delete_post, admin_edit_post
from routes.admin_panel.settings import admin_settings
from routes.admin_panel.users import admin_users_view, admin_users_add, admin_delete_user
from routes.api.categories import api_list_categories, api_create_category, api_update_category
from routes.api.comments import api_list_comments, api_delete_comment
from routes.api.api_keys import admin_generate_api_key, admin_delete_api_key
from routes.api.pages import api_create_page, api_update_page, api_delete_page, api_get_pages
from routes.api.posts import api_create_post, api_delete_post, api_update_post, api_get_posts
from routes.api.upload_file import api_save_image_from_data_uri
from routes.index_page.custom_page import custom_page
from routes.index_page.index import index_page
from routes.index_page.post import post_page
from routes.robots import robots_txt
from routes.setup import setup_database, setup_add_first_account
from routes.sitemap import sitemap
from utils.config import Config

routes = [
    Mount('/static', app=StaticFiles(directory='static'), name="static"),

    Route("/setup/add-first-account", setup_add_first_account, methods=["GET", "POST"]),
    Route("/setup/database", setup_database, methods=["GET", "POST"]),

    Route("/admin/login", admin_login, methods=["GET", "POST"]),
    Route("/admin/logout", logout, methods=["GET", "POST"]),

    Route("/admin/homepage", admin_homepage, methods=["GET", "POST"]),

    Route("/admin/comments/view", admin_comments_view, methods=["GET"]),
    Route("/admin/comments/delete", admin_delete_comment, methods=["GET"]),

    Route("/admin/users/view", admin_users_view, methods=["GET"]),
    Route("/admin/users/delete", admin_delete_user, methods=["GET"]),
    Route("/admin/users/add", admin_users_add, methods=["GET", "POST"]),

    Route("/admin/posts/view", admin_show_posts, methods=["GET"]),
    Route("/admin/posts/delete", admin_delete_post, methods=["GET"]),
    Route("/admin/posts/add", admin_add_post, methods=["GET", "POST"]),
    Route("/admin/posts/edit", admin_edit_post, methods=["GET", "POST"]),

    Route("/admin/categories/view", admin_view_categories, methods=["GET", "POST"]),
    Route("/admin/categories/edit", admin_edit_category, methods=["GET", "POST"]),
    Route("/admin/categories/delete", admin_delete_category, methods=["GET"]),
    Route("/admin/categories/add", admin_add_category, methods=["GET", "POST"]),

    Route("/admin/pages/view", admin_show_pages, methods=["GET"]),
    Route("/admin/pages/delete", admin_delete_page, methods=["GET"]),
    Route("/admin/pages/add", admin_add_page, methods=["GET", "POST"]),
    Route("/admin/pages/edit", admin_edit_page, methods=["GET", "POST"]),

    Route("/admin/settings", admin_settings, methods=["GET", "POST"]),
    Route("/admin/images/view", admin_image_gallery, methods=["GET"]),

    Route("/admin/plugins/view", admin_show_plugins, methods=["GET"]),
    Route("/admin/settings/generate-api-key", admin_generate_api_key, methods=["GET"]),
    Route("/admin/settings/delete-api-key", admin_delete_api_key, methods=["GET"]),

    Route("/api/upload-file", api_save_image_from_data_uri, methods=["POST"]),
    Route("/api/v1/categories", api_list_categories, methods=["GET"]),
    Route("/api/v1/categories", api_create_category, methods=["POST"]),
    Route("/api/v1/categories/{id:int}", api_update_category, methods=["PUT"]),

    Route("/api/v1/comments", api_list_comments, methods=["GET"]),
    Route("/api/v1/comments/{id:int}", api_delete_comment, methods=["DELETE"]),

    Route("/api/v1/pages", api_get_pages, methods=["GET"]),
    Route("/api/v1/pages", api_create_page, methods=["POST"]),
    Route("/api/v1/pages/{id:int}", api_update_page, methods=["PUT"]),
    Route("/api/v1/pages/{id:int}", api_delete_page, methods=["DELETE"]),

    Route("/api/v1/posts", api_create_post, methods=["POST"]),
    Route("/api/v1/posts/{id:int}", api_update_post, methods=["PUT"]),
    Route("/api/v1/posts/{id:int}", api_delete_post, methods=["DELETE"]),
    Route("/api/v1/posts", api_get_posts, methods=["GET"]),

    Route("/robots.txt", robots_txt, methods=["GET"]),
    Route("/sitemap.xml", sitemap, methods=["GET"]),
    Route("/{slug}", custom_page, methods=["GET", "POST"]),
    Route("/{category}/{slug}", post_page, methods=["GET", "POST"]),

    Route("/", index_page, methods=["GET"]),

]
middleware = [
    Middleware(SessionMiddleware, secret_key=secrets.token_hex(128)),
    Middleware(CheckSetUp),
    Middleware(CheckAuthorized),
    Middleware(CheckPermissions),
    Middleware(CheckAuthorizedApi),
    Middleware(CSRFMiddleware),
    Middleware(VerifyCSRFTokenMiddleware),
]

# Change debug to False in production
app = Starlette(debug=True, routes=[], middleware=middleware)
config = Config()


@app.on_event("startup")
async def startup():
    if not config.exists():
        config.copy_config()

    pm = PluginManager(app, routes)
    await pm.load_plugins()

    app.routes.extend(pm.routes)
    app.state.plugins = pm.plugins

    app.state.crud = MySQLCRUD()
    await app.state.crud.initialize()


@app.on_event("shutdown")
async def shutdown():
    pool = getattr(app.state.crud, "pool", None)
    print(pool)

    if not pool:
        return

    pool.close()
    await pool.wait_closed()

