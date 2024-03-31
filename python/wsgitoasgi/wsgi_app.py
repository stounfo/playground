from icecream import ic


def application(environ, start_response):
    ic(environ["wsgi.input"].read().decode())
    status = "200 OK"
    headers = [("Content-type", "text/plain")]
    start_response(status, headers)
    return [b"Hello, this is a WSGI app!"]
