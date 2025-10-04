class PagesCRUD:
    def __init__(self, pool):
        self.pool = pool

    async def get_index_page_for_index(self):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    """SELECT title, image, meta_title, meta_description,
                                    meta_keywords, meta_robots, language, navbar_title
                                    FROM `pages` WHERE id = 1"""
                )
                return await cursor.fetchone()

    async def get_index_meta(self):
        return await self.get_index_page_for_index()

    async def get_menu_pages(self):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("SELECT id, navbar_title, slug, display FROM `pages` WHERE show_in_menu = 1")
                return await cursor.fetchall()

    async def get_by_slug(self, slug: str):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    """SELECT title, image, meta_title, meta_description,
                                    meta_keywords, meta_robots, language, content, redirect_url
                                    FROM `pages` WHERE slug = %s""",
                    (slug,)
                )
                return await cursor.fetchone()

    async def get_index_navbar_title(self):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("SELECT navbar_title FROM `pages` WHERE id = 1")
                return await cursor.fetchone()

    async def admin_list_pages(self):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    """SELECT pages.id, pages.slug, pages.title,
                                    CONCAT(users.firstname, ' ', users.lastname), pages.created_at,
                                    pages.meta_title, pages.meta_description, pages.meta_keywords,
                                    pages.meta_robots, pages.redirect_url, pages.parent_id,
                                    pages.show_in_menu, categories.name  FROM `pages`
                                    LEFT JOIN users ON author_id = users.id
                                    LEFT JOIN categories ON category_id = categories.id
                                    WHERE pages.id != 1"""
                )
                return await cursor.fetchall()

    async def admin_get_details(self, page_id: int):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    """
            SELECT title, content, navbar_title,
            meta_title, meta_description, meta_keywords,
            redirect_url, language, image
            FROM `pages` WHERE id = %s
            """,
                    (page_id,)
                )
                return await cursor.fetchone()

    async def admin_update(self, page_id: int, *, title: str, slug: str, content: str | None,
                            navbar_title: str, meta_title: str | None, meta_description: str | None,
                            meta_keywords: str | None, redirect_url: str | None, language: str,
                            display: str, meta_robots: str, category_id: int | None,
                            show_in_menu: int, image: str | None):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    """UPDATE pages SET title=%s,slug=%s,content=%s,navbar_title=%s,
                meta_title=%s,meta_description=%s,meta_keywords=%s,redirect_url=%s,
                language=%s,display=%s,meta_robots=%s,category_id=%s,show_in_menu=%s,
                image=%s,updated_at=CURRENT_TIMESTAMP()
                WHERE id = %s""",
                    (
                        title, slug, content, navbar_title, meta_title, meta_description, meta_keywords,
                        redirect_url, language, display, meta_robots, category_id, show_in_menu, image, page_id
                    )
                )

    async def admin_create(self, *, slug: str, image: str | None, title: str, content: str | None,
                           display: str, author_id: int, navbar_title: str, meta_title: str | None,
                           meta_description: str | None, meta_keywords: str | None, meta_robots: str,
                           language: str, redirect_url: str | None, show_in_menu: int, category_id: int | None):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    """INSERT INTO pages (slug, image, title, content, display, author_id,
                                        navbar_title, meta_title, meta_description, meta_keywords, meta_robots,
                                         language, redirect_url, show_in_menu, category_id)
                                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                    (
                        slug, image, title, content, display, author_id, navbar_title, meta_title, meta_description,
                        meta_keywords, meta_robots, language, redirect_url, show_in_menu, category_id
                    )
                )

    async def delete(self, page_id: int):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("DELETE FROM pages WHERE id = %s", (page_id,))

    async def api_list(self):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("SELECT * FROM pages")
                rows = await cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                return [dict(zip(columns, row)) for row in rows]

    async def api_create(self, payload: dict):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    """
                INSERT INTO pages (slug, image, title, content, display, author_id, created_at, updated_at, navbar_title, meta_title, meta_description, meta_keywords, meta_robots, language, redirect_url, parent_id, show_in_menu, category_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
                    (
                        payload.get("slug"), payload.get("image"), payload.get("title"), payload.get("content"),
                        payload.get("display"), payload.get("author_id"), payload.get("created_at"),
                        payload.get("updated_at"), payload.get("navbar_title"), payload.get("meta_title"),
                        payload.get("meta_description"), payload.get("meta_keywords"), payload.get("meta_robots"),
                        payload.get("language"), payload.get("redirect_url"), payload.get("parent_id"),
                        payload.get("show_in_menu"), payload.get("category_id")
                    )
                )

    async def api_update(self, page_id: int, payload: dict):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    """
                UPDATE pages
                SET slug = %s, image = %s, title = %s, content = %s, display = %s, author_id = %s, updated_at = %s, navbar_title = %s, meta_title = %s, meta_description = %s, meta_keywords = %s, meta_robots = %s, language = %s, redirect_url = %s, parent_id = %s, show_in_menu = %s, category_id = %s
                WHERE id = %s
            """,
                    (
                        payload.get("slug"), payload.get("image"), payload.get("title"), payload.get("content"),
                        payload.get("display"), payload.get("author_id"), payload.get("updated_at"),
                        payload.get("navbar_title"), payload.get("meta_title"), payload.get("meta_description"),
                        payload.get("meta_keywords"), payload.get("meta_robots"), payload.get("language"),
                        payload.get("redirect_url"), payload.get("parent_id"), payload.get("show_in_menu"),
                        payload.get("category_id"), page_id
                    )
                )