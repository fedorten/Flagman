import json
import requests
import os
from http.server import HTTPServer, BaseHTTPRequestHandler

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")


def send_to_telegram(name, contact, message):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        return False

    text = (
        f"📬 *Новая заявка с сайта Flagman*\n\n"
        f"👤 *Имя:* {name}\n"
        f"📞 *Контакт:* {contact}\n"
        f"📝 *Сообщение:* {message}"
    )

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "Markdown"}

    try:
        response = requests.post(url, json=data, timeout=10)
        return response.status_code == 200
    except Exception:
        return False


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        with open("index.html", "rb") as f:
            self.wfile.write(f.read())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_POST(self):
        if self.path == "/api/contact":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")

            try:
                data = json.loads(body)
            except:
                data = {}

            name = data.get("name", "").strip() if data.get("name") else ""
            contact_info = (
                data.get("contact", "").strip() if data.get("contact") else ""
            )
            message = data.get("message", "").strip() if data.get("message") else ""

            if not name or not contact_info:
                self.send_response(400)
                self.send_header("Content-type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(
                    json.dumps(
                        {"success": False, "message": "Заполните обязательные поля"}
                    ).encode()
                )
                return

            if send_to_telegram(name, contact_info, message):
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(
                    json.dumps(
                        {"success": True, "message": "Заявка отправлена!"}
                    ).encode()
                )
            else:
                self.send_response(500)
                self.send_header("Content-type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(
                    json.dumps(
                        {"success": False, "message": "Ошибка отправки"}
                    ).encode()
                )
        else:
            self.send_response(404)
            self.end_headers()


if __name__ == "__main__":
    port = 5000
    print(f"Запуск сервера на http://localhost:{port}")
    server = HTTPServer(("0.0.0.0", port), Handler)
    server.serve_forever()
