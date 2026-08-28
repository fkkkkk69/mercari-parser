import asyncio
import json
import os
import time

import telebot
from mercapi import Mercapi

# Секреты берутся из переменных окружения, не хранятся в коде
TOKEN = os.environ["TG_BOT_TOKEN"]
CHAT_ID = int(os.environ["TG_CHAT_ID"])

bot = telebot.TeleBot(TOKEN)
m = Mercapi()

# Ключевые слова для поиска (японский + английский)
KEYWORDS = [
    # Японские названия
    "アンダーカバー",        # Undercover
    "ナンバーナイン",        # Number Nine
    "ヒステリックグラマー",   # Hysteric Glamour
    "リックオウエンス",      # Rick Owens
    "ラフシモンズ",          # Raf Simons
    "ジェレミースコット",    # Jeremy Scott
    "ヴィヴィアンウエストウッド",  # Vivienne Westwood
    "ジュンヤワタナベ",      # Junya Watanabe
    "コムデギャルソン",      # CDG
    "ヘルムートラング",      # Helmut Lang
    "モスキーノ",            # Moschino
    "バルマン",              # Balmain
    "ディーゼル",            # Diesel
    "グッチ",               # Gucci
    "プラダ",               # Prada
    # Английские названия
    "undercover",
    "number nine",
    "hysteric glamour",
    "rick owens",
    "raf simons",
    "jeremy scott",
    "walter van beirendonck",
    "424",
    "gucci",
    "prada",
    "helmut lang",
    "moschino",
    "junya watanabe",
    "diesel",
    "balmain",
    "ppfm",
    "tornado mart",
    "vivienne westwood",
    "c2h4",
]
SEEN_FILE = "seen.json"
DELAY_BETWEEN_KEYWORDS = 3  # сек, чтобы не словить рейт-лимит
POLL_INTERVAL = 300  # сек


def load_seen():
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, "r") as f:
            return set(json.load(f))
    return set()


def save_seen(seen):
    with open(SEEN_FILE, "w") as f:
        json.dump(list(seen), f)


async def search_mercari(keyword):
    try:
        results = await m.search(keyword)
        return results.items
    except Exception as e:
        print(f"Ошибка поиска '{keyword}': {e}")
        return []


async def check_new():
    seen = load_seen()
    first_run = len(seen) == 0
    new_items = []

    for keyword in KEYWORDS:
        items = await search_mercari(keyword)
        for item in items:
            item_id = item.id_
            if item_id and item_id not in seen:
                seen.add(item_id)
                if not first_run:
                    new_items.append({
                        "id": item_id,
                        "name": item.name,
                        "price": item.price,
                        "keyword": keyword,
                        "url": f"https://jp.mercari.com/item/{item_id}",
                    })
        await asyncio.sleep(DELAY_BETWEEN_KEYWORDS)

    save_seen(seen)
    if first_run:
        print(f"Первый запуск: сохранено {len(seen)} товаров как уже виденные, уведомления не отправлены.")
    return new_items


def notify(item):
    text = (
        f"🆕 Новый товар на Mercari!\n\n"
        f"*{item['name']}*\n"
        f"💴 ¥{item['price']}\n"
        f"🔍 Запрос: {item['keyword']}\n"
        f"🔗 [Открыть]({item['url']})"
    )
    bot.send_message(CHAT_ID, text, parse_mode="Markdown")


async def main():
    print("Проверяю...")
    new = await check_new()
    for item in new:
        notify(item)
        print(f"Новый: {item['name']} — ¥{item['price']}")
        await asyncio.sleep(1)  # защита от 429 Too Many Requests в Telegram
    if not new:
        print("Новых нет.")


if __name__ == "__main__":
    run_once = os.environ.get("RUN_ONCE", "0") == "1"
    if run_once:
        # Режим для GitHub Actions / cron: одна проверка и выход
        asyncio.run(main())
    else:
        # Режим постоянного демона (например, для Railway)
        print("Парсер запущен. Проверка каждые 5 минут...")
        while True:
            asyncio.run(main())
            time.sleep(POLL_INTERVAL)
