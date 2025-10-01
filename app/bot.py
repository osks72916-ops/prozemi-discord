import discord
import requests
import os
from collections import defaultdict

# ==== 設定 ====
TOKEN = os.environ.get("DISCORD_BOT_TOKEN")  # Botトークンは環境変数で管理

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

# バッジを付けるユーザー（author_infoがキー、バッジ画像URLが値）
VERIFIED_USERS = {
    "Y4ud Umc8": "https://yourdomain.com/badge1.png",   # 例: 蓮花蝶さん
    "ABCD1234":  "https://yourdomain.com/badge2.png",   # 他の認証ユーザー
}

# ユーザー検索結果の一時キャッシュ
user_search_cache = {}

intents = discord.Intents.default()
bot = discord.Client(intents=intents)

# ==== Botイベント ====

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # ユーザー一覧検索
    if message.content.startswith("!prosemiuser"):
        nickname_query = message.content[len("!prosemiuser"):].strip()
        if not nickname_query:
            await message.channel.send("検索するユーザー名を入力してください。\n例: `!prosemiuser 蓮花蝶`")
            return

        params = API_PARAMS.copy()
        params["per_page"] = 15
        params["page"] = 1
        params["nickname"] = nickname_query

        try:
            res = requests.get(API_BASE, params=params)
            if res.status_code != 200:
                await message.channel.send("APIリクエストに失敗しました。")
                return

            data = res.json()
            projects = data.get("projects", [])
            if not projects:
                await message.channel.send(f"ユーザー「{nickname_query}」の作品は見つかりませんでした。")
                return

            # author_info（ユーザーID）ごとにまとめてリストアップ
            user_dict = defaultdict(list)
            for proj in projects:
                user_dict[(proj['author'], proj['author_info'])].append(proj)

            # 表示用リストと、ユーザーキャッシュ保存
            user_list = []
            search_key = f"{message.author.id}:{nickname_query}"
            user_search_cache[search_key] = []
            for idx, ((author, author_info), projs) in enumerate(user_dict.items(), 1):
                user_id_tag = f"{author}#{idx}"
                badge_url = VERIFIED_USERS.get(author_info)
                badge_txt = f"[バッジ画像]({badge_url})" if badge_url else ""
                user_list.append(f"{user_id_tag} (ID: {author_info}) {badge_txt} 作品数: {len(projs)}")
                user_search_cache[search_key].append({
                    "author": author,
                    "author_info": author_info,
                    "user_id_tag": user_id_tag,
                    "projects": projs
                })

            reply = f"**「{nickname_query}」での検索結果：**\n"
            reply += "\n".join(user_list)
            reply += "\n\n詳細を見たい場合は `!prosemiprofile ユーザー名#番号` で指定してください。"
            await message.channel.send(reply)

        except Exception as e:
            await message.channel.send(f"エラーが発生しました: {e}")

    # プロファイル・作品表示
    if message.content.startswith("!prosemiprofile"):
        arg = message.content[len("!prosemiprofile"):].strip()
        if not arg or "#" not in arg:
            await message.channel.send("ユーザー名#番号の形式で入力してください。\n例: `!prosemiprofile 蓮花蝶#1`")
            return

        nickname, idx_str = arg.rsplit("#", 1)
        try:
            idx = int(idx_str)
        except ValueError:
            await message.channel.send("番号部分が正しくありません。")
            return

        # 前回の検索キャッシュから取得
        search_key = f"{message.author.id}:{nickname}"
        users = user_search_cache.get(search_key)
        if not users or idx < 1 or idx > len(users):
            await message.channel.send("指定されたユーザーは見つかりませんでした。\nまず `!prosemiuser ユーザー名` で検索してください。")
            return

        user = users[idx - 1]
        author_info = user['author_info']
        badge_url = VERIFIED_USERS.get(author_info)
        # 名前欄＋バッジ
        if badge_url:
            name_line = f"**{user['user_id_tag']}**\n[バッジ画像]({badge_url})\n"
        else:
            name_line = f"**{user['user_id_tag']}**\n"

        reply = f"{name_line}\n**作品一覧**\n"
        for proj in user['projects']:
            reply += (
                f"\n▶︎ [{proj['name']}]({proj['url']})\n"
                f"　👍{proj['like']}　👁{proj['view']}　🔁{proj['remix']}\n"
                f"　[サムネイル]({proj['thumbnail']})\n"
            )
        await message.channel.send(reply)

# ==== 起動 ====
bot.run(TOKEN)
