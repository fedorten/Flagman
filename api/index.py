import json
import requests
import os

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


def handler(request):
    if request.method == "OPTIONS":
        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type",
            },
        }

    if request.method == "POST" and request.uri == "/api/contact":
        try:
            data = json.loads(request.body) if request.body else {}
        except:
            data = {}

        name = data.get("name", "").strip() if data.get("name") else ""
        contact_info = data.get("contact", "").strip() if data.get("contact") else ""
        message = data.get("message", "").strip() if data.get("message") else ""

        if not name or not contact_info:
            return {
                "statusCode": 400,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                },
                "body": json.dumps(
                    {"success": False, "message": "Заполните обязательные поля"}
                ),
            }

        if send_to_telegram(name, contact_info, message):
            return {
                "statusCode": 200,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                },
                "body": json.dumps({"success": True, "message": "Заявка отправлена!"}),
            }
        else:
            return {
                "statusCode": 500,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                },
                "body": json.dumps({"success": False, "message": "Ошибка отправки"}),
            }

    return {"statusCode": 404, "body": "Not Found"}
