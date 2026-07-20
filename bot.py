import discord
from discord.ext import commands
import json
import os
from datetime import date
import random
from discord.ui import View
from discord import app_commands

TOKEN = os.environ.get('DISCORD_TOKEN')

intents = discord.Intents.default()

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

DATA_FILE = "data.json"


def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def get_user(data, user_id):
    user_id = str(user_id)

    if user_id not in data:
        data[user_id] = {
            "coins": 0,
            "summer_box": 0,
            "gold_box": 0,
            "legend_box": 0,
            "attendance": 0,
            "last_attendance": ""
        }

    return user_id


@bot.event
async def on_ready():
    synced = await bot.tree.sync()
    print(f"{bot.user} 로그인 완료!")
    print(f"{len(synced)}개의 명령어 등록 완료")


@bot.tree.command(name="출석", description="방학 출석")
async def attendance(interaction: discord.Interaction):

    data = load_data()
    user = get_user(data, interaction.user.id)

    today = str(date.today())

    if data[user]["last_attendance"] == today:
        await interaction.response.send_message(
            "❌ 오늘은 이미 출석했습니다.",
            ephemeral=True
        )
        return

    data[user]["last_attendance"] = today
    data[user]["attendance"] += 1
    data[user]["coins"] += 10
    data[user]["summer_box"] += 1

    msg = (
        f"🌴 {interaction.user.mention} 출석 완료!\n\n"
        "🪙 여름 코인 +10\n"
        "📦 여름 상자 +1"
    )

    if data[user]["attendance"] == 7:
        data[user]["gold_box"] += 1
        msg += "\n🟨 7일 달성!\n🎁 황금 상자 +1"

    if data[user]["attendance"] == 30:
        data[user]["legend_box"] += 1
        msg += "\n🌈 30일 달성!\n🎁 레전드 상자 +1"

    save_data(data)

    await interaction.response.send_message(msg)


@bot.tree.command(name="코인", description="보유 코인 확인")
async def coin(interaction: discord.Interaction):

    data = load_data()
    user = get_user(data, interaction.user.id)

    await interaction.response.send_message(
        f"🪙 보유 여름 코인 : {data[user]['coins']}개"
    )


@bot.tree.command(name="상자", description="보유 상자 확인")
async def box(interaction: discord.Interaction):

    data = load_data()
    user = get_user(data, interaction.user.id)

    await interaction.response.send_message(
        f"""
📦 **보유 상자**

📦 여름 상자 : {data[user]['summer_box']}개
🟨 황금 상자 : {data[user]['gold_box']}개
🌈 레전드 상자 : {data[user]['legend_box']}개
"""
    )


@bot.tree.command(name="도움말", description="명령어")
async def help_command(interaction: discord.Interaction):

    await interaction.response.send_message(
        """
🌴 **SEOLYE BOT**

📅 /출석
🪙 /코인
📦 /상자
❓ /도움말
🎒 /인벤토리
🏖️ /상점
🛍️ /상점설치
🌴 /이벤트초기화
"""
    )

@bot.tree.command(name="상자열기", description="상자를 엽니다.")
@app_commands.choices(
    종류=[
        app_commands.Choice(name="여름", value="여름"),
        app_commands.Choice(name="황금", value="황금"),
        app_commands.Choice(name="레전드", value="레전드"),
    ]
)
async def open_box(
    interaction: discord.Interaction,
    종류: app_commands.Choice[str]
):

    data = load_data()
    user = get_user(data, interaction.user.id)

    if "inventory" not in data[user]:
        data[user]["inventory"] = []

    종류 = 종류.value.lower()

    if 종류 == "여름":

        if data[user]["summer_box"] <= 0:
            await interaction.response.send_message("❌ 여름 상자가 없습니다.")
            return

        data[user]["summer_box"] -= 1

        rewards = [
            ("🪙 여름 코인 20개", "coin", 20),
            ("🪙 여름 코인 50개", "coin", 50),
            ("🪙 여름 코인 100개", "coin", 100),
            ("🎨 역할 색상권", "item"),
            ("✨ 닉네임 꾸미기권", "item")
        ]

    elif 종류 == "황금":

        if data[user]["gold_box"] <= 0:
            await interaction.response.send_message("❌ 황금 상자가 없습니다.")
            return

        data[user]["gold_box"] -= 1

        rewards = [
            ("🪙 여름 코인 200개", "coin", 200),
            ("🪙 여름 코인 300개", "coin", 300),
            ("🌊 바다 역할 교환권", "item"),
            ("✨ 윤슬 역할 교환권", "item")
        ]

    elif 종류 == "레전드":

        if data[user]["legend_box"] <= 0:
            await interaction.response.send_message("❌ 레전드 상자가 없습니다.")
            return

        data[user]["legend_box"] -= 1

        rewards = [
            ("🪙 여름 코인 1000개", "coin", 1000),
            ("☀️ 여름 신 역할 교환권", "item"),
            ("🎁 특별 보상", "item")
        ]

    else:
        await interaction.response.send_message(
            "사용법 : `/상자열기 여름`, `/상자열기 황금`, `/상자열기 레전드`"
        )
        return

    reward = random.choice(rewards)

    if reward[1] == "coin":
        data[user]["coins"] += reward[2]
    else:
        data[user]["inventory"].append(reward[0])

    save_data(data)

    await interaction.response.send_message(
        f"📦 **{종류} 상자를 열었습니다!**\n\n"
        f"🎉 획득 보상\n{reward[0]}"
    )


