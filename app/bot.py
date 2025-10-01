import discord
import requests
import os

TOKEN = os.environ.get("DISCORD_BOT_TOKEN")  # 環境変数からBotトークン取得

# 必須APIパラメータ
API_BASE = "https://api.programmingzemi.com/api/v1/apps/wjzZKZ5XF19UDHCyGsG8/works"
API_PARAMS = {
    "app": "com.programmingzemi",
    "device": "uYNOM0Ey4GNzPgwyHCQOJ",
    "app_ver": "1.11.0",
    "build": "7d694f0e5",
    "model_name": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:142.0) Gecko/20100101 Firefox/142.0",
    "os": "browser",
    "os_ver": "Windows firefox 142.0",
    "api_token": "5SqP1VroD5cXeMUH_UfT",
}

intents = discord.Intents.default()
bot = discord.Client(intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.content.startswith("!prosemiuser"):
        nickname = message.content[len("!prosemiuser"):].strip()
        if not nickname:
            await message.channel.send("検索するユーザー名を入力してください。\n例: `!prosemiuser 蓮花蝶`")
            return

        params = API_PARAMS.copy()
        params["per_page"] = 5
        params["page"] = 1
        params["nickname"] = nickname

        try:
            res = requests.get(API_BASE, params=params)
            if res.status_code != 200:
                await message.channel.send("APIリクエストに失敗しました。")
                return

            data = res.json()
            projects = data.get("projects", [])
            if not projects:
                await message.channel.send(f"ユーザー「{nickname}」の作品は見つかりませんでした。")
                return

            reply = f"**{nickname}さんのプロゼミ作品一覧**\n"
            for proj in projects:
                reply += (
                    f"\n▶︎ [{proj['name']}]({proj['url']})\n"
                    f"　👍{proj['like']}　👁{proj['view']}　🔁{proj['remix']}\n"
                    f"　[サムネイル]({proj['thumbnail']})\n"
                )
            await message.channel.send(reply)
        except Exception as e:
            await message.channel.send(f"エラーが発生しました: {e}")

bot.run(TOKEN)
