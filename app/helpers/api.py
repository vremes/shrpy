import flask

def response(status_code: int = 200, status: str = "OK", **kwargs) -> flask.Response:
    """Wrapper for `flask.jsonify`

    :param int status_code: HTTP status code, defaults to `200`
    :param str status: HTTP status message or your own custom status, defaults to `OK`
    :param **kwargs: Arbitrary keyword arguments, these will be added to the returned `Response` as JSON key/value pairs
    :return: flask.jsonify (flask.Response)
    """
    response_dict = {
        "status_code": status_code,
        "status": status,
    }

    for key, value in kwargs.items():
        response_dict[key] = value

    resp = flask.jsonify(response_dict)
    resp.status_code = status_code

    return resp