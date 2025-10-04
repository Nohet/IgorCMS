class SitemapCRUD:
    def __init__(self, pool):
        self.pool = pool

    async def list_posts_with_categories(self):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    """
                        SELECT categories.name, slug, posts.updated_at
                        FROM posts
                        LEFT JOIN categories ON categories.id = posts.category_id
                    """
                )
                return await cursor.fetchall()

    async def list_custom_pages(self):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("SELECT slug, updated_at FROM pages WHERE id != 1")
                return await cursor.fetchall()
