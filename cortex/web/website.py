import http.server
import re

class Website:
    def __init__(self):
        self._routing = {}

    def route(self, path):
        def router(f):
            self._routing[path] = f
            return f
        return router

    def get_handler(self, path):
        for option in self._routing:
            match = re.match(option, path)
            if match and len(match.group()) == len(path):
                return self._routing[option], match.groups()

        return None, None



    def run(self, address):
        _self = self
        class ServerRunner(http.server.BaseHTTPRequestHandler):
            def __init__(self, request, client_address, server):
                super().__init__(request, client_address, server)

            def _respond(self, code, body):
                self.send_response(code)
                self.end_headers()
                self.wfile.write(bytearray(body, "utf-8"))


            def do_GET(self):
                handler, args = _self.get_handler(self.path)
                if not handler:
                    self._respond(404, "")
                    return
                self._respond(*handler(*args))

        with http.server.HTTPServer(address, ServerRunner) as httpd:
            httpd.serve_forever()




