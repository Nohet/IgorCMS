class HomepageCRUD:
    def __init__(self, pool):
        self.pool = pool

    async def create_post_draft(self, author_id: int, title: str, slug: str, content: str):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    "INSERT INTO posts(author_id, title, slug, content, status) VALUES (%s, %s, %s, %s, 'draft')",
                    (author_id, title, slug, content)
                )

    async def counts(self):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("SELECT COUNT(*) from posts;")
                post_count = (await cursor.fetchone())[0]
                await cursor.execute("SELECT COUNT(*) from pages;")
                pages_count = (await cursor.fetchone())[0]
                await cursor.execute("SELECT COUNT(*) from comments;")
                comments_count = (await cursor.fetchone())[0]
                return post_count, pages_count, comments_count

    async def last_post(self):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("SELECT created_at, title FROM `posts` GROUP BY created_at DESC LIMIT 1")
                return await cursor.fetchone()

    async def last_comment_with_post(self):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    """SELECT comments.author, comments.content, comments.published_at, posts.title
                            FROM `comments`
                            INNER JOIN posts on posts.id = comments.post_id GROUP BY published_at DESC LIMIT 1;"""
                )
                return await cursor.fetchone()