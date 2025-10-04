class SettingsCRUD:
    def __init__(self, pool):
        self.pool = pool

    async def update_general_settings(self, *, site_name: str, site_icon: str | None, meta_title: str | None,
                                      meta_desc: str | None, meta_keywords: str | None, meta_robots: str,
                                      site_language: str):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    """UPDATE pages
                set title = %s, image = %s, meta_title = %s,
                meta_description = %s, meta_keywords = %s,
                meta_robots = %s, language = %s,
                updated_at = CURRENT_TIMESTAMP() WHERE id = 1;""",
                    (site_name, site_icon, meta_title, meta_desc, meta_keywords, meta_robots, site_language)
                )

    async def get_index_page_basic(self):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    """SELECT title, image, meta_title, meta_description, meta_keywords, language
                                FROM `pages`"""
                )
                return await cursor.fetchone()

    async def list_api_keys(self, user_id: int):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("SELECT api_key FROM api_keys WHERE user_id = %s", (user_id,))
                return await cursor.fetchall()

    async def create_api_key(self, user_id: int, api_key: str):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("INSERT INTO api_keys(user_id, api_key) VALUES (%s, %s)", (user_id, api_key))

    async def delete_api_key(self, api_key: str):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("DELETE FROM api_keys WHERE api_key = %s", (api_key,))