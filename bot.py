import os
import json
import random

import discord

from datetime import date
from discord.ext import commands
from discord import app_commands
import aiohttp
from aiohttp import web
from dotenv import load_dotenv

load_dotenv()

# =========================
# 🔑 TOKEN
# =========================


# =========================
# 💾 데이터
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
# 데이터 불러오기
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
# 데이터 저장
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
# 유저 생성
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

        "lucky_dice":0,      # 🎲 럭키 다이스 추가
        "golden_ticket":0,   # 🎫 황금 티켓 추가

        "attendance":0,

        "last_attendance":"",

        "inventory":[]

    }




    for key, value in default.items():

        if key not in data[uid]:

            data[uid][key] = value



    return uid







# =========================
# 역할 버프 확인
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
# 봇 시작
# =========================

@bot.event
async def on_ready():


    synced = await bot.tree.sync()


    print(
        f"{bot.user} 로그인 완료!"
    )


    print(
        f"{len(synced)}개 명령어 등록 완료"
    )

    # =========================
# 📅 출석 시스템
# =========================


@bot.tree.command(
    name="출석",
    description="여름 이벤트 출석"
)
async def attendance(
    interaction: discord.Interaction
):

    data = load_data()

    user = get_user(
        data,
        interaction.user.id
    )


    today = str(date.today())



    if data[user]["last_attendance"] == today:

        await interaction.response.send_message(
            "❌ 오늘은 이미 출석했습니다.",
            ephemeral=True
        )

        return





    # 역할 보너스

    buff = get_role_buff(
        interaction.user
    )


    base_coin = 10


    bonus = int(
        base_coin * buff["coin_bonus"]
    )


    total_coin = base_coin + bonus






    data[user]["last_attendance"] = today

    data[user]["attendance"] += 1

    data[user]["coins"] += total_coin

    data[user]["summer_box"] += 1






    msg = f"""
🌴 출석 완료!

🪙 여름 코인 +{total_coin}
📦 여름 상자 +1

📅 출석:
{data[user]["attendance"]}일
"""





    if bonus > 0:

        msg += f"""

✨ 역할 보너스

추가 코인 +{bonus}
"""






    # 7일 보상

    if data[user]["attendance"] == 7:

        data[user]["gold_box"] += 1


        msg += """

🟨 7일 달성!

황금 상자 +1
"""







    # 30일 보상

    if data[user]["attendance"] == 30:

        data[user]["legend_box"] += 1


        msg += """

🌈 30일 달성!

레전드 상자 +1
"""





    save_data(data)



    await interaction.response.send_message(
        msg
    )








# =========================
# 🪙 코인 확인
# =========================


@bot.tree.command(
    name="코인",
    description="보유 코인 확인"
)
async def coin(
    interaction: discord.Interaction
):

    data = load_data()


    user = get_user(
        data,
        interaction.user.id
    )


    save_data(data)



    await interaction.response.send_message(

        f"""
🪙 **{interaction.user.display_name}님의 여름 코인**

보유량:
{data[user]["coins"]}개
"""

    )

    # =========================
# 📦 상자 확인
# =========================


@bot.tree.command(
    name="상자",
    description="보유 상자 확인"
)
async def box(
    interaction: discord.Interaction
):

    data = load_data()

    user = get_user(
        data,
        interaction.user.id
    )


    save_data(data)


    await interaction.response.send_message(
        f"""
📦 **보유 상자 및 특수 아이템**

📦 여름 상자 : {data[user]["summer_box"]}개

🟨 황금 상자 : {data[user]["gold_box"]}개

🌈 레전드 상자 : {data[user]["legend_box"]}개

🎲 럭키 다이스 : {data[user]["lucky_dice"]}개

🎫 황금 티켓 : {data[user]["golden_ticket"]}장
"""
    )







# =========================
# 🎁 상자 열기 (가중치 확률 및 재귀 적용)
# =========================


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


    if box_type == "summer":
        if data[user]["summer_box"] <= 0:
            await interaction.response.send_message("❌ 여름 상자가 없습니다.", ephemeral=True)
            return
        data[user]["summer_box"] -= 1

        pool = [
            ("🪙 여름 코인 20개", "coin", 20, 35),
            ("🪙 여름 코인 50개", "coin", 50, 25),
            ("🪙 여름 코인 100개", "coin", 100, 15),
            ("🎨 역할 색상권", "item", 0, 8),
            ("✨ 닉네임 꾸미기권", "item", 0, 7),
            ("📦 여름 상자 1개", "box", "summer_box", 5),
            ("🍀 행운 티켓", "ticket", 1, 5),
        ]

    elif box_type == "gold":
        if data[user]["gold_box"] <= 0:
            await interaction.response.send_message("❌ 황금 상자가 없습니다.", ephemeral=True)
            return
        data[user]["gold_box"] -= 1

        pool = [
            ("🪙 여름 코인 200개", "coin", 200, 30),
            ("🪙 여름 코인 300개", "coin", 300, 20),
            ("🌊 바다 역할권", "item", 0, 15),
            ("🎨 역할 색상권", "item", 0, 10),
            ("🍀 행운 티켓", "ticket", 1, 10),
            ("📦 황금 상자 1개", "box", "gold_box", 8),
            ("🌈 레전드 상자 1개", "box", "legend_box", 7),
        ]

    elif box_type == "legend":
        if data[user]["legend_box"] <= 0:
            await interaction.response.send_message("❌ 레전드 상자가 없습니다.", ephemeral=True)
            return
        data[user]["legend_box"] -= 1

        pool = [
            ("🪙 여름 코인 1000개", "coin", 1000, 25),
            ("✨ 윤슬 역할권", "item", 0, 20),
            ("🎫 황금 티켓 1장", "ticket", 1, 15),
            ("💰 코인 2배 쿠폰", "item", 0, 12),
            ("🎟️ 닉네임 꾸미기권", "item", 0, 10),
            ("🔑 황금 열쇠", "item", 0, 8),
            ("💎 레전드 상자 1개", "box", "legend_box", 5),
            ("🎲 럭키 다이스", "special_dice", 1, 5),
        ]

    choices = [p[0] for p in pool]
    weights = [p[3] for p in pool]
    selected_tuple = random.choices(choices, weights=weights, k=1)[0]
    
    reward = next(p for p in pool if p[0] == selected_tuple)

    if reward[1] == "coin":
        buff = get_role_buff(interaction.user)
        bonus = int(reward[2] * buff["coin_bonus"])
        total = reward[2] + bonus
        data[user]["coins"] += total
        result = f"{reward[0]}\n✨ 역할 보너스 +{bonus}코인\n총 획득 {total}코인"

    elif reward[1] == "box":
        data[user][reward[2]] += 1
        result = f"🎉 대박! 상자 안에서 [{reward[0]}] 획득!"

    elif reward[1] == "ticket":
        data[user]["golden_ticket"] += reward[2]
        result = f"🎫 황금 티켓 +{reward[2]}장 획득!"

    elif reward[1] == "special_dice":
        data[user]["lucky_dice"] += reward[2]
        result = f"🎲 럭키 다이스 +{reward[2]}개 획득!"

    else:
        data[user]["inventory"].append(reward[0])
        result = reward[0]

    save_data(data)

    await interaction.response.send_message(
        f"""
🎁 **{종류.name} 개봉!**

획득 보상:
{result}
"""
    )


# =========================
# 🎲 럭키 다이스 시스템
# =========================

@bot.tree.command(
    name="럭키다이스",
    description="럭키 다이스를 굴려 보상을 받습니다"
)
async def lucky_dice(interaction: discord.Interaction):
    data = load_data()
    user = get_user(data, interaction.user.id)

    if data[user]["lucky_dice"] <= 0:
        await interaction.response.send_message("❌ 보유 중인 럭키 다이스가 없습니다.", ephemeral=True)
        return

    data[user]["lucky_dice"] -= 1

    pool = [
        ("🪙 여름 코인 200개", "coin", 200, 30),
        ("🪙 여름 코인 500개", "coin", 500, 20),
        ("📦 여름 상자 1개", "box", "summer_box", 15),
        ("🟨 황금 상자 1개", "box", "gold_box", 10),
        ("🎫 황금 티켓 1장", "ticket", 1, 8),
        ("💰 코인 2배 쿠폰", "item", 0, 7),
        ("🌈 레전드 상자 1개", "box", "legend_box", 5),
        ("🎨 역할 색상권", "item", 0, 5),
    ]

    choices = [p[0] for p in pool]
    weights = [p[3] for p in pool]
    selected_tuple = random.choices(choices, weights=weights, k=1)[0]
    reward = next(p for p in pool if p[0] == selected_tuple)

    if reward[1] == "coin":
        buff = get_role_buff(interaction.user)
        bonus = int(reward[2] * buff["coin_bonus"])
        total = reward[2] + bonus
        data[user]["coins"] += total
        result = f"{reward[0]} (보너스 +{bonus}코인)"
    elif reward[1] == "box":
        data[user][reward[2]] += 1
        result = f"{reward[0]}"
    elif reward[1] == "ticket":
        data[user]["golden_ticket"] += reward[2]
        result = f"🎫 황금 티켓 +{reward[2]}장"
    else:
        data[user]["inventory"].append(reward[0])
        result = reward[0]

    save_data(data)

    await interaction.response.send_message(
        f"""
🎲 **주사위를 굴리는 중...**
. . .
✨ **결과!**

🎁 보상: **{result}**
"""
    )


# =========================
# 📊 확률 안내 (/확률) - 전체 공개
# =========================

@bot.tree.command(
    name="확률",
    description="모든 상자 및 다이스의 획득 확률을 확인합니다"
)
async def drop_rates(interaction: discord.Interaction):
    embed = discord.Embed(
        title="📊 이벤트 상자 & 다이스 확률표",
        description="각 상자와 럭키 다이스에서 등장하는 아이템의 확률입니다.",
        color=discord.Color.gold()
    )
    
    embed.add_field(
        name="📦 여름 상자",
        value="🪙 코인 20개 (35%)\n🪙 코인 50개 (25%)\n🪙 코인 100개 (15%)\n🎨 역할 색상권 (8%)\n✨ 닉네임 꾸미기권 (7%)\n📦 여름 상자 (5%)\n🍀 행운 티켓 (5%)",
        inline=False
    )
    embed.add_field(
        name="🟨 황금 상자",
        value="🪙 코인 200개 (30%)\n🪙 코인 300개 (20%)\n🌊 바다 역할권 (15%)\n🎨 역할 색상권 (10%)\n🍀 행운 티켓 (10%)\n📦 황금 상자 (8%)\n🌈 레전드 상자 (7%)",
        inline=False
    )
    embed.add_field(
        name="🌈 레전드 상자",
        value="🪙 코인 1000개 (25%)\n✨ 윤슬 역할권 (20%)\n🎫 황금 티켓 (15%)\n💰 코인 2배 쿠폰 (12%)\n🎟️ 닉네임 꾸미기권 (10%)\n🔑 황금 열쇠 (8%)\n💎 레전드 상자 (5%)\n🎲 럭키 다이스 (5%)",
        inline=False
    )
    embed.add_field(
        name="🎲 럭키 다이스",
        value="🪙 코인 200개 (30%)\n🪙 코인 500개 (20%)\n📦 여름 상자 (15%)\n🟨 황금 상자 (10%)\n🎫 황금 티켓 (8%)\n💰 코인 2배 쿠폰 (7%)\n🌈 레전드 상자 (5%)\n🎨 역할 색상권 (5%)",
        inline=False
    )

    await interaction.response.send_message(embed=embed)


# =========================
# 🎫 티켓 교환소 (/티켓교환)
# =========================

@bot.tree.command(
    name="티켓교환",
    description="황금 티켓을 사용하여 원하는 보상으로 교환합니다"
)
@app_commands.choices(
    교환항목=[
        app_commands.Choice(name="황금 상자 ×2 (티켓 1장)", value="gold_2"),
        app_commands.Choice(name="레전드 상자 ×1 (티켓 2장)", value="legend_1"),
        app_commands.Choice(name="윤슬 역할권 (티켓 3장)", value="role_yunsl"),
        app_commands.Choice(name="원하는 이벤트 아이템 선택권 (티켓 5장)", value="custom_item"),
    ]
)
async def ticket_exchange(interaction: discord.Interaction, 교환항목: app_commands.Choice[str]):
    data = load_data()
    user = get_user(data, interaction.user.id)

    costs = {
        "gold_2": 1,
        "legend_1": 2,
        "role_yunsl": 3,
        "custom_item": 5
    }

    req_ticket = costs[교환항목.value]

    if data[user]["golden_ticket"] < req_ticket:
        await interaction.response.send_message(f"❌ 황금 티켓이 부족합니다. (필요: {req_ticket}장, 보유: {data[user]['golden_ticket']}장)", ephemeral=True)
        return

    data[user]["golden_ticket"] -= req_ticket

    if 교환항목.value == "gold_2":
        data[user]["gold_box"] += 2
        msg = "🟨 황금 상자 2개 교환 완료!"
    elif 교환항목.value == "legend_1":
        data[user]["legend_box"] += 1
        msg = "🌈 레전드 상자 1개 교환 완료!"
    elif 교환항목.value == "role_yunsl":
        data[user]["inventory"].append("✨ 윤슬 역할권")
        msg = "✨ 윤슬 역할권 지급 완료!"
    elif 교환항목.value == "custom_item":
        data[user]["inventory"].append("🎁 특별 보상권")
        msg = "🎁 원하는 이벤트 아이템으로 교환할 수 있는 [특별 보상권] 지급 완료!"

    save_data(data)
    await interaction.response.send_message(f"✅ 티켓 교환 성공!\n\n{msg} (남은 황금 티켓: {data[user]['golden_ticket']}장)")


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


    save_data(data)



    if len(data[user]["inventory"]) == 0:

        text = "없음"

    else:

        text = "\n".join(
            data[user]["inventory"]
        )



    await interaction.response.send_message(

        f"""
🎒 **{interaction.user.display_name}님의 인벤토리**

{text}
"""
    )

    # =========================
# 🏖️ 상점 목록
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



        item = SHOP_ITEMS[
            self.item_name
        ]



        # 할인 적용

        buff = get_role_buff(
            interaction.user
        )


        price = int(
            item["price"] *
            (1 - buff["shop_discount"])
        )




        # 코인 부족

        if data[user]["coins"] < price:


            await interaction.response.send_message(

                "❌ 코인이 부족합니다.",

                ephemeral=True

            )

            return





        # =====================
        # 역할 구매
        # =====================


        if item["type"] == "role":


            role = discord.utils.find(
    lambda r: r.name == item["role"],
    interaction.guild.roles
)

            if role is None:


                await interaction.response.send_message(

                    f"❌ 서버에 `{item['role']}` 역할이 없습니다.\n"
                    "역할을 먼저 만들어주세요.",

                    ephemeral=True

                )

                return




            try:

                await interaction.user.add_roles(
                    role
                )


            except discord.Forbidden:


                await interaction.response.send_message(

                    "❌ 봇 역할이 구매 역할보다 낮습니다.\n"
                    "서버 설정 → 역할에서 봇 역할을 올려주세요.",

                    ephemeral=True

                )

                return







        # =====================
        # 아이템 구매
        # =====================


        elif item["type"] == "item":


            data[user]["inventory"].append(
                self.item_name
            )








        # =====================
        # 상자 구매
        # =====================


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
# 💰 판매 가격표
# =========================

SELL_PRICE = {

    "🎨 역할 색상권":300,

    "✨ 닉네임 꾸미기권":250,

    "🏷️ 개인 채널 꾸미기권":400,

    "🌊 바다 역할권":300,

    "✨ 윤슬 역할권":400,

    "🎁 특별 보상권":500

}








# =========================
# 💰 판매
# =========================


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




    # 이름 일부 입력 허용

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




    item = find_item






    # 판매 가격

    price = SELL_PRICE.get(
        item,
        100
    )







    # 역할별 수수료

    buff = get_role_buff(
        interaction.user
    )


    fee_rate = buff["sell_fee"]



    fee = int(
        price * fee_rate
    )



    receive = price - fee







    # =====================
    # 아이템 제거 먼저
    # =====================


    if item in data[user]["inventory"]:

        data[user]["inventory"].remove(
            item
        )

    else:

        await interaction.response.send_message(

            "❌ 판매 처리 오류",

            ephemeral=True

        )

        return







    # 코인 지급

    data[user]["coins"] += receive



    save_data(data)







    await interaction.response.send_message(

        f"""
💰 판매 완료!


📦 아이템

{item}


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
    코인: int
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

            "❌ 여름 / 황금 / 레전드 중 입력해주세요."

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


📦 상자 및 특수

📦 여름 : {data[user]["summer_box"]}
🟨 황금 : {data[user]["gold_box"]}
🌈 레전드 : {data[user]["legend_box"]}
🎲 다이스 : {data[user]["lucky_dice"]}
🎫 티켓 : {data[user]["golden_ticket"]}


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


📦 상자 및 미니게임

/상자
/상자열기
/확률
/럭키다이스
/티켓교환


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



    print(error)







# =========================
# 🚀 실행
# =========================

bot.run(os.environ['TOKEN'])
