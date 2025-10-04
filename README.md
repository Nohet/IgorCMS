## What is it?

IgorCMS is a CMS (Content Management System) written in Python using the Starlette framework and a MySQL/MariaDB database but other databases can be implemented easily.

---

## Screenshot

![Screenshot showing the admin panel](https://i.imgur.com/RVUjRb1.png)

---

## How to run my CMS?

Recommended Python version: <3.10

1. Install the required libraries:

   - `pip install -r requirements.txt`

2. Run the database (MySQL/MariaDB).

3. Create an empty database that will be used by the CMS.
   The name of the database should be provided during the first setup.

4. Start the CMS. By default, the CMS runs in debug mode. To disable it, change `debug=True` to `debug=False` in the `app.py` file:

   - `uvicorn app:app` or `python -m uvicorn app:app`

5. Open your browser and go to the CMS website.
   If the CMS is not configured, a form will appear allowing you to perform the setup and create the first user account.

---

## Features of my CMS:

- Create, edit, and delete pages.
- Create, edit, and delete categories.
- Create, edit, and delete posts.
- Add comments to posts.
- WYSIWYG (What You See Is What You Get) editor:
  - Supports text formatting (headings, lists, quotes, etc.).
  - Preview the draft before publishing.
- User registration and login.
- Role and permission system (e.g., author, administrator).
- Change passwords.
- File storage and organization (images, videos, documents).
- Manage meta tags (title, description, keywords).
- SEO-friendly URLs.
- Automatic generation of sitemap (`sitemap.xml`).
- Security:
  - Authentication via JWT.
  - Protection against XSS and CSRF attacks.
  - Password hashing with bcrypt.
- Plugin support.
- API for headless CMS (without the graphical panel).
- Asynchronous query handling.

---