import aiomysql
from pydantic import ValidationError

from models.config import ConfigModel, MySQLServerModel
from utils.config import Config
from .auth import AuthCRUD
from .categories import CategoriesCRUD
from .comments import CommentsCRUD
from .homepage import HomepageCRUD
from .pages import PagesCRUD
from .posts import PostsCRUD
from .settings import SettingsCRUD
from .users import UsersCRUD
from .setup import SetupCRUD
from .sitemap import SitemapCRUD


class MySQLCRUD:
    def __init__(self):
        self.settings = None
        self.posts = None
        self.pages = None
        self.homepage = None
        self.comments = None
        self.categories = None
        self.auth = None
        self.users = None
        self.setup = None
        self.sitemap = None

        self.config = Config()
        self.pool = None

    async def initialize(self):
        initialized = await self.initialize_pool()
        if not initialized:
            return
        self.initialize_crud()

    async def initialize_pool(self) -> bool:
        try:
            config = self.config.read_config(ConfigModel, MySQLServerModel)
        except (ValidationError, FileNotFoundError, TypeError, ValueError):
            return False

        self.pool = await aiomysql.create_pool(
            host=config.database.host,
            port=config.database.port,
            user=config.database.user,
            password=config.database.password,
            db=config.database.database_name,
            minsize=0,
            maxsize=100,
            autocommit=True
        )

        return True

    def initialize_crud(self):
        self.auth = AuthCRUD(self.pool)
        self.categories = CategoriesCRUD(self.pool)
        self.comments = CommentsCRUD(self.pool)
        self.homepage = HomepageCRUD(self.pool)
        self.pages = PagesCRUD(self.pool)
        self.posts = PostsCRUD(self.pool)
        self.settings = SettingsCRUD(self.pool)
        self.users = UsersCRUD(self.pool)
        self.setup = SetupCRUD(self.pool)
        self.sitemap = SitemapCRUD(self.pool)

    async def configure_database(self, *, host: str, port: int | str, user: str, password: str, database_name: str):
        new_pool = await aiomysql.create_pool(
            host=host,
            port=int(port),
            user=user,
            password=password,
            db=database_name,
            minsize=0,
            maxsize=100,
            autocommit=True
        )

        if self.pool:
            self.pool.close()
            await self.pool.wait_closed()

        self.pool = new_pool
        self.initialize_crud()
