"""Strangler-fig routing: a facade sends migrated paths to the new service and everything else to the legacy one."""
import http.client
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer


def backend(name):
    class H(BaseHTTPRequestHandler):
        def do_GET(self):
            body = f"{name}:{self.path}".encode()
            self.send_response(200)
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *a):
            pass

    return H


MIGRATED = ("/orders",)  # grow this tuple route by route until legacy is empty


def start(handler):
    s = HTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=s.serve_forever, daemon=True).start()
    return s


def get(port, path):
    c = http.client.HTTPConnection("127.0.0.1", port)
    c.request("GET", path)
    return c.getresponse().read().decode()


if __name__ == "__main__":
    legacy, new = start(backend("legacy")), start(backend("new"))

    class Facade(BaseHTTPRequestHandler):
        def do_GET(self):
            target = new if self.path.startswith(MIGRATED) else legacy
            body = get(target.server_port, self.path).encode()
            self.send_response(200)
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *a):
            pass

    facade = start(Facade)
    p = facade.server_port
    r = [get(p, "/orders/1"), get(p, "/customers/9")]
    print(r)
    assert r == ["new:/orders/1", "legacy:/customers/9"]
