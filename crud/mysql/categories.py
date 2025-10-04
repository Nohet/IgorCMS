class CategoriesCRUD:
    def __init__(self, pool):
        self.pool = pool

    async def list_all_basic(self):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("SELECT id, name FROM `categories`")
                return await cursor.fetchall()

    async def list_all_full(self):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("SELECT id, name, description, created_at, parent_id FROM `categories`")
                return await cursor.fetchall()

    async def get_details(self, category_id: int):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("SELECT name, description FROM `categories` WHERE id = %s", (category_id,))
                return await cursor.fetchone()

    async def create(self, name: str, description: str, parent_id: int | None):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    "INSERT INTO categories(name, description, parent_id) VALUES (%s, %s, %s)",
                    (name, description, parent_id)
                )

    async def update(self, category_id: int, name: str, description: str, parent_id: int | None):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    """UPDATE categories SET name=%s, description=%s, parent_id=%s,
                    updated_at=CURRENT_TIMESTAMP() WHERE id = %s""",
                    (name, description, parent_id, category_id)
                )

    async def delete(self, category_id: int):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("DELETE FROM categories WHERE id = %s", (category_id,))

    async def api_list(self):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("SELECT * FROM categories")
                rows = await cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                return [dict(zip(columns, row)) for row in rows]