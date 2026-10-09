# Фильтр по типу одежды. Определяем тип по названию лота (латиница + японский).
# Если у подписчика типы не выбраны, пропускаем всё.
import re

KW = {'шапка': ['beanie', 'knit hat', 'knit cap', 'balaclava', 'ニット帽', 'ビーニー', 'ニットキャップ', 'バラクラバ', '目出し帽', '防寒帽'],
 'кепка': ['cap', 'snapback', 'baseball cap', 'trucker', 'キャップ', 'スナップバック', 'ワークキャップ', 'ストラップバック'],
 'шляпа': ['hat', 'bucket hat', 'fedora', 'beret', 'ハット', '中折れ', 'ベレー帽', 'フェドーラ'],
 'куртка': ['jacket',
            'bomber',
            'blouson',
            'parka',
            'down jacket',
            'ジャケット',
            'ブルゾン',
            'ライダース',
            'ダウン',
            'ミリタリー',
            'スタジャン',
            'gジャン',
            'ma-1'],
 'пальто': ['coat',
            'overcoat',
            'trench',
            'peacoat',
            'pea coat',
            'コート',
            'ステンカラー',
            'トレンチ',
            'チェスター',
            'ピーコート',
            'ダッフル'],
 'ветровка': ['windbreaker',
              'anorak',
              'shell jacket',
              'track jacket',
              'nylon jacket',
              'ウィンドブレーカー',
              'ウインドブレーカー',
              'ナイロンジャケット',
              'マウンテンパーカー',
              'アノラック',
              'シェルジャケット'],
 'жилетка': ['vest', 'gilet', 'waistcoat', 'ベスト', 'ジレ', 'ダウンベスト'],
 'зипка': ['zip hoodie',
           'zip up hoodie',
           'zip-up',
           'zip up',
           'full zip',
           'zipup',
           'ジップパーカー',
           'ジップアップ',
           'フルジップ',
           'ジップ パーカー'],
 'худи': ['hoodie', 'hooded', 'pullover hoodie', 'パーカー', 'フーディ', 'プルオーバーパーカー'],
 'свитшот': ['sweatshirt', 'crewneck', 'crew neck', 'sweat', 'スウェット', 'トレーナー', 'クルーネック'],
 'лонгслив': ['long sleeve', 'longsleeve', 'long-sleeve', 'l/s', 'ロンt', '長袖', 'ロングスリーブ'],
 'футболка': ['t-shirt', 'tshirt', 't shirt', 'tee', 'tee shirt', 'tシャツ', 'ティーシャツ', '半袖'],
 'майка': ['tank top', 'tank', 'singlet', 'sleeveless', 'camisole', 'タンクトップ', 'ノースリーブ', 'キャミソール'],
 'браслет': ['bracelet', 'bangle', 'cuff', 'ブレスレット', 'バングル', 'カフ'],
 'кольцо': ['ring', 'signet', '指輪', 'ピンキーリング', 'シグネットリング', 'シルバーリング', '印台'],
 'сумка': ['bag',
           'tote',
           'shoulder bag',
           'crossbody',
           'messenger',
           'handbag',
           'pouch',
           'clutch',
           'バッグ',
           'ショルダー',
           'ポーチ',
           'クラッチ',
           'メッセンジャー',
           'ボストン'],
 'рюкзак': ['backpack', 'rucksack', 'daypack', 'back pack', 'リュック', 'バックパック', 'デイパック', 'ザック'],
 'штаны': ['pants',
           'trousers',
           'cargo',
           'slacks',
           'sweatpants',
           'joggers',
           'track pants',
           'パンツ',
           'スラックス',
           'カーゴ',
           'ボトムス',
           'トラウザー',
           'ジョガー'],
 'джинсы': ['jeans', 'denim pants', 'ジーンズ', 'ジーパン', 'デニムパンツ'],
 'шорты': ['shorts', 'short pants', 'ショーツ', 'ハーフパンツ', 'ショートパンツ', '短パン'],
 'носки': ['socks', 'sock', 'ソックス', '靴下'],
 'кроссовки': ['sneakers', 'sneaker', 'trainers', 'runners', 'running shoes', 'スニーカー', 'ランニングシューズ'],
 'ботинки': ['boots', 'boot', 'derby', 'oxford', 'loafers', 'leather shoes', 'ブーツ', 'ブーティ', '革靴', 'ドレスシューズ'],
 'казаки': ['cowboy boots',
            'cowboy boot',
            'western boots',
            'cossack',
            'ウエスタンブーツ',
            'ウェスタンブーツ',
            'カウボーイブーツ',
            'テキサスブーツ'],
 'кеды': ['canvas shoes', 'canvas sneaker', 'low top', 'low-top', 'chuck 70', 'all star', 'キャンバス', 'ローカット'],
 'высокие кеды': ['high top', 'high-top', 'hi top', 'hi-top', 'chuck taylor', 'ハイカット', 'ハイトップ']}

def _compile(kw_by_type):
    out = {}
    for t, kws in kw_by_type.items():
        parts = []
        for k in kws:
            k = k.lower()
            if re.fullmatch(r"[a-z0-9 \-/.]+", k):
                parts.append(r"(?<![a-z0-9])" + re.escape(k) + r"s?(?![a-z0-9])")
            else:
                parts.append(re.escape(k))
        out[t] = re.compile("|".join(parts))
    return out

_MATCHERS = _compile(KW)


def type_ok(title, wanted):
    wanted = [w for w in (wanted or []) if w in _MATCHERS]
    if not wanted:
        return True
    t = (title or "").lower()
    return any(_MATCHERS[w].search(t) for w in wanted)
