class CommentsCRUD:
    def __init__(self, pool):
        self.pool = pool

    async def delete(self, comment_id: int):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("DELETE FROM comments WHERE id = %s", (comment_id,))

    async def list_with_posts_for_admin(self):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    """SELECT comments.author, comments.content, posts.title, comments.published_at, comments.id
                       FROM `comments`
                       INNER JOIN posts on posts.id = comments.post_id GROUP BY published_at;"""
                )
                return await cursor.fetchall()

    async def list_for_post(self, post_id: int):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    "SELECT author, content, published_at FROM `comments` WHERE post_id = %s",
                    (post_id,)
                )
                return await cursor.fetchall()

    async def add_comment(self, author: str, email: str, content: str, post_id: int):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    "INSERT INTO comments (author, email, content, post_id) VALUES (%s, %s, %s, %s)",
                    (author, email, content, post_id)
                )

    async def api_list(self):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("SELECT * FROM comments")
                rows = await cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                return [dict(zip(columns, row)) for row in rows]