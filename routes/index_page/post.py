from starlette.requests import Request
from starlette.responses import RedirectResponse
from definitions.static import templates


async def post_page(request: Request):
    async with request.app.state.db_pool.acquire() as conn:
        async with conn.cursor() as cursor:
            category = request.path_params['category'] if request.path_params['category'] != "bez-kategorii" else ""
            slug = request.path_params['slug']

            await cursor.execute("""SELECT title, meta_robots, language, navbar_title, image
                                    FROM `pages` WHERE id = 1""")
            index_page_info = await cursor.fetchone()

            await cursor.execute("""SELECT id, navbar_title, slug, display FROM `pages` 
                                    WHERE show_in_menu = 1""")
            pages = await cursor.fetchall()

            await cursor.execute("""SELECT 
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
                                    END""", (slug, category, category))
            post = await cursor.fetchone()

            if not post:
                return RedirectResponse("/")

            form_data = await request.form()

            if form_data:
                author = form_data.get("author")
                email = form_data.get("email")
                content = form_data.get("content")

                post_id = post[7]

                await cursor.execute("INSERT INTO comments (author, email, content, post_id) VALUES (%s, %s, %s, %s)",
                                     (author, email, content, post_id))

            await cursor.execute("SELECT author, content, published_at FROM `comments` WHERE post_id = %s", (post[7],))
            comments = await cursor.fetchall()

            pages_center = [p for p in pages if p[3] == 'center']
            pages_right = [p for p in pages if p[3] == 'right']

            return templates.TemplateResponse("index/post.html", {"request": request,
                                                                  "post": post,
                                                                  "comments": comments,
                                                                  "pages_center": pages_center,
                                                                  "pages_right": pages_right,
                                                                  "info": index_page_info})
