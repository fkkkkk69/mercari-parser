import asyncio
import json
import os
import time

import requests
import telebot
from mercapi import Mercapi

# Секреты берутся из переменных окружения, не хранятся в коде
TOKEN = os.environ["TG_BOT_TOKEN"]
WORKER_URL = os.environ["WORKER_URL"]  # напр. https://mercari-bot-worker.<sub>.workers.dev
API_SECRET = os.environ["API_SECRET"]

bot = telebot.TeleBot(TOKEN)
m = Mercapi()

# Ключевые слова для поиска (японский + английский)
KEYWORDS = [
    "アンダーカバー",
    "ナンバーナイン",
    "ヒステリックグラマー",
    "リックオウエンス",
    "ラフシモンズ",
    "ジェレミースコット",
    "ヴィヴィアンウエストウッド",
    "ジュンヤワタナベ",
    "コムデギャルソン",
    "ヘルムートラング",
    "モスキーノ",
    "バルマン",
    "ディーゼル",
    "グッチ",
    "プラダ",
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
    "john galliano",
    "maison margiela",
    "jean paul gaultier",
    "amiri",
    "issey miyake",
    "carol christian poell",
    "stone island",
    "yohji yamamoto",
    "y-3",
    "boris bidjan saberi",
    "bernhard willhelm",
    "hussein chalayan",
    "ann demeulemeester",
    "dries van noten",
    "dirk bikkembergs",
    "marina yee",
    "craig green",
    "kiko kostadinov",
    "post archive faction",
    "kanghyuk",
    "andersson bell",
    "hyein seo",
    "jil sander",
    "lemaire",
    "carpe diem",
    "m.a+",
    "label under construction",
    "layer-0",
    "julius",
    "devoa",
    "ziggy chen",
    "uma wang",
    "inaisce",
    "guidi",
    "a1923",
    "individual sentiments",
    "obscur",
    "leon emanuel blanck",
    "thom krom",
    "off-white",
    "balenciaga",
    "vetements",
    "chrome hearts",
    "gallery dept",
    "palm angels",
    "casablanca",
    "rhude",
    "givenchy",
    "dior homme",
    "louis vuitton",
    "heron preston",
    "fear of god",
    "yeezy",
    "sp5der",
    "denim tears",
    "hellstar",
    "corteiz",
    "c.p. company",
    "nike",
    "arcteryx",
    "moncler",
    "canada goose",
    "trapstar",
    "syna world",
    "benjart",
    "hoodrich",
    "burberry",
    "lacoste",
    "the north face",
    "oakley",
    "salomon",
    "asics",
    "saint laurent",
    "ysl",
    "dior",
    "the kooples",
    "allsaints",
    "zadig & voltaire",
    "american apparel",
    "urban outfitters",
    "cheap monday",
    "unif",
    "marc jacobs",
    "tripp nyc",
    "lip service",
    "dr. martens",
    "converse",
    "juicy couture",
    "von dutch",
    "ed hardy",
    "kmiri",
    "lgb",
    "20471120",
    "chanel",
    "if six was nine",
]
SEEN_FILE = "seen.json"
DELAY_BETWEEN_KEYWORDS = 3
POLL_INTERVAL = 300


def load_seen():
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, "r") as f:
            return set(json.load(f))
    return set()


def save_seen(seen):
    with open(SEEN_FILE, "w") as f:
        json.dump(list(seen), f)


def get_subscribers():
    try:
        r = requests.get(f"{WORKER_URL}/subscribers", headers={"X-API-Key": API_SECRET}, timeout=15)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"Не удалось получить подписчиков: {e}")
        return []


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
                        "keyword": keyword.lower(),
                        "url": f"https://jp.mercari.com/item/{item_id}",
                    })
        await asyncio.sleep(DELAY_BETWEEN_KEYWORDS)

    save_seen(seen)
    if first_run:
        print(f"Первый запуск: сохранено {len(seen)} товаров как уже виденные, уведомления не отправлены.")
    return new_items


def matches(item, sub):
    brands = [b.lower() for b in sub.get("brands", [])]
    if brands and not any(b in item["keyword"] or b in item["name"].lower() for b in brands):
        return False
    price = item["price"]
    if price < sub.get("price_min", 0) or price > sub.get("price_max", 9999999):
        return False
    return True


def notify(chat_id, item):
    text = (
        f"🆕 Новый товар на Mercari!\n\n"
        f"*{item['name']}*\n"
        f"💴 ¥{item['price']}\n"
        f"🔍 Запрос: {item['keyword']}\n"
        f"🔗 [Открыть]({item['url']})"
    )
    try:
        bot.send_message(int(chat_id), text, parse_mode="Markdown")
    except Exception as e:
        print(f"Не удалось отправить {chat_id}: {e}")


async def main():
    print("Проверяю...")
    new = await check_new()
    debug_lines = [f"=== run at {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())} ==="]
    if not new:
        print("Новых нет.")
        debug_lines.append("no new items")
        with open("debug_log.txt", "a") as f:
            f.write("\n".join(debug_lines) + "\n")
        return

    subs = get_subscribers()
    debug_lines.append(f"new items: {len(new)}, subscribers: {len(subs)}")
    for s in subs:
        debug_lines.append(f"  sub {s.get('chat_id')}: brands={s.get('brands')}, price={s.get('price_min')}-{s.get('price_max')}, active={s.get('active')}")

    print(f"Найдено новых: {len(new)}, подписчиков: {len(subs)}")

    for item in new:
        debug_lines.append(f"item: {item['name'][:30]} kw={item['keyword']} price={item['price']}")
        for sub in subs:
            m = matches(item, sub)
            debug_lines.append(f"    vs {sub.get('chat_id')} -> {m}")
            if m:
                notify(sub["chat_id"], item)
                await asyncio.sleep(1)

    with open("debug_log.txt", "a") as f:
        f.write("\n".join(debug_lines) + "\n")


if __name__ == "__main__":
    run_once = os.environ.get("RUN_ONCE", "0") == "1"
    if run_once:
        asyncio.run(main())
    else:
        print("Парсер запущен. Проверка каждые 5 минут...")
        while True:
            asyncio.run(main())
            time.sleep(POLL_INTERVAL)
