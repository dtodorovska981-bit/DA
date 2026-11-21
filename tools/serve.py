#!/usr/bin/env python3
"""Local preview that serves the site the way the Cloudflare Worker does:
clean URLs (/contact -> contact.html), /contact.html -> 307 /contact, and 404.html with a 404 status.

Usage: python3 tools/serve.py [directory] [port]
"""
import http.server, os, sys

ROOT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else ".")
PORT = int(sys.argv[2]) if len(sys.argv) > 2 else 8080


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=ROOT, **k)

    def do_GET(self):
        path = self.path.split("?")[0].split("#")[0]
        query = self.path[len(path):]
        if path.endswith(".html"):
            target = path[:-5]
            if target.endswith("/index"):
                target = target[:-5]
            self.send_response(307)
            self.send_header("Location", (target or "/") + query)
            self.end_headers()
            return
        local = os.path.join(ROOT, path.lstrip("/"))
        if path != "/" and not os.path.exists(local):
            if os.path.isfile(local + ".html"):
                self.path = path + ".html" + query
            else:
                body = open(os.path.join(ROOT, "404.html"), "rb").read()
                self.send_response(404)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return
        super().do_GET()

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    http.server.ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
