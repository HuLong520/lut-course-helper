from __future__ import annotations

import http.server
import socketserver
import sys
import threading
import time
import webbrowser
from pathlib import Path


HOST = "127.0.0.1"


def resource_path(name: str) -> Path:
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return base / name


class AppRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, directory: str, **kwargs):
        super().__init__(*args, directory=directory, **kwargs)

    def log_message(self, message: str, *args) -> None:
        print(f"[LUTHelper] {self.address_string()} {message % args}")


def main() -> None:
    index = resource_path("index.html")
    if not index.is_file():
        raise FileNotFoundError(f"找不到内嵌页面：{index}")

    def handler(*args, **kwargs):
        return AppRequestHandler(*args, directory=str(index.parent), **kwargs)

    with socketserver.TCPServer((HOST, 0), handler) as server:
        port = server.server_address[1]
        url = f"http://{HOST}:{port}/index.html"
        threading.Thread(target=server.serve_forever, daemon=True).start()

        print("=" * 68)
        print("  抢课助手 WebUI")
        print(f"  本地地址：{url}")
        print("  关闭此终端或按 Ctrl+C 即可退出程序")
        print("=" * 68)
        time.sleep(0.3)
        if not webbrowser.open(url, new=2):
            print(f"[LUTHelper] 未能自动打开浏览器，请手动访问：{url}")

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n[LUTHelper] 正在退出…")
        finally:
            server.shutdown()
            server.server_close()


if __name__ == "__main__":
    main()
