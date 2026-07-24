#!/usr/bin/env python3
"""Local dev server for this repo -- a drop-in replacement for
`python3 -m http.server` with two extras the hotspot editor needs:

1. Caching disabled on every response. `http.server`'s plain SimpleHTTPRequestHandler
   lets the browser cache board/hotspot/image files, which is exactly wrong
   while actively editing one of them (see hotspot-editor.html's own
   auto-load-the-matching-file feature, and just the general "I edited the
   file, why does reloading still show the old one" confusion). Every
   response here gets Cache-Control/Pragma/Expires headers that tell the
   browser never to reuse a cached copy.

2. A small upload endpoint so hotspot-editor.html can save a
   `<board_id>.hotspots.yaml` it just generated STRAIGHT to this repo's
   `hotspots/` folder, instead of the contributor manually downloading it
   from the browser and moving it into place by hand. Deliberately narrow:
   POST to `/__save_hotspots__/<board_id>.hotspots.yaml` with the file's
   raw text as the request body, and that's the ONLY thing this endpoint
   will do -- no arbitrary path, no overwriting anything outside
   `hotspots/`, no other HTTP methods, no other content types. This is a
   local development convenience, not a general file-upload API: it's not
   meant to be exposed on anything but localhost.

Usage (same as http.server's own):
    python3 tools/dev_server.py [port]        # defaults to 8000
Run it from the repo root (same place you'd normally run
`python3 -m http.server`), same as README's "Running it locally" section.
"""
import http.server
import pathlib
import re
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
HOTSPOTS_DIR = REPO_ROOT / "hotspots"

# Matches board.schema.json's own id pattern (^[a-z0-9_]+$) -- the only
# filenames this endpoint will ever agree to write. Deliberately rejects
# anything with a path separator, "..", a leading dot, or characters outside
# that set, so there's no way to escape HOTSPOTS_DIR or overwrite a file
# that isn't a hotspots.yaml this tool itself would generate.
SAVE_PATH_RE = re.compile(r"^/__save_hotspots__/([a-z0-9_]+\.hotspots\.yaml)$")

MAX_UPLOAD_BYTES = 2 * 1024 * 1024  # 2MB -- generous for a hand-drawn hotspots.yaml; just a sanity cap


class DevRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(REPO_ROOT), **kwargs)

    def end_headers(self):
        # Applies to every response this handler sends (GET/HEAD's normal
        # file-serving path, directory listings, redirects, and the POST
        # handler below all funnel through here) -- one place to guarantee
        # nothing ever gets cached.
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()

    def do_POST(self):
        m = SAVE_PATH_RE.match(self.path)
        if not m:
            self.send_error(404, "No such endpoint (only POST /__save_hotspots__/<id>.hotspots.yaml is supported)")
            return
        filename = m.group(1)

        length_header = self.headers.get("Content-Length")
        if length_header is None:
            self.send_error(411, "Content-Length required")
            return
        try:
            length = int(length_header)
        except ValueError:
            self.send_error(400, "Invalid Content-Length")
            return
        if length > MAX_UPLOAD_BYTES:
            self.send_error(413, f"Body too large (max {MAX_UPLOAD_BYTES} bytes)")
            return

        body = self.rfile.read(length)
        try:
            text = body.decode("utf-8")
        except UnicodeDecodeError:
            self.send_error(400, "Body must be UTF-8 text")
            return

        HOTSPOTS_DIR.mkdir(exist_ok=True)
        dest = HOTSPOTS_DIR / filename
        # Write to a temp file in the same directory, then atomically
        # rename over the destination -- avoids ever leaving a half-written
        # hotspots.yaml on disk if the write is interrupted partway through.
        tmp = dest.with_suffix(dest.suffix + ".tmp")
        tmp.write_text(text, encoding="utf-8")
        tmp.replace(dest)

        rel = dest.relative_to(REPO_ROOT)
        print(f"Saved {rel} ({len(body)} bytes)")
        response = f'{{"ok": true, "path": "{rel.as_posix()}"}}'.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(response)))
        self.end_headers()
        self.wfile.write(response)

    # SimpleHTTPRequestHandler's default log_message() is fine as-is (prints
    # each request to stderr) -- no override needed.


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    server = http.server.ThreadingHTTPServer(("", port), DevRequestHandler)
    print(f"Serving {REPO_ROOT} at http://localhost:{port}/ (caching disabled, hotspots/ upload enabled)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
