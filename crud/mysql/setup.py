import bcrypt

from .schema import create_tables


class SetupCRUD:
    def __init__(self, pool):
        self.pool = pool

    async def get_users_count(self) -> int:
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("SELECT COUNT(id) FROM users")
                result = await cursor.fetchone()

        return result[0] if result else 0

    async def create_initial_user(self, firstname: str, lastname: str, email: str, password: str) -> None:
        password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    """
                        INSERT INTO users (firstname, lastname, email, password_hash, permissions, profile_picture, description)
                        VALUES (%s, %s, %s, %s, 3, '', '')
                    """,
                    (firstname, lastname, email, password_hash)
                )

    async def ensure_schema(self) -> None:
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await create_tables(cursor)
