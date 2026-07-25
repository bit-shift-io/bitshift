#!/usr/bin/env python3

import http.server
import logging
import os
import sys
import threading
import time
import webbrowser

from jinja2 import Environment, FileSystemLoader
from staticjinja import Site
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
SEARCHPATH = os.path.join(PROJECT_ROOT, "templates")
OUTPATH = os.path.join(PROJECT_ROOT, "public")
PORT = 8000
DEBOUNCE_SECONDS = 0.3

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())

_build_lock = threading.Lock()
_build_count = 0

LIVE_RELOAD_SCRIPT = b"""
<script>
(function() {
  var lastBuild = null;
  setInterval(function() {
    fetch("/__dev__/last-build").then(function(r) { return r.text(); }).then(function(text) {
      if (lastBuild === null) {
        lastBuild = text;
      } else if (text !== lastBuild) {
        location.reload();
      }
    });
  }, 1000);
})();
</script>
"""


class RelEnvironment(Environment):
    """Override join_path() to enable relative template paths."""
    def join_path(self, template, parent):
        return os.path.join(os.path.dirname(parent), template)


class MySite(Site):
    def is_static(self, filename):
        return not filename.endswith(".html") and not filename.endswith(".css")


def build():
    environment = RelEnvironment(
        loader=FileSystemLoader(searchpath=SEARCHPATH, encoding="utf8", followlinks=True)
    )
    site = MySite(environment=environment, outpath=OUTPATH, searchpath=SEARCHPATH, encoding="utf8")
    site.render(use_reloader=False)


def safe_build():
    global _build_count
    try:
        build()
    except Exception:
        logger.exception("Build failed; keeping the last successful build")
        return False
    with _build_lock:
        _build_count += 1
    return True


def get_build_count():
    with _build_lock:
        return _build_count


class RebuildHandler(FileSystemEventHandler):
    """Debounces filesystem events and triggers a rebuild after a quiet period."""

    def __init__(self, on_rebuild):
        self._on_rebuild = on_rebuild
        self._timer = None
        self._lock = threading.Lock()

    def on_any_event(self, event):
        with self._lock:
            if self._timer is not None:
                self._timer.cancel()
            self._timer = threading.Timer(DEBOUNCE_SECONDS, self._fire)
            self._timer.daemon = True
            self._timer.start()

    def _fire(self):
        logger.info("Change detected, rebuilding...")
        self._on_rebuild()


def start_watching(on_rebuild):
    handler = RebuildHandler(on_rebuild)
    observer = Observer()
    observer.schedule(handler, SEARCHPATH, recursive=True)
    observer.start()
    return observer


class DevRequestHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self._serve()

    def do_HEAD(self):
        self._serve(head_only=True)

    def _serve(self, head_only=False):
        url_path = self.path.split("?", 1)[0]

        if url_path == "/__dev__/last-build":
            body = str(get_build_count()).encode("utf8")
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            if not head_only:
                self.wfile.write(body)
            return

        path = self._resolve_path(url_path)
        if path is None:
            self.send_error(404)
            return

        with open(path, "rb") as f:
            body = f.read()

        content_type = self._content_type(path)
        if content_type.startswith("text/html"):
            body = body.replace(b"</body>", LIVE_RELOAD_SCRIPT + b"</body>", 1)

        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if not head_only:
            self.wfile.write(body)

    def _resolve_path(self, url_path):
        if url_path == "/":
            url_path = "/index.html"

        candidate = os.path.normpath(os.path.join(OUTPATH, url_path.lstrip("/")))
        if not candidate.startswith(OUTPATH):
            return None

        if os.path.isfile(candidate):
            return candidate

        with_html = candidate + ".html"
        if os.path.isfile(with_html):
            return with_html

        return None

    def _content_type(self, path):
        if path.endswith(".html"):
            return "text/html; charset=utf-8"
        if path.endswith(".css"):
            return "text/css; charset=utf-8"
        if path.endswith(".js"):
            return "application/javascript; charset=utf-8"
        if path.endswith(".json"):
            return "application/json; charset=utf-8"
        if path.endswith(".svg"):
            return "image/svg+xml"
        if path.endswith(".png"):
            return "image/png"
        if path.endswith(".jpg") or path.endswith(".jpeg"):
            return "image/jpeg"
        if path.endswith(".ico"):
            return "image/x-icon"
        return "application/octet-stream"

    def log_message(self, format, *args):
        logger.info("%s - %s", self.address_string(), format % args)


def open_browser(url):
    opened = False
    try:
        opened = webbrowser.open(url)
    except webbrowser.Error:
        opened = False

    if not opened:
        logger.info("Open your browser to: %s", url)


def serve():
    server = http.server.HTTPServer(("localhost", PORT), DevRequestHandler)
    url = "http://localhost:%d" % PORT
    logger.info("Serving %s at %s", OUTPATH, url)
    open_browser(url)
    server.serve_forever()


if __name__ == "__main__":
    safe_build()
    start_watching(safe_build)
    serve()
