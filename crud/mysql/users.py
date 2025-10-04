import bcrypt


class UsersCRUD:
	def __init__(self, pool):
		self.pool = pool

	async def delete(self, user_id: int):
		async with self.pool.acquire() as conn:
			async with conn.cursor() as cursor:
				await cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))

	async def admin_list_users(self):
		async with self.pool.acquire() as conn:
			async with conn.cursor() as cursor:
				await cursor.execute(
					"""SELECT users.firstname, users.lastname, users.email, permissions, COUNT(posts.id), users.id
							FROM users
							LEFT JOIN posts
							ON posts.author_id = users.id
							GROUP BY users.id;"""
				)
				return await cursor.fetchall()

	async def create(self, firstname: str, lastname: str, email: str, password: str, permissions: int):
		password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
		async with self.pool.acquire() as conn:
			async with conn.cursor() as cursor:
				await cursor.execute(
					"INSERT INTO USERS(firstname, lastname, email, password_hash, permissions) VALUES(%s, %s, %s, %s, %s)",
					(firstname, lastname, email, password_hash, int(permissions))
				)

	async def update_password_if_old_matches(self, user_id: int, old_hash: str, new_password: str):
		new_hash = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
		async with self.pool.acquire() as conn:
			async with conn.cursor() as cursor:
				await cursor.execute(
					"UPDATE users SET password_hash = %s WHERE password_hash = %s and id = %s",
					(new_hash, old_hash, user_id)
				)
