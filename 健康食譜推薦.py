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
@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)

        if text == '我想要取得健康食譜':
            buttons_template = ButtonsTemplate(
                title='健康食譜推薦',
                text='請選擇您想要的餐點',
                actions=[
                    PostbackAction(label='早餐', data='meal:breakfast', text='早餐'),
                    PostbackAction(label='午餐', data='meal:lunch', text='午餐'),
                    PostbackAction(label='晚餐', data='meal:dinner', text='晚餐'),
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
                    messages=[TextMessage(text=reply_text)]
                )
            )
        else:
            buttons_template = ButtonsTemplate(
                title='健康食譜推薦',
                text='請選擇您想要的餐點',
                actions=[
                    PostbackAction(label='早餐', data='meal:breakfast', text='早餐'),
                    PostbackAction(label='午餐', data='meal:lunch', text='午餐'),
                    PostbackAction(label='晚餐', data='meal:dinner', text='晚餐'),
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
