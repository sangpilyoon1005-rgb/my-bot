import os
import json
import random

import discord

from datetime import date
from discord.ext import commands
from discord import app_commands

from dotenv import load_dotenv

load_dotenv()


# =========================
# 🔑 데이터 설정
# =========================

DATA_FILE = "data.json"



# =========================
# 🤖 디스코드 설정
# =========================

intents = discord.Intents.default()

intents.guilds = True
intents.message_content = True


bot = commands.Bot(
    command_prefix="!",
    intents=intents
)



# =========================
# 🌴 역할 버프
# =========================

ROLE_BUFFS = {

    "🌱 여름 기초자": {

        "sell_fee":0.18,
        "coin_bonus":0.05,
        "shop_discount":0.02

    },


    "🏝️ 여름 여행자": {

        "sell_fee":0.15,
        "coin_bonus":0.10,
        "shop_discount":0.05

    },


    "🌊 바다": {

        "sell_fee":0.10,
        "coin_bonus":0.15,
        "shop_discount":0.10

    },


    "✨ 윤슬": {

        "sell_fee":0.05,
        "coin_bonus":0.25,
        "shop_discount":0.15

    }

}



# =========================
# 💾 데이터 불러오기
# =========================

def load_data():

    if os.path.exists(DATA_FILE):

        with open(
            DATA_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            return json.load(f)


    return {}




# =========================
# 💾 데이터 저장
# =========================

def save_data(data):

    with open(
        DATA_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=4
        )




# =========================
# 👤 유저 생성
# =========================

def get_user(data, user_id):

    uid = str(user_id)


    if uid not in data:

        data[uid] = {}



    default = {

        "coins":0,

        "summer_box":0,

        "gold_box":0,

        "legend_box":0,

        "attendance":0,

        "last_attendance":"",

        "inventory":[]

    }



    for key,value in default.items():

        if key not in data[uid]:

            data[uid][key] = value



    return uid




# =========================
# 🌴 역할 버프 확인
# =========================

def get_role_buff(member):


    for role in member.roles[::-1]:

        if role.name in ROLE_BUFFS:

            return ROLE_BUFFS[role.name]



    return {

        "sell_fee":0.20,

        "coin_bonus":0,

        "shop_discount":0

    }



# =========================
# 🎁 상자 확률 데이터
# =========================

BOX_REWARDS = {


    "summer":[

        {
            "name":"🪙 여름 코인 20개",
            "type":"coin",
            "value":20,
            "prob":40
        },

        {
            "name":"🪙 여름 코인 50개",
            "type":"coin",
            "value":50,
            "prob":30
        },

        {
            "name":"🪙 여름 코인 100개",
            "type":"coin",
            "value":100,
            "prob":20
        },

        {
            "name":"🎨 역할 색상권",
            "type":"item",
            "value":0,
            "prob":7
        },

        {
            "name":"✨ 닉네임 꾸미기권",
            "type":"item",
            "value":0,
            "prob":3
        }

    ],



    "gold":[

        {
            "name":"🪙 여름 코인 200개",
            "type":"coin",
            "value":200,
            "prob":40
        },

        {
            "name":"🪙 여름 코인 300개",
            "type":"coin",
            "value":300,
            "prob":30
        },

        {
            "name":"🌊 바다 역할권",
            "type":"item",
            "value":0,
            "prob":20
        },

        {
            "name":"🏷️ 개인 채널 꾸미기권",
            "type":"item",
            "value":0,
            "prob":10
        }

    ],



    "legend":[

        {
            "name":"🪙 여름 코인 1000개",
            "type":"coin",
            "value":1000,
            "prob":50
        },

        {
            "name":"✨ 윤슬 역할권",
            "type":"item",
            "value":0,
            "prob":25
        },

        {
            "name":"🎁 특별 보상권",
            "type":"item",
            "value":0,
            "prob":25
        }

    ]

}

# =========================
# 🎁 상자 열기 + 확률 시스템
# =========================


BOX_PROBABILITY = {

    "summer": [

        ("🪙 여름 코인 20개", 40),
        ("🪙 여름 코인 50개", 30),
        ("🪙 여름 코인 100개", 15),
        ("🎨 역할 색상권", 10),
        ("✨ 닉네임 꾸미기권", 5)

    ],


    "gold": [

        ("🪙 여름 코인 200개", 40),
        ("🪙 여름 코인 300개", 25),
        ("🌊 바다 역할권", 20),
        ("🏷️ 개인 채널 꾸미기권", 15)

    ],


    "legend": [

        ("🪙 여름 코인 1000개", 50),
        ("✨ 윤슬 역할권", 30),
        ("🎁 특별 보상권", 20)

    ]

}



def get_box_reward(box):

    rewards = BOX_PROBABILITY[box]

    names = []

    weights = []


    for name, chance in rewards:

        names.append(name)

        weights.append(chance)


    return random.choices(
        names,
        weights=weights,
        k=1
    )[0]





@bot.tree.command(
    name="확률",
    description="상자 보상 확률 공개"
)
async def probability(
    interaction: discord.Interaction
):

    await interaction.response.send_message(

        """
🎁 **SEOLYE SUMMER BOT 상자 확률표**

━━━━━━━━━━━━━━

📦 여름 상자

🪙 여름 코인 20개 — 40%
🪙 여름 코인 50개 — 30%
🪙 여름 코인 100개 — 15%
🎨 역할 색상권 — 10%
✨ 닉네임 꾸미기권 — 5%


━━━━━━━━━━━━━━

🟨 황금 상자

🪙 여름 코인 200개 — 40%
🪙 여름 코인 300개 — 25%
🌊 바다 역할권 — 20%
🏷️ 개인 채널 꾸미기권 — 15%


━━━━━━━━━━━━━━

🌈 레전드 상자

🪙 여름 코인 1000개 — 50%
✨ 윤슬 역할권 — 30%
🎁 특별 보상권 — 20%


━━━━━━━━━━━━━━

🍀 행운을 빌어요!
"""
    )








@bot.tree.command(
    name="상자열기",
    description="상자를 엽니다"
)
@app_commands.choices(
    종류=[

        app_commands.Choice(
            name="여름 상자",
            value="summer"
        ),

        app_commands.Choice(
            name="황금 상자",
            value="gold"
        ),

        app_commands.Choice(
            name="레전드 상자",
            value="legend"
        )

    ]
)
async def open_box(
    interaction: discord.Interaction,
    종류: app_commands.Choice[str]
):


    data = load_data()


    user = get_user(
        data,
        interaction.user.id
    )


    box_type = 종류.value



    box_key = {

        "summer":"summer_box",
        "gold":"gold_box",
        "legend":"legend_box"

    }



    key = box_key[box_type]



    if data[user][key] <= 0:

        await interaction.response.send_message(

            "❌ 해당 상자가 없습니다.",

            ephemeral=True

        )

        return



    # 상자 차감

    data[user][key] -= 1



    reward_name = get_box_reward(
        box_type
    )



    # 코인 보상 처리

    coin_rewards = {

        "🪙 여름 코인 20개":20,
        "🪙 여름 코인 50개":50,
        "🪙 여름 코인 100개":100,
        "🪙 여름 코인 200개":200,
        "🪙 여름 코인 300개":300,
        "🪙 여름 코인 1000개":1000

    }



    if reward_name in coin_rewards:


        amount = coin_rewards[reward_name]


        buff = get_role_buff(
            interaction.user
        )


        bonus = int(
            amount * buff["coin_bonus"]
        )


        total = amount + bonus


        data[user]["coins"] += total



        result = f"""

{reward_name}

✨ 역할 보너스 +{bonus}코인

총 획득:
{total}코인

"""



    else:


        data[user]["inventory"].append(
            reward_name
        )


        result = reward_name




    save_data(data)



    await interaction.response.send_message(

        f"""
🎁 **{종류.name} 개봉!**

획득 보상

{result}
"""

    )





# =========================
# 🎒 인벤토리
# =========================


@bot.tree.command(
    name="인벤토리",
    description="아이템 확인"
)
async def inventory(
    interaction: discord.Interaction
):


    data = load_data()


    user = get_user(
        data,
        interaction.user.id
    )


    items = data[user]["inventory"]



    if not items:

        text = "없음"

    else:

        text = "\n".join(items)



    await interaction.response.send_message(

        f"""
🎒 **{interaction.user.display_name}님의 인벤토리**

{text}
"""

    )

# =========================
# 🏖️ 상점 시스템
# =========================


SHOP_ITEMS = {


    "🌱 여름 기초자": {

        "price":50,

        "type":"role",

        "role":"🌱 여름 기초자"

    },


    "🏝️ 여름 여행자": {

        "price":200,

        "type":"role",

        "role":"🏝️ 여름 여행자"

    },


    "🌊 바다": {

        "price":600,

        "type":"role",

        "role":"🌊 바다"

    },


    "✨ 윤슬": {

        "price":750,

        "type":"role",

        "role":"✨ 윤슬"

    },


    "🎨 역할 색상권": {

        "price":500,

        "type":"item"

    },


    "✨ 닉네임 꾸미기권": {

        "price":400,

        "type":"item"

    },


    "🏷️ 개인 채널 꾸미기권": {

        "price":700,

        "type":"item"

    },


    "📦 여름 상자": {

        "price":100,

        "type":"box",

        "box":"summer_box"

    },


    "🟨 황금 상자": {

        "price":300,

        "type":"box",

        "box":"gold_box"

    },


    "🌈 레전드 상자": {

        "price":700,

        "type":"box",

        "box":"legend_box"

    }

}







# =========================
# 🛒 상점 버튼
# =========================


class ShopButton(discord.ui.Button):


    def __init__(self, item):


        self.item_name = item


        super().__init__(

            label=item,

            style=discord.ButtonStyle.primary

        )





    async def callback(
        self,
        interaction: discord.Interaction
    ):


        data = load_data()


        user = get_user(

            data,

            interaction.user.id

        )



        item = SHOP_ITEMS[self.item_name]



        buff = get_role_buff(

            interaction.user

        )



        price = int(

            item["price"] *

            (1 - buff["shop_discount"])

        )



        if data[user]["coins"] < price:


            await interaction.response.send_message(

                "❌ 코인이 부족합니다.",

                ephemeral=True

            )

            return





        # 역할 구매


        if item["type"] == "role":


            role = discord.utils.find(

                lambda r:
                r.name == item["role"],

                interaction.guild.roles

            )



            if role is None:


                await interaction.response.send_message(

                    "❌ 서버에 역할이 없습니다.",

                    ephemeral=True

                )

                return




            try:


                await interaction.user.add_roles(

                    role

                )


            except discord.Forbidden:


                await interaction.response.send_message(

                    "❌ 봇 역할 순서를 올려주세요.",

                    ephemeral=True

                )

                return





        # 아이템 구매


        elif item["type"] == "item":


            data[user]["inventory"].append(

                self.item_name

            )






        # 상자 구매


        elif item["type"] == "box":


            data[user][item["box"]] += 1





        data[user]["coins"] -= price



        save_data(data)




        await interaction.response.send_message(

            f"""

🎉 구매 완료!

상품:
{self.item_name}


🪙 사용 코인:
{price}개

"""

        )







# =========================
# 상점 UI
# =========================


class ShopView(discord.ui.View):


    def __init__(self):

        super().__init__(

            timeout=120

        )


        for item in SHOP_ITEMS:


            self.add_item(

                ShopButton(item)

            )







# =========================
# 🏖️ 상점 명령어
# =========================


@bot.tree.command(

    name="상점",

    description="여름 코인 상점"

)
async def shop(

    interaction: discord.Interaction

):


    embed = discord.Embed(

        title="🏖️ 여름 코인 상점",

        description="""

🌴 역할

🌱 여름 기초자 - 50
🏝️ 여름 여행자 - 200
🌊 바다 - 600
✨ 윤슬 - 750


🎨 아이템

🎨 역할 색상권 - 500
✨ 닉네임 꾸미기권 - 400
🏷️ 개인 채널 꾸미기권 - 700


📦 상자

📦 여름 상자 - 100
🟨 황금 상자 - 300
🌈 레전드 상자 - 700


✨ 역할 보유자는 할인 적용

""",

        color=discord.Color.blue()

    )



    await interaction.response.send_message(

        embed=embed,

        view=ShopView()

    )

# =========================
# 💰 판매 시스템
# =========================


SELL_PRICE = {

    "🎨 역할 색상권":300,

    "✨ 닉네임 꾸미기권":250,

    "🏷️ 개인 채널 꾸미기권":400,

    "🌊 바다 역할권":300,

    "✨ 윤슬 역할권":400,

    "🎁 특별 보상권":500

}





@bot.tree.command(
    name="판매",
    description="아이템을 판매합니다"
)
@app_commands.describe(
    아이템="판매할 아이템 이름"
)
async def sell(
    interaction: discord.Interaction,
    아이템:str
):


    data = load_data()


    user = get_user(

        data,

        interaction.user.id

    )



    find_item = None



    for inv_item in data[user]["inventory"]:


        if 아이템.strip() in inv_item:


            find_item = inv_item

            break





    if find_item is None:


        await interaction.response.send_message(

            "❌ 인벤토리에 해당 아이템이 없습니다.",

            ephemeral=True

        )

        return





    price = SELL_PRICE.get(

        find_item,

        100

    )




    buff = get_role_buff(

        interaction.user

    )



    fee = int(

        price * buff["sell_fee"]

    )



    receive = price - fee





    data[user]["inventory"].remove(

        find_item

    )



    data[user]["coins"] += receive



    save_data(data)




    await interaction.response.send_message(

        f"""

💰 판매 완료!


📦 아이템

{find_item}


💵 판매 가격

{price} 코인


💸 수수료

{fee} 코인


✅ 획득

{receive} 코인

"""

    )









# =========================
# 👑 관리자 코인 지급
# =========================


@bot.tree.command(
    name="코인지급",
    description="코인을 지급합니다"
)
@app_commands.checks.has_permissions(
    administrator=True
)
async def give_coin(

    interaction: discord.Interaction,

    유저: discord.Member,

    코인:int

):


    data = load_data()


    user = get_user(

        data,

        유저.id

    )


    data[user]["coins"] += 코인


    save_data(data)




    await interaction.response.send_message(

        f"✅ {유저.mention}님에게 🪙 {코인}코인 지급 완료"

    )









# =========================
# 👑 관리자 코인 회수
# =========================


@bot.tree.command(
    name="코인회수",
    description="코인을 회수합니다"
)
@app_commands.checks.has_permissions(
    administrator=True
)
async def remove_coin(

    interaction: discord.Interaction,

    유저: discord.Member,

    코인:int

):


    data = load_data()


    user = get_user(

        data,

        유저.id

    )



    data[user]["coins"] = max(

        0,

        data[user]["coins"] - 코인

    )



    save_data(data)




    await interaction.response.send_message(

        f"✅ {유저.mention}님의 🪙 {코인}코인 회수 완료"

    )









# =========================
# 👑 관리자 상자 지급
# =========================


@bot.tree.command(
    name="상자지급",
    description="상자를 지급합니다"
)
@app_commands.checks.has_permissions(
    administrator=True
)
async def give_box(

    interaction: discord.Interaction,

    유저: discord.Member,

    종류:str,

    개수:int

):


    data = load_data()


    user = get_user(

        data,

        유저.id

    )




    if 종류 == "여름":

        data[user]["summer_box"] += 개수


    elif 종류 == "황금":

        data[user]["gold_box"] += 개수


    elif 종류 == "레전드":

        data[user]["legend_box"] += 개수


    else:


        await interaction.response.send_message(

            "❌ 여름 / 황금 / 레전드 중 입력해주세요.",

            ephemeral=True

        )

        return





    save_data(data)




    await interaction.response.send_message(

        f"📦 {유저.mention}님에게 {종류} 상자 {개수}개 지급 완료"

    )









# =========================
# 👤 유저 정보
# =========================


@bot.tree.command(
    name="유저정보",
    description="유저 정보를 확인합니다"
)
@app_commands.checks.has_permissions(
    administrator=True
)
async def user_info(

    interaction: discord.Interaction,

    유저: discord.Member

):


    data = load_data()


    user = get_user(

        data,

        유저.id

    )



    items = (

        "\n".join(
            data[user]["inventory"]
        )

        if data[user]["inventory"]

        else "없음"

    )




    await interaction.response.send_message(

        f"""

👤 {유저.display_name}


🪙 코인

{data[user]["coins"]}


📦 상자

📦 여름 : {data[user]["summer_box"]}

🟨 황금 : {data[user]["gold_box"]}

🌈 레전드 : {data[user]["legend_box"]}


📅 출석

{data[user]["attendance"]}일


🎒 인벤토리

{items}

"""

    )

# =========================
# ❓ 도움말
# =========================


@bot.tree.command(
    name="도움말",
    description="명령어 목록"
)
async def help_command(
    interaction: discord.Interaction
):


    await interaction.response.send_message(

        """
🌴 **SEOLYE SUMMER BOT**


📅 이벤트

/출석
/코인


📦 상자

/상자
/상자열기
/확률


🎒 아이템

/인벤토리
/판매


🏖️ 경제

/상점


👑 관리자

/코인지급
/코인회수
/상자지급
/유저정보

"""

    )









# =========================
# ⚠️ 오류 처리
# =========================


@bot.tree.error
async def command_error(

    interaction: discord.Interaction,

    error

):


    if isinstance(

        error,

        app_commands.errors.MissingPermissions

    ):


        await interaction.response.send_message(

            "❌ 관리자 권한이 필요합니다.",

            ephemeral=True

        )

        return



    print(

        error

    )









# =========================
# 🚀 실행
# =========================


bot.run(
    os.environ["TOKEN"]
)
