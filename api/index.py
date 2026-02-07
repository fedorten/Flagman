from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

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


@app.route("/api/contact", methods=["POST"])
def contact():
    data = request.get_json(silent=True) or {}
    name = data.get("name", "").strip() if data.get("name") else ""
    contact_info = data.get("contact", "").strip() if data.get("contact") else ""
    message = data.get("message", "").strip() if data.get("message") else ""

    if not name or not contact_info:
        return jsonify({"success": False, "message": "Заполните обязательные поля"})

    if send_to_telegram(name, contact_info, message):
        return jsonify({"success": True, "message": "Заявка отправлена!"})
    else:
        return jsonify({"success": False, "message": "Ошибка отправки"})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
