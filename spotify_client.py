import os
import socket
import threading
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer

import importlib.util
import qrcode
import spotipy
from PIL import Image
from spotipy.oauth2 import SpotifyOAuth

SPOTIFY_SCOPE = "user-read-playback-state"
DEFAULT_CACHE_PATH = os.path.join(os.path.dirname(__file__), ".spotify_cache")
QR_MATRIX_SIZE = (64, 64)

if importlib.util.find_spec("matrix_display"):
    from matrix_display import create_matrix, show_image
else:
    create_matrix = None
    show_image = None


def _get_redirect_uri():
    return (
        os.getenv("SPOTIGOTCHI_REDIRECT_URI")
        or os.getenv("SPOTIPY_REDIRECT_URI")
        or "http://localhost:8888/callback"
    )


def _get_local_ip():
    sock = None
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect(("8.8.8.8", 80))
        return sock.getsockname()[0]
    except OSError:
        return None
    finally:
        if sock:
            sock.close()


def _build_auth_manager():
    return SpotifyOAuth(
        scope=SPOTIFY_SCOPE,
        cache_path=os.getenv("SPOTIGOTCHI_CACHE_PATH", DEFAULT_CACHE_PATH),
        redirect_uri=_get_redirect_uri(),
        open_browser=False,
    )


class _SpotifyAuthHandler(BaseHTTPRequestHandler):
    auth_code = None
    auth_error = None

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)
        if "code" in params:
            _SpotifyAuthHandler.auth_code = params["code"][0]
            message = "Spotify authorization complete. You can close this page."
            self._send_response(200, message)
            return
        if "error" in params:
            _SpotifyAuthHandler.auth_error = params["error"][0]
            message = f"Spotify authorization failed: {_SpotifyAuthHandler.auth_error}"
            self._send_response(400, message)
            return
        self._send_response(404, "Missing authorization code.")

    def log_message(self, format, *args):
        return

    def _send_response(self, status_code, message):
        self.send_response(status_code)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(message.encode("utf-8"))


def _parse_redirect_port(redirect_uri):
    parsed = urllib.parse.urlparse(redirect_uri)
    if parsed.port:
        return parsed.port
    return 443 if parsed.scheme == "https" else 80


def _print_auth_qr(auth_url):
    qr = qrcode.QRCode(border=1)
    qr.add_data(auth_url)
    qr.make(fit=True)
    matrix = qr.get_matrix()
    black = "██"
    white = "  "
    for row in matrix:
        print("".join(black if cell else white for cell in row))

    if create_matrix and show_image:
        qr_image = (
            qr.make_image(fill_color="black", back_color="white")
            .convert("RGB")
            .resize(QR_MATRIX_SIZE, Image.NEAREST)
        )
        matrix_display = create_matrix()
        show_image(matrix_display, qr_image)


def _await_auth_code(redirect_uri):
    _SpotifyAuthHandler.auth_code = None
    _SpotifyAuthHandler.auth_error = None
    server = HTTPServer(("0.0.0.0", _parse_redirect_port(redirect_uri)), _SpotifyAuthHandler)
    thread = threading.Thread(target=server.handle_request)
    thread.daemon = True
    thread.start()
    thread.join(timeout=300)
    server.server_close()
    return _SpotifyAuthHandler.auth_code, _SpotifyAuthHandler.auth_error


def ensure_spotify_token(auth_manager):
    token_info = auth_manager.get_cached_token()
    if token_info:
        return token_info

    auth_url = auth_manager.get_authorize_url()
    redirect_uri = auth_manager.redirect_uri
    local_ip = _get_local_ip()

    print("No Spotify token found.")
    print("Open this URL on your phone to authorize Spotify:")
    _print_auth_qr(auth_url)
    print("Make sure the redirect URI matches exactly what you registered with Spotify.")
    if redirect_uri.startswith("http://localhost"):
        print(
            "Tip: set SPOTIGOTCHI_REDIRECT_URI to "
            f"http://{local_ip or '<device-ip>'}:8888/callback in your environment and "
            "add it to your Spotify app redirect URIs for phone-based login."
        )
    if local_ip:
        print(f"Waiting for Spotify authorization on http://{local_ip}:8888/callback ...")
    code, error = _await_auth_code(redirect_uri)
    if error:
        raise RuntimeError(f"Spotify authorization failed: {error}")
    if not code:
        raise RuntimeError("Timed out waiting for Spotify authorization.")
    return auth_manager.get_access_token(code)


def get_spotify_client():
    auth_manager = _build_auth_manager()
    ensure_spotify_token(auth_manager)
    return spotipy.Spotify(auth_manager=auth_manager)
