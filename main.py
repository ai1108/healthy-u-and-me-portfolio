from flask import Flask, request, abort

from linebot.v3  import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import Configuration, ApiClient, MessagingApi, ReplyMessageRequest, TextMessage
from linebot.v3.webhooks import UserSource
from linebot.v3.webhooks import MessageEvent, TextMessageContent
from linebot.v3.messaging import ButtonsTemplate, TemplateMessage
from linebot.v3.messaging import PostbackAction

import livejson

from datetime import datetime
from utils import calculateBMI
import os

app = Flask(__name__)
# run_with_ngrok(app)
# LINE 聊天機器人的基本設定
configuration = Configuration(access_token = os.environ.get('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.environ.get('LINE_CHANNEL_SECRET'))

datasets = livejson.File('information.json', pretty = True, indent = 4)

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.info("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message = TextMessageContent)
def handle_message(event):
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token = event.reply_token,
                messages=[TextMessage(text = event.message.text)]
            )
        )

@handler.add(MessageEvent, message=TextMessageContent)
def handle_text_message(event):
    text = event.message.text
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)

        '''
        # time %Y/%m/%d, %H:%M:%S (2024/06/08 03:31:12)
        datasets
            userID
                userName
                userHeight         [time, value], [time, value], [time, value] ...
                userWeight         [time, value], [time, value], [time, value] ...
                userBloodPressure  [time, value], [time, value], [time, value] ...
                userBloodSuger     [time, value], [time, value], [time, value] ...
        '''
        if isinstance(event.source, UserSource):
            profile = line_bot_api.get_profile(user_id = event.source.user_id)
            if event.source.user_id not in datasets:
                datasets[event.source.user_id] = {
                    "userName" : profile.display_name,
                    "userHeight" : [],
                    "userWeight" : [],
                    "userBloodSuger" : [],
                    "userBloodPressure" : []
                }


        # --- 我的健康資訊 --- # 1
        if text == '我想查看我的健康資訊':
            buttons_health = ButtonsTemplate(
                title = '我想查看我的健康資訊',
                text = '請點擊以下按鈕觸發健康資訊',
                actions=[
                    PostbackAction(label = '我想輸入身高體重', data='我想輸入身高體重', text='我想輸入身高體重'),
                    PostbackAction(label = '我想輸入血壓血糖', data='我想輸入血壓血糖', text='我想輸入血壓血糖'),
            ])
            template_message = TemplateMessage(
                alt_text = 'Buttons alt text',
                template = buttons_health
            )
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token = event.reply_token,
                    messages = [template_message]
                )
            )

        if text == '我想輸入身高體重':
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[
                        TextMessage(text='身高(單位cm)範例格式為:身高 160\n體重(單位kg)範例格式為:體重 50.4')
                    ]
                )
            )

        if text == '我想輸入血壓血糖':
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[
                        TextMessage(text='血壓(單位mmHg)範例格式為:血壓 120/80\n血糖(單位mg/dl)範例格式為:血糖 100')
                    ]
                )
            )

        if text.startswith("身高"):
            if text.split(" ")[1].isdigit():
                profile = line_bot_api.get_profile(user_id = event.source.user_id)
                datasets[event.source.user_id]['userHeight'].append([datetime.now().strftime("%m/%d/%Y, %H:%M:%S"), text.split(" ")[1]])
                BMItext = calculateBMI(datasets[event.source.user_id])
                line_bot_api.reply_message(
                    ReplyMessageRequest(
                        reply_token = event.reply_token,
                        messages=[
                            TextMessage(text = f'成功輸入，{profile.display_name}的身高為{text.split(" ")[1]}{BMItext}')
                        ]
                    )
                )
            else:
                line_bot_api.reply_message(
                    ReplyMessageRequest(
                        reply_token = event.reply_token,
                        messages=[
                            TextMessage(text='身高(單位cm)範例格式為:身高 160')
                        ]
                    )
                )
        elif text.startswith("體重"):
            try:
                float(text.split(" ")[1])
                profile = line_bot_api.get_profile(user_id = event.source.user_id)
                datasets[event.source.user_id]['userWeight'].append([datetime.now().strftime("%m/%d/%Y, %H:%M:%S"), text.split(" ")[1]])
                BMItext = calculateBMI(datasets[event.source.user_id])
                line_bot_api.reply_message(
                    ReplyMessageRequest(
                        reply_token = event.reply_token,
                        messages=[
                            TextMessage(text = f'成功輸入，{profile.display_name}的體重為{text.split(" ")[1]}{BMItext}'),
                        ]
                    )
                )
            except:
                line_bot_api.reply_message(
                    ReplyMessageRequest(
                        reply_token = event.reply_token,
                        messages=[
                            TextMessage(text='體重(單位kg)範例格式為:體重 50.4')
                        ]
                    )
                )
        elif text.startswith("血壓"):
            if ("/" in text.split(" ")[1]) and (text.split(" ")[1].split("/")[0].isdigit) and (text.split(" ")[1].split("/")[1].isdigit):
                profile = line_bot_api.get_profile(user_id = event.source.user_id)
                datasets[event.source.user_id]['userBloodPressure'].append([datetime.now().strftime("%m/%d/%Y, %H:%M:%S"), text.split(" ")[1]])
                line_bot_api.reply_message(
                    ReplyMessageRequest(
                        reply_token = event.reply_token,
                        messages=[
                            TextMessage(text = f'成功輸入，{profile.display_name}的血壓為{text.split(" ")[1]}')
                        ]
                    )
                )
            else:
                line_bot_api.reply_message(
                    ReplyMessageRequest(
                        reply_token = event.reply_token,
                        messages=[
                            TextMessage(text='血壓(單位mmHg)範例格式為:血壓 120/80')
                        ]
                    )
                )
        elif text.startswith("血糖"):
            if text.split(" ")[1].isdigit():
                profile = line_bot_api.get_profile(user_id = event.source.user_id)
                datasets[event.source.user_id]['userBloodSuger'].append([datetime.now().strftime("%m/%d/%Y, %H:%M:%S"), text.split(" ")[1]])
                line_bot_api.reply_message(
                    ReplyMessageRequest(
                        reply_token = event.reply_token,
                        messages=[
                            TextMessage(text = f'成功輸入，{profile.display_name}的血糖為{text.split(" ")[1]}')
                        ]
                    )
                )
            else:
                line_bot_api.reply_message(
                    ReplyMessageRequest(
                        reply_token = event.reply_token,
                        messages=[
                            TextMessage(text='血糖(單位mg/dl)範例格式為:血糖 100')
                        ]
                    )
                )

if __name__ == "__main__":
    app.run()
