from flask import Flask, request, abort

from linebot.v3  import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import Configuration, ApiClient, MessagingApi, ReplyMessageRequest, TextMessage
from linebot.v3.webhooks import UserSource
from linebot.v3.webhooks import MessageEvent, TextMessageContent, LocationMessageContent
from linebot.v3.messaging import ButtonsTemplate, TemplateMessage, ImageMessage
from linebot.v3.messaging import PostbackAction

import livejson

from datetime import datetime
from utils import calculateBMI, calculateDayCalories, plotHealth
import random
import os

app = Flask(__name__)
# run_with_ngrok(app)
# LINE 聊天機器人的基本設定
configuration = Configuration(access_token = os.environ.get('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.environ.get('LINE_CHANNEL_SECRET'))
ngrok_url = "https://555b-2001-b011-7800-dc60-cbc-3c37-4d10-40ef.ngrok-free.app/static/"
datasets = livejson.File('information.json', pretty = True, indent = 4)

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

breakfast_recipes = [
    {"name": "燕麥粥", "ingredients": ["燕麥", "牛奶", "蜂蜜", "水果"], "method": "將燕麥與牛奶煮沸，然後加入蜂蜜和水果即可食用。"},
    {"name": "蔬菜煎蛋", "ingredients": ["雞蛋", "菠菜", "蕃茄", "洋蔥"], "method": "將雞蛋打散，加入切碎的菠菜、蕃茄和洋蔥，煎至熟透。"},
    {"name": "全麥吐司配牛油果", "ingredients": ["全麥吐司", "牛油果", "鹽", "胡椒"], "method": "將牛油果搗碎，塗在全麥吐司上，撒上鹽和胡椒即可。"},
]

lunch_recipes = [
    {"name": "雞肉沙拉", "ingredients": ["雞胸肉", "生菜", "黃瓜", "橄欖油"], "method": "將雞胸肉煮熟切片，與生菜和黃瓜混合，淋上橄欖油。"},
    {"name": "番茄義大利麵", "ingredients": ["義大利麵", "番茄醬", "大蒜", "橄欖油"], "method": "煮熟義大利麵，加入炒好的番茄醬和大蒜，即可食用。"},
    {"name": "燒烤三文魚", "ingredients": ["三文魚", "檸檬", "橄欖油", "迷迭香"], "method": "將三文魚用檸檬汁和橄欖油醃製，撒上迷迭香，烤至熟透。"},
]

dinner_recipes = [
    {"name": "牛肉燉蔬菜", "ingredients": ["牛肉", "馬鈴薯", "胡蘿蔔", "洋蔥"], "method": "將牛肉與蔬菜一起燉煮，直至所有食材熟透入味。"},
    {"name": "豆腐炒青菜", "ingredients": ["豆腐", "青菜", "大蒜", "醬油"], "method": "將豆腐和青菜與大蒜一起翻炒，加入適量醬油調味。"},
    {"name": "烤雞胸肉", "ingredients": ["雞胸肉", "檸檬", "胡椒", "鹽"], "method": "將雞胸肉用檸檬汁、鹽和胡椒醃製，然後烤至熟透。"},
]

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
                
                function ... 1
                userHeight         [time, value], [time, value], [time, value] ...
                userWeight         [time, value], [time, value], [time, value] ...
                userBloodPressure  [time, value], [time, value], [time, value] ...
                userBloodSuger     [time, value], [time, value], [time, value] ...
                
                function ... 2
                userCalories       [time, value], [time, value], [time, value] ...
                
                function ... 5
                userPlay           [played, answer]
        '''
        if isinstance(event.source, UserSource):
            profile = line_bot_api.get_profile(user_id = event.source.user_id)
            if event.source.user_id not in datasets:
                os.makedirs(f"./static/{event.source.user_id}/", exist_ok = True)
                datasets[event.source.user_id] = {
                    "userName" : profile.display_name,
                    "userHeight" : [],
                    "userWeight" : [],
                    "userBloodSuger" : [],
                    "userBloodPressure" : [],
                    
                    "userCalories" : [],
                    
                    "userPlay" : [0, 0]
                }
            
        
        # --- 我的身體健康 --- # 1
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
        
        # --- 飲食追蹤器開始貼 --- # 2
        if text == '我想追蹤我的飲食狀況':
            buttons_eat = ButtonsTemplate(
                title = '我想追蹤飲食紀錄',
                text = '請點擊以下按鈕觸發飲食紀錄',
                actions=[
                    PostbackAction(label = '我想紀錄飲食卡路里', data='我想紀錄飲食卡路里', text='我想紀錄飲食卡路里'),
                    PostbackAction(label = '我想查看今天攝取多少卡路里', data='我想查看今天攝取多少卡路里', text='我想查看今天攝取多少卡路里'),
            ])
            template_message = TemplateMessage(
                alt_text = 'Buttons alt text',
                template = buttons_eat
            )
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token = event.reply_token,
                    messages = [template_message]
                )
            )
        
        if text == "我想紀錄飲食卡路里":
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token = event.reply_token,
                    messages=[
                        TextMessage(text='卡路里(單位kcal)範例格式為:卡路里 300')
                    ]
                )
            )        
        
        if text == "我想查看今天攝取多少卡路里":
            profile = line_bot_api.get_profile(user_id = event.source.user_id)
            heats = calculateDayCalories(datasets[event.source.user_id])
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token = event.reply_token,
                    messages=[
                        TextMessage(text = f'{profile.display_name}，今天總共攝取的卡路里為 {heats} kcal')
                    ]
                )
            )
            
        if text.startswith("卡路里"):
            try:
                float(text.split(" ")[1])
                datasets[event.source.user_id]['userCalories'].append([datetime.now().strftime("%m/%d/%Y, %H:%M:%S"), text.split(" ")[1]])
                line_bot_api.reply_message(
                    ReplyMessageRequest(
                        reply_token = event.reply_token,
                        messages=[
                            TextMessage(text = f'成功輸入，{profile.display_name}的攝取了{text.split(" ")[1]}卡路里。')
                        ]
                    )
                )
            except:
                line_bot_api.reply_message(
                    ReplyMessageRequest(
                        reply_token = event.reply_token,
                        messages=[
                            TextMessage(text='卡路里(單位kcal)範例格式為:卡路里 300')
                        ]
                    )
                )
            
        # --- 健康食譜推薦 --- # 3
        if text == '我想要取得健康食譜':
            buttons_template = ButtonsTemplate(
                title='健康食譜推薦',
                text='請選擇您想要的餐點',
                actions=[
                    PostbackAction(label='早餐', data='meal:breakfast', text='早餐'),
                    PostbackAction(label='午餐', data='meal:lunch', text='午餐'),
                    PostbackAction(label='晚餐', data='meal:dinner', text='晚餐')
                ]
            )
            template_message = TemplateMessage(
                alt_text='健康食譜推薦',
                template=buttons_template
            )
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[template_message]
                )
            )
        elif text in ['早餐', '午餐', '晚餐']:
            if text == '早餐':
                recipe = random.choice(breakfast_recipes)
            elif text == '午餐':
                recipe = random.choice(lunch_recipes)
            else:
                recipe = random.choice(dinner_recipes)

            recipe_name = recipe["name"]
            ingredients = ", ".join(recipe["ingredients"])
            method = recipe["method"]
            reply_text = f"推薦的{text}食譜是: {recipe_name}\n所需食材: {ingredients}\n作法: {method}"

            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[
                        TextMessage(text = reply_text)
                        ]
                )
            )
        
        # --- 健康外食Go --- # 4
        if text == '我想取得周遭健康外食':
            reply_text = f"請分享您的位置地址給我，在\"文字聊天\"左邊\"+\"的\"位置資訊\"!"

            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[
                        TextMessage(text = reply_text)
                        ]
                )
            )
            
        # --- 健康知識王 --- # 5
        if text == '我想玩健康知識王':
            question = random.choice(questions)
            question_text = question["question"]
            options = question["options"]
            datasets[event.source.user_id]["userPlay"] = [1, question['answer']]
            question_template = ButtonsTemplate(
                title='健康知識問答',
                text=question_text,
                actions=[
                    PostbackAction(label=options["A"], data=f"我選擇答案(A)", text="我選擇答案(A)" + options["A"]),
                    PostbackAction(label=options["B"], data=f"我選擇答案(B)", text="我選擇答案(B)" + options["B"]),
                    PostbackAction(label=options["C"], data=f"我選擇答案(C)", text="我選擇答案(C)" + options["C"]),
                ]
            )
            
            template_message = TemplateMessage(
                alt_text = 'Buttons alt text',
                template = question_template
            )
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token = event.reply_token,
                    messages = [template_message]
                )
            )
        elif text.startswith("我選擇答案") and datasets[event.source.user_id]["userPlay"][0]:
            user_answer = text.split('(')[1].split(')')[0]
            answer = datasets[event.source.user_id]["userPlay"][1]
            if user_answer == datasets[event.source.user_id]["userPlay"][1]:
                reply_text = "恭喜回答正確！"
                datasets[event.source.user_id]["userPlay"][0] = 0
            else:
                reply_text = f"不對喔！再試試看吧！！"
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token = event.reply_token,
                    messages=[
                        TextMessage(text = reply_text)
                        ]
                )
            )
            
        # --- 健康數據圖 --- # 6
        if text == "我想取得健康數據圖":
            BMI_text = calculateBMI(datasets[event.source.user_id])
            reply_text = f"根據您的「血糖、血壓、BMI」輸入資料，這是30日內的各個數據圖：\n空腹血糖<110以及飯後血糖<140\n血壓收縮壓<120以及擴張壓<80\n這些是正常範圍喔！請多多注意⚠️\n根據您的身高體重資料計算出BMI{BMI_text}"
            plotHealth(datasets[event.source.user_id], event.source.user_id)
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token = event.reply_token,
                    messages=[
                        TextMessage(
                            text = reply_text
                            ),
                        ImageMessage(
                                type = "image",
                                originalContentUrl = ngrok_url + event.source.user_id + "/output.png",
                                previewImageUrl = ngrok_url + event.source.user_id + "/output.png"
                            )
                        
                        ]
                )
            )
# --- 健康外食Go --- # 4
BASE_URL = 'https://www.google.com.tw/maps/search/健康外食'
@handler.add(MessageEvent, message = LocationMessageContent)
def handle_text_message(event):
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        if isinstance(event.source, UserSource):
            profile = line_bot_api.get_profile(user_id = event.source.user_id)
            # address = event.message.address
            # search_url = BASE_URL + address
            if event.source.user_id not in datasets:
                datasets[event.source.user_id] = {
                    "userName" : profile.display_name,
                    "userHeight" : [],
                    "userWeight" : [],
                    "userBloodSuger" : [],
                    "userBloodPressure" : [],
                    
                    "userCalories" : [],
                }
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text = BASE_URL)]
                )
            )

            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text = BASE_URL)]
                )
            )
            
if __name__ == "__main__":
  app.run()