@bot.tree.command(name="인벤토리", description="아이템을 확인합니다.")
async def inventory(interaction: discord.Interaction):

    data = load_data()
    user = get_user(data, interaction.user.id)

    if "inventory" not in data[user]:
        data[user]["inventory"] = []

    if len(data[user]["inventory"]) == 0:
        text = "없음"
    else:
        text = "\n".join(data[user]["inventory"])

    await interaction.response.send_message(
        f"🎒 {interaction.user.display_name}님의 인벤토리\n\n{text}"
    )

@bot.tree.command(name="코인지급", description="여름 코인을 지급합니다.")
@app_commands.checks.has_permissions(administrator=True)
async def give_coin(
    interaction: discord.Interaction,
    유저: discord.Member,
    코인: int
):
    data = load_data()
    user = get_user(data, 유저.id)

    data[user]["coins"] += 코인
    save_data(data)

    await interaction.response.send_message(
        f"✅ {유저.mention}님에게 여름 코인 {코인}개를 지급했습니다."
    )


@bot.tree.command(name="코인회수", description="여름 코인을 회수합니다.")
@app_commands.checks.has_permissions(administrator=True)
async def remove_coin(interaction: discord.Interaction, 유저: discord.Member, 코인: int):

    data = load_data()
    user = get_user(data, 유저.id)

    data[user]["coins"] = max(0, data[user]["coins"] - 코인)
    save_data(data)

    await interaction.response.send_message(
        f"✅ {유저.mention}님의 여름 코인 {코인}개를 회수했습니다."
    )


@bot.tree.command(name="상자지급", description="상자를 지급합니다.")
@app_commands.checks.has_permissions(administrator=True)
async def give_box(
    interaction: discord.Interaction,
    유저: discord.Member,
    종류: str,
    개수: int
):

    data = load_data()
    user = get_user(data, 유저.id)

    종류 = 종류.lower()

    if 종류 == "여름":
        data[user]["summer_box"] += 개수

    elif 종류 == "황금":
        data[user]["gold_box"] += 개수

    elif 종류 == "레전드":
        data[user]["legend_box"] += 개수

    else:
        await interaction.response.send_message(
            "❌ 종류는 여름 / 황금 / 레전드 중 하나를 입력하세요."
        )
        return

    save_data(data)

    await interaction.response.send_message(
        f"📦 {유저.mention}님에게 {종류} 상자 {개수}개를 지급했습니다."
    )


@bot.tree.command(name="유저정보", description="유저 정보를 확인합니다.")
@app_commands.checks.has_permissions(administrator=True)
async def user_info(interaction: discord.Interaction, 유저: discord.Member):

    data = load_data()
    user = get_user(data, 유저.id)

    await interaction.response.send_message(
        f"""
👤 {유저.display_name}

🪙 여름 코인 : {data[user]['coins']}

📦 여름 상자 : {data[user]['summer_box']}
🟨 황금 상자 : {data[user]['gold_box']}
🌈 레전드 상자 : {data[user]['legend_box']}

📅 누적 출석 : {data[user]['attendance']}일
"""
    )

bot.run(TOKEN)
