import json
import bcrypt
import aiomysql

from pathlib import Path

from starlette.requests import Request
from starlette.responses import RedirectResponse

from utils.tables import create_tables
from definitions.static import templates

base_dir = Path(__file__).resolve().parent.parent
config_path = base_dir / 'config.json'


async def setup_add_first_account(request: Request):
    form_data = await request.form()

    async with request.app.state.db_pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("SELECT COUNT(id) FROM users")
            account_count = (await cursor.fetchone())[0]

            if account_count > 0:
                return templates.TemplateResponse(request, "setup/already-setted-up.html")

            if form_data.get("pass"):
                firstname = form_data.get("firstname")
                lastname = form_data.get("lastname")
                email = form_data.get("email")
                password = form_data.get("pass")

                try:
                    await cursor.execute(
                        """
                            INSERT INTO users (firstname, lastname, email, password_hash, permissions, profile_picture, description) 
                            VALUES (%s, %s, %s, %s, 3, '', '')
                        """,
                        (firstname, lastname, email,
                         bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8"))
                    )

                    return RedirectResponse("/admin/login")

                except:
                    return templates.TemplateResponse("setup/create-first-account.html", {"request": request, "message":
                        ["Coś poszło nie tak! Upewnij się, że uzupełniłeś wszystkie pola poprawnie."]})

    return templates.TemplateResponse(request, "setup/create-first-account.html")


async def setup_database(request: Request):
    db_json = json.loads(open(config_path).read())

    if not any(value is None for value in db_json["database"].values()):
        return templates.TemplateResponse(request, "setup/already-setted-up.html")

    form_data = await request.form()
    if form_data:
        json_conf = json.loads(open(config_path).read())

        hostname = form_data.get("hostname")
        dbname = form_data.get("dbname")
        username = form_data.get("username")
        dbpass = form_data.get("dbpass")
        port = form_data.get("port")

        try:

            request.app.state.db_pool = await aiomysql.create_pool(
                host=hostname,
                port=int(port),
                user=username,
                password=dbpass,
                db=dbname,
                minsize=0,
                maxsize=100,
                autocommit=True
            )

            async with request.app.state.db_pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await create_tables(cursor)

        except Exception:
            return templates.TemplateResponse("setup/setup.html", {"request": request, "message": [
                "Połączenie z bazą się nie powiodło, upewnij się, że wprowadzasz poprawne dane!"]})

        json_conf["database"]["host"] = hostname
        json_conf["database"]["dbname"] = dbname
        json_conf["database"]["user"] = username
        json_conf["database"]["pass"] = dbpass
        json_conf["database"]["port"] = port

        open(config_path, "w").write(json.dumps(json_conf, indent=4))

        return RedirectResponse("/setup/add-first-account")

    return templates.TemplateResponse("setup/setup.html", {"request": request})
