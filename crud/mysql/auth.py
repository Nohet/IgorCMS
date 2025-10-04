import bcrypt


class AuthCRUD:
    def __init__(self, pool):
        self.pool = pool

    async def login(self, email: str, password: str):
        if len(email) == 0 or len(password) == 0:
            return False

        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    "SELECT password_hash, id, firstname, lastname, permissions from users WHERE email = %s",
                    (email,))
                row = await cursor.fetchone()

                if not row:
                    return False

                password_hash, user_id, firstname, lastname, permissions = row

                if bcrypt.checkpw(bytes(password.encode("utf-8")), bytes(password_hash.encode("utf-8"))):
                    return {
                        "password_hash": password_hash,
                        "user_id": user_id,
                        "firstname": firstname,
                        "lastname": lastname,
                        "permissions": permissions,
                    }

                return False
