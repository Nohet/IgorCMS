from starlette.responses import JSONResponse


def response_message(status: str, message: str, data=None, code=200):
    return JSONResponse({"status": status, "message": message, "data": data}, status_code=code)
