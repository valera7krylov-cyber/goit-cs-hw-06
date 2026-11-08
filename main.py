import json
import socket
import mimetypes
import time

from multiprocessing import Process
from datetime import datetime
from pymongo import MongoClient
from urllib.parse import unquote, urlparse, parse_qs
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"


class MyHttpRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        print(f"Received GET request: {self.path}")

        url_path = unquote(urlparse(self.path).path)

        if url_path == "/":
            url_path = "/index.html"

        if url_path in ("/style.css", "/logo.png"):
            file_path = STATIC_DIR / url_path.lstrip("/")
        else:
            file_path = TEMPLATES_DIR / url_path.lstrip("/")

        try:
            content = file_path.read_bytes()

        except FileNotFoundError:
            self.send_error_page(404)
            return

        content_type, _ = mimetypes.guess_type(file_path)

        if content_type is None:
            content_type = "application/octet-stream"

        if content_type.startswith("text/"):
            content_type += "; charset=utf-8"

        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.end_headers()
        self.wfile.write(content)

    def send_error_page(self, status_code):
        error_page = TEMPLATES_DIR / "error.html"
        content = error_page.read_bytes()

        self.send_response(status_code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(content)

    def do_POST(self):
        url_path = urlparse(self.path).path

        if url_path != "/message":
            self.send_error_page(404)
            return

        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)

        form_data = parse_qs(body.decode("utf-8"))

        username = form_data.get("username", [""])[0].strip()
        message = form_data.get("message", [""])[0].strip()

        if not username or not message:
            self.send_error_page(400)
            return

        message_data = {"username": username, "message": message}

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
            udp_socket.sendto(
                json.dumps(message_data, ensure_ascii=False).encode("utf-8"),
                ("127.0.0.1", 5000),
            )

        self.send_response(303)
        self.send_header("Location", "/message.html")
        self.end_headers()


def run_socket_server():
    mongo_client = MongoClient("mongodb://mongo:27017/", serverSelectionTimeoutMS=5000)

    db = mongo_client["messages_db"]
    collection = db["messages"]

    # Wait until MongoDB is ready
    while True:
        try:
            mongo_client.admin.command("ping")
            print("Connected to MongoDB")
            break

        except Exception as error:
            print(f"Waiting for MongoDB: {error}")
            time.sleep(2)

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server_socket:
        server_socket.bind(("0.0.0.0", 5000))

        print("UDP Socket server started on port 5000")

        while True:
            data, address = server_socket.recvfrom(1024)

            try:
                message_data = json.loads(data.decode("utf-8"))

                document = {
                    "date": str(datetime.now()),
                    "username": message_data["username"],
                    "message": message_data["message"],
                }

                collection.insert_one(document)

                print(f"Message saved: {document}")

            except (ValueError, KeyError) as error:
                print(f"Invalid message received: {error}")


def main():
    socket_process = Process(target=run_socket_server)
    socket_process.start()

    print("Socket server process started")

    server_address = ("0.0.0.0", 3000)
    http_server = HTTPServer(server_address, MyHttpRequestHandler)

    print("HTTP server started on port 3000")

    try:
        http_server.serve_forever()

    except KeyboardInterrupt:
        print("Shutting down servers...")

    finally:
        http_server.server_close()

        socket_process.terminate()
        socket_process.join()


if __name__ == "__main__":
    main()
