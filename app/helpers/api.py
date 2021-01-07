from flask import jsonify

def response(status_code: int = 200, status: str = "OK", **kwargs):
    response_dict = {
        "status_code": status_code,
        "status": status,
    }

    for key, value in kwargs.items():
        response_dict[key] = value

    resp = jsonify(response_dict)
    resp.status_code = status_code

    return resp