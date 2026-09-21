from flask import Flask, request, abort
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import Configuration, ApiClient, MessagingApi, ReplyMessageRequest, TextMessage
from linebot.v3.webhooks import UserSource, MessageEvent, TextMessageContent, PostbackEvent
from linebot.v3.messaging import ButtonsTemplate, TemplateMessage, PostbackAction

import livejson
from datetime import datetime
import os

app = Flask(__name__)

configuration = Configuration(access_token=os.environ.get('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.environ.get('LINE_CHANNEL_SECRET'))

datasets = livejson.File('information.json', pretty=True, indent=4)

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.info("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    text = event.message.text
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)

        if isinstance(event.source, UserSource):
            profile = line_bot_api.get_profile(user_id=event.source.user_id)
            if event.source.user_id not in datasets:
                datasets[event.source.user_id] = {
                    "userName": profile.display_name,
                    "mealRecords": {
                        "breakfast": [],
                        "lunch": [],
                        "dinner": [],
                        "other": []
                    }
                }

        if text == '我想追蹤我的飲食情況':
            buttons_health = ButtonsTemplate(
                title='飲食追蹤',
                text='請選擇要記錄的餐點',
                actions=[
                    PostbackAction(label='早餐', data='meal:breakfast', text='早餐'),
                    PostbackAction(label='午餐', data='meal:lunch', text='午餐'),
                    PostbackAction(label='晚餐', data='meal:dinner', text='晚餐'),
                    PostbackAction(label='其他', data='meal:other', text='其他'),
                    PostbackAction(label='查看目前攝取總量', data='view_total', text='查看目前攝取總量')
                ]
            )
            template_message = TemplateMessage(
                alt_text='Buttons alt text',
                template=buttons_health
            )
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[template_message]
                )
            )
        elif text.startswith("早餐") or text.startswith("午餐") or text.startswith("晚餐") or text.startswith("其他"):
            meal_type = 'breakfast' if text.startswith("早餐") else 'lunch' if text.startswith("午餐") else 'dinner' if text.startswith("晚餐") else 'other'
            datasets[event.source.user_id]['mealRecords'][meal_type].append({
                "timestamp": datetime.now().strftime("%Y/%m/%d %H:%M:%S"),
                "description": text
            })
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[
                        TextMessage(text=f'成功記錄 {meal_type} 攝取: {text}')
                    ]
                )
            )
        elif text == '查看目前攝取總量':
            total_records = sum(len(meals) for meals in datasets[event.source.user_id]['mealRecords'].values())
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[
                        TextMessage(text=f'目前的攝取總量: {total_records} 條記錄')
                    ]
                )
            )

@handler.add(PostbackEvent)
def handle_postback(event):
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)

        if event.postback.data.startswith("meal:"):
            meal_type = event.postback.data.split(":")[1]
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[
                        TextMessage(text=f'請輸入{meal_type}的攝取內容，範例格式: {meal_type} 蘋果 100g')
                    ]
                )
            )
        elif event.postback.data == 'view_total':
            total_records = sum(len(meals) for meals in datasets[event.source.user_id]['mealRecords'].values())
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[
                        TextMessage(text=f'目前的攝取總量: {total_records} 條記錄')
                    ]
                )
            )

if __name__ == "__main__":
    app.run()
