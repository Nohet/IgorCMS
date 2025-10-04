import json
import secrets

from pathlib import Path

from starlette.requests import Request
from starlette.responses import RedirectResponse

from constants.static import templates

base_dir = Path(__file__).resolve().parent.parent
config_path = base_dir / 'config.json'


async def setup_add_first_account(request: Request):
    form_data = await request.form()
    crud_setup = getattr(request.app.state.crud, "setup", None)

    if crud_setup is None:
        return templates.TemplateResponse(
            "setup/create-first-account.html",
            {"request": request, "message": ["Database connection is not ready yet. Please configure the database first."]}
        )

    account_count = await crud_setup.get_users_count()

    if account_count > 0:
        return templates.TemplateResponse("setup/already-setted-up.html", {"request": request})

    if form_data.get("pass"):
        firstname = form_data.get("firstname")
        lastname = form_data.get("lastname")
        email = form_data.get("email")
        password = form_data.get("pass")

        try:
            await crud_setup.create_initial_user(firstname, lastname, email, password)
            return RedirectResponse("/admin/login")
        except Exception:
            return templates.TemplateResponse(
                "setup/create-first-account.html",
                {"request": request,
                 "message": ["Something went wrong! Make sure you've filled in all the fields correctly."]}
            )

    return templates.TemplateResponse("setup/create-first-account.html", {"request": request})


async def setup_database(request: Request):
    db_json = json.loads(open(config_path).read())

    if not any(value is None for value in db_json["database"].values()):
        return templates.TemplateResponse("setup/already-setted-up.html", {"request": request})

    form_data = await request.form()
    if form_data:
        json_conf = json.loads(open(config_path).read())

        hostname = form_data.get("hostname")
        dbname = form_data.get("dbname")
        username = form_data.get("username")
        dbpass = form_data.get("dbpass")
        port = form_data.get("port")

        try:
            crud = request.app.state.crud
            await crud.configure_database(
                host=hostname,
                port=port,
                user=username,
                password=dbpass,
                database_name=dbname
            )

            crud_setup = getattr(crud, "setup", None)
            if crud_setup is None:
                raise RuntimeError("Setup CRUD is not available after configuring the database")

            await crud_setup.ensure_schema()

        except Exception as e:
            print(e)
            return templates.TemplateResponse("setup/setup.html", {"request": request, "message": [
                "The connection to the database failed, make sure you are entering the correct data!"]})

        json_conf["database"]["host"] = hostname
        json_conf["database"]["database_name"] = dbname
        json_conf["database"]["user"] = username
        json_conf["database"]["password"] = dbpass
        json_conf["database"]["port"] = port
        json_conf["secretKey"] = secrets.token_hex(64)

        open(config_path, "w").write(json.dumps(json_conf, indent=4))

        return RedirectResponse("/setup/add-first-account")

    return templates.TemplateResponse("setup/setup.html", {"request": request})
