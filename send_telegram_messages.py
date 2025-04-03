import requests
import json
from io import BytesIO
import PublicVarible

def send_telegram_messages(text, chat_ids):
    token = "8041867463:AAEUH_w2CYFne521LxNVsuR6hiuqk-75pfQ"
    url = f"https://api.telegram.org/bot{token}/sendMessage"

    responses = {}
    for chat_id in chat_ids:
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML"
        }
        response = requests.post(url, json=payload)
        responses[chat_id] = response.json()
    return responses

chat_ids = [152284556 , 388239785 , 98785822 , 1864188026 , 92618613 , 76616815 , 6958871546 , 38776931 , 7318507893]
send_telegram_messages(f"سلام \n سیگنالهای این بات براساس استراتژی پرایس اکشن تشخیص لگ های قیمت و نواحی BOS پس از آنها می باشد. در صورت خروج قدرتمند قیمت از هر طرف BOS نیز پیامی متناسب نمایش داده خواهد. بیاد داشته باشید هر استراژی چندین شرط دارد که باید برقرار باشد تا بتوان وارد معامله شد ", chat_ids)
