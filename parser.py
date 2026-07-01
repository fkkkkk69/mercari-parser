import requests
import telebot
import time
import json
import os

TOKEN = "8758293670:AAGeeusbVT6t0Bo2XLSBhioKYnisrTNZ__g"
CHAT_ID = 2034814464

bot = telebot.TeleBot(TOKEN)

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

def load_seen():
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, "r") as f:
            return json.load(f)
    return []

def save_seen(seen):
    with open(SEEN_FILE, "w") as f:
        json.dump(seen, f)

def search_mercari(keyword):
    url = "https://api.mercari.jp/v2/entities:search"
    payload = {
        "pageSize": 20,
        "pageToken": "",
        "searchSessionId": "test",
        "indexRouting": "INDEX_ROUTING_UNSPECIFIED",
        "searchCondition": {
            "keyword": keyword,
            "excludeKeyword": "",
            "sort": "SORT_CREATED_TIME",
            "order": "ORDER_DESC",
            "status": ["STATUS_ON_SALE"],
            "categoryId": [],
        },
        "defaultDatasets": ["DATASET_TYPE_MERCARI"]
    }
    headers = {
        "User-Agent": "Mozilla/5.0",
        "X-Platform": "web",
        "Accept": "application/json",
        "Content-Type": "application/json",
        "DPoP": "test"
    }
    try:
        r = requests.post(url, json=payload, headers=headers, timeout=10)
        if r.status_code == 200:
            data = r.json()
            return data.get("items", [])
    except Exception as e:
        print(f"Ошибка: {e}")
    return []

def check_new():
    seen = load_seen()
    new_items = []

    for keyword in KEYWORDS:
        items = search_mercari(keyword)
        for item in items:
            item_id = item.get("id")
            if item_id and item_id not in seen:
                seen.append(item_id)
                new_items.append({
                    "id": item_id,
                    "name": item.get("name", ""),
                    "price": item.get("price", 0),
                    "keyword": keyword,
                    "url": f"https://jp.mercari.com/item/{item_id}"
                })

    save_seen(seen)
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

print("Парсер запущен. Проверка каждые 5 минут...")

while True:
    print("Проверяю...")
    new = check_new()
    for item in new:
        notify(item)
        print(f"Новый: {item['name']} — ¥{item['price']}")
    if not new:
        print("Новых нет.")
    time.sleep(300)