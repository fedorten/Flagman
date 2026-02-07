from flask import Flask, render_template, request, jsonify
import requests
import os

app = Flask(__name__)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

print("=" * 50)
print("TELEGRAM_TOKEN:", "УСТАНОВЛЕН" if TELEGRAM_TOKEN else "НЕ УСТАНОВЛЕН")
print("TELEGRAM_CHAT_ID:", "УСТАНОВЛЕН" if TELEGRAM_CHAT_ID else "НЕ УСТАНОВЛЕН")
print("=" * 50)


def send_to_telegram(name, contact, message):
    print(f"[DEBUG] Попытка отправки: name={name}, contact={contact}")
    
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("[ERROR] TELEGRAM_TOKEN или TELEGRAM_CHAT_ID не настроены!")
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
        print(f"[DEBUG] Ответ Telegram: {response.status_code}")
        if response.status_code != 200:
            print(f"[DEBUG] Текст ответа: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"[ERROR] Исключение: {e}")
        return False


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/contact", methods=["POST"])
def contact():
    data = request.get_json(silent=True) or {}
    name = data.get("name", "").strip() if data.get("name") else ""
    contact_info = data.get("contact", "").strip() if data.get("contact") else ""
    message = data.get("message", "").strip() if data.get("message") else ""

    print(f"[DEBUG] Получена заявка: name={name}, contact={contact_info}")

    if not name or not contact_info:
        return jsonify({"success": False, "message": "Заполните обязательные поля"})

    if send_to_telegram(name, contact_info, message):
        return jsonify({"success": True, "message": "Заявка отправлена!"})
    else:
        return jsonify({"success": False, "message": "Ошибка отправки"})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
