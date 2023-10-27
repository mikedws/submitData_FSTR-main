from fastapi.responses import JSONResponse


def get_json_response(status_code: int, message: str, id=None):
    return JSONResponse(
        status_code=status_code,
        content={'status': status_code, 'message': message, 'id': id}
    )


class ErrorConnectionServer(Exception):
    def __init__(self, name: str):
        self.name = name
