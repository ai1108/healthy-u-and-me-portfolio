import logging
import random
import os
from flask import Flask, request, abort

from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import Configuration, ApiClient, MessagingApi, ReplyMessageRequest, TextMessage, ButtonsTemplate, TemplateMessage, PostbackAction
from linebot.v3.webhooks import UserSource, MessageEvent, TextMessageContent

app = Flask(__name__)

# LINE 聊天機器人的基本設定
configuration = Configuration(access_token=os.environ.get('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.environ.get('LINE_CHANNEL_SECRET'))

questions = [
    {"question": "健康的均衡飲食應包括哪三類食物？", "options": {"A": "碳水化合物、蛋白質、脂肪", "B": "碳水化合物、維他命、糖", "C": "纖維、脂肪、蛋白質"}, "answer": "A"},
    {"question": "每日建議攝取多少克的纖維？", "options": {"A": "10-15克", "B": "20-35克", "C": "50-60克"}, "answer": "B"},
    {"question": "哪種運動最有助於心肺功能的提升？", "options": {"A": "舉重", "B": "跑步", "C": "跳舞"}, "answer": "B"},
    {"question": "成人每天應該睡多久以維持健康？", "options": {"A": "5-6小時", "B": "7-8小時", "C": "9-10小時"}, "answer": "B"},
    {"question": "以下哪種食物富含抗氧化劑？", "options": {"A": "蘋果", "B": "麵包", "C": "豬肉"}, "answer": "A"},
    {"question": "保持身體健康，每周應至少進行多少分鐘的中等強度運動？", "options": {"A": "75分鐘", "B": "150分鐘", "C": "225分鐘"}, "answer": "B"},
    {"question": "維他命C的主要功能是什麼？", "options": {"A": "促進視力", "B": "增強免疫系統", "C": "幫助骨骼生長"}, "answer": "B"},
    {"question": "過量攝取鹽分可能引起什麼健康問題？", "options": {"A": "高血壓", "B": "低血壓", "C": "低血糖"}, "answer": "A"},
    {"question": "哪種食物含有豐富的Omega-3脂肪酸？", "options": {"A": "雞肉", "B": "魚", "C": "豆腐"}, "answer": "B"},
    {"question": "喝足夠的水對於維持哪種身體機能特別重要？", "options": {"A": "消化系統", "B": "呼吸系統", "C": "神經系統"}, "answer": "A"},
]

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
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)

        text = event.message.text
       if text == '我想查看我的健康資訊':
            question = random.choice(questions)
            question_text = question["question"]
            options = question["options"]

            buttons_template = ButtonsTemplate(
                title='健康知識問答',
                text=question_text,
                actions=[
                    PostbackAction(label=options["A"], data=f"answer:{question['answer']}|user_answer:A", text=options["A"]),
                    PostbackAction(label=options["B"], data=f"answer:{question['answer']}|user_answer:B", text=options["B"]),
                    PostbackAction(label=options["C"], data=f"answer:{question['answer']}|user_answer:C", text=options["C"]),
                ]
            )

            template_message = TemplateMessage(
                alt_text='健康知識問答',
                template=buttons_template
            )

            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[template_message]
                )
            )

@handler.add(MessageEvent, message=TextMessageContent)
def handle_postback(event):
    if event.postback.data.startswith("answer:"):
        data = event.postback.data.split("|")
        correct_answer = data[0].split(":")[1]
        user_answer = data[1].split(":")[1]

        if user_answer == correct_answer:
            reply_text = "恭喜回答正確！"
        else:
            reply_text = "不對喔！再試試看吧！"

        with ApiClient(configuration) as api_client:
            line_bot_api = MessagingApi(api_client)
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=reply_text)]
                )
            )

if __name__ == "__main__":
    app.run()
