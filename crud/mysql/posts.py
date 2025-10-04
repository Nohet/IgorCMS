class PostsCRUD:
    def __init__(self, pool):
        self.pool = pool

    async def create_draft(self, *, author_id: int, title: str, slug: str, content: str):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    "INSERT INTO posts(author_id, title, slug, content, status) VALUES (%s, %s, %s, %s, 'draft')",
                    (author_id, title, slug, content)
                )

    async def count_posts(self):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("SELECT COUNT(*) from posts;")
                return (await cursor.fetchone())[0]

    async def last_post(self):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("SELECT created_at, title FROM `posts` GROUP BY created_at DESC LIMIT 1")
                return await cursor.fetchone()

    async def admin_list_posts(self):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    """SELECT posts.title,
    CONCAT(users.firstname, " ", users.lastname) AS author_name,
    COALESCE(categories.name, NULL) AS category_name,
    posts.tags,
    posts.updated_at,
    posts.status,
    posts.id,
    posts.slug
    FROM posts
    LEFT JOIN users ON posts.author_id = users.id
    LEFT JOIN categories ON posts.category_id = categories.id;"""
                )
                return await cursor.fetchall()

    async def admin_get_details(self, post_id: int):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    "SELECT title, content, excerpt, tags, featured_image FROM `posts` WHERE id = %s",
                    (post_id,)
                )
                return await cursor.fetchone()

    async def admin_update(self, post_id: int, *, title: str, slug: str, content: str, excerpt: str | None,
                           tags: str | None, featured_image: str | None, comments_enabled: int,
                           category_id: int | None, status: str, editor_id: int):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    """
                UPDATE posts SET title=%s, slug=%s,content=%s,
                excerpt=%s,tags=%s,featured_image=%s,comments_enabled=%s,
                category_id=%s,status=%s, updated_at=CURRENT_TIMESTAMP(),editor_id=%s
                WHERE id = %s
                """,
                    (
                        title, slug, content, excerpt, tags, featured_image, comments_enabled, category_id, status,
                        editor_id, post_id
                    )
                )

    async def admin_delete(self, post_id: int):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("DELETE FROM posts WHERE id = %s", (post_id,))

    async def admin_create(self, *, slug: str, title: str, content: str, excerpt: str | None, author_id: int,
                           status: str, tags: str | None, featured_image: str | None, comments_enabled: int,
                           category_id: int | None):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    """INSERT INTO posts(slug, title, content, excerpt, author_id, status, tags, featured_image, comments_enabled, category_id)
                                VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                    (
                        slug, title, content, excerpt, author_id, status, tags, featured_image, comments_enabled,
                        category_id
                    )
                )

    async def list_published_for_index(self):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    """SELECT posts.title, posts.updated_at, posts.featured_image,
                                    categories.name, posts.id, posts.slug, status
                                    FROM `posts`
                                    LEFT JOIN categories ON categories.id = posts.category_id
                                    HAVING status = 'published'
                                    ORDER BY posts.updated_at DESC"""
                )
                return await cursor.fetchall()

    async def get_with_category_author_by_slug(self, slug: str, normalized_category_name: str):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    """SELECT
                                    categories.name, posts.title, CONCAT(users.firstname, ' ', users.lastname),
                                    posts.updated_at, posts.excerpt, posts.content,
                                    featured_image, posts.id, posts.tags
                                    FROM posts
                                    LEFT JOIN users ON posts.author_id = users.id
                                    LEFT JOIN categories ON posts.category_id = categories.id
                                    WHERE posts.slug = %s AND
                                    CASE
                                        WHEN %s = '' THEN categories.name IS NULL
                                        ELSE REPLACE(LOWER(categories.name), ' ', '-') = %s
                                    END""",
                    (slug, normalized_category_name, normalized_category_name)
                )
                return await cursor.fetchone()

    async def api_list(self):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("SELECT * FROM posts")
                rows = await cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                return [dict(zip(columns, row)) for row in rows]

    async def api_create(self, payload: dict):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    """
                INSERT INTO posts (slug, title, content, excerpt, author_id, editor_id, created_at, updated_at, published_at, status, tags, featured_image, comments_enabled, category_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
                    (
                        payload.get("slug"), payload.get("title"), payload.get("content"), payload.get("excerpt"),
                        payload.get("author_id"), payload.get("editor_id"), payload.get("created_at"),
                        payload.get("updated_at"), payload.get("published_at"), payload.get("status"),
                        payload.get("tags"), payload.get("featured_image"), payload.get("comments_enabled"),
                        payload.get("category_id")
                    )
                )

    async def api_update(self, post_id: int, payload: dict):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    """
                UPDATE posts
                SET slug = %s, title = %s, content = %s, excerpt = %s, author_id = %s, editor_id = %s, updated_at = %s, published_at = %s, status = %s, tags = %s, featured_image = %s, comments_enabled = %s, category_id = %s
                WHERE id = %s
            """,
                    (
                        payload.get("slug"), payload.get("title"), payload.get("content"), payload.get("excerpt"),
                        payload.get("author_id"), payload.get("editor_id"), payload.get("updated_at"),
                        payload.get("published_at"), payload.get("status"), payload.get("tags"),
                        payload.get("featured_image"), payload.get("comments_enabled"), payload.get("category_id"),
                        post_id
                    )
                )