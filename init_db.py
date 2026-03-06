import sqlite3


def setup_database():
    conn = sqlite3.connect('japow_watch.db')
    cursor = conn.cursor()

    #Create Tables
    cursor.execute('DROP TABLE IF EXISTS resorts')  # Reset for clean seed
    cursor.execute('''
                   CREATE TABLE resorts
                   (
                       id         INTEGER PRIMARY KEY AUTOINCREMENT,
                       name       TEXT UNIQUE NOT NULL,
                       url        TEXT,
                       region     TEXT,
                       prefecture TEXT
                   )
                   ''')

    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS daily_stats
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       resort_id
                       INTEGER,
                       timestamp
                       DATETIME
                       DEFAULT
                       CURRENT_TIMESTAMP,
                       snow_depth_cm
                       INTEGER,
                       temp_celsius
                       REAL,
                       lift_status
                       TEXT,
                       FOREIGN
                       KEY
                   (
                       resort_id
                   ) REFERENCES resorts
                   (
                       id
                   )
                       )
                   ''')

    #Master resorts table
    resort_data = [
        ("Niseko United", "https://www.niseko.ne.jp/en/status/", "Hokkaido", "Hokkaido"),
        ("Rusutsu Resort", "https://rusutsu.com/en/snow-and-weather-report/", "Hokkaido", "Hokkaido"),
        ("Furano Ski Resort", "https://www.princehotels.com/en/ski/furano/", "Hokkaido", "Hokkaido"),
        ("Kiroro Snow World", "https://www.kiroro.co.jp/lift-status/", "Hokkaido", "Hokkaido"),
        ("Hoshino Resorts TOMAMU", "https://www.snowtomamu.jp/winter/en/ski/slope/", "Hokkaido", "Hokkaido"),
        ("Sapporo Teine", "https://sapporo-teine.com/snow/lang/en/", "Hokkaido", "Hokkaido"),
        ("Sapporo Kokusai", "https://www.sapporo-kokusai.jp/en/status/", "Hokkaido", "Hokkaido"),
        ("Kamui Ski Links", "https://www.kamui-skilinks.com/en/", "Hokkaido", "Hokkaido"),
        ("Sahoro Resort", "https://sahoro.co.jp/en/ski/status", "Hokkaido", "Hokkaido"),
        ("Asahidake Ropeway", "https://asahidake.hokkaido.jp/en/", "Hokkaido", "Hokkaido"),
        ("Shiga Kogen", "https://www.shigakogen-ski.or.jp/lift/index-en.php", "Nagano", "Nagano"),
        ("Nozawa Onsen", "https://en.nozawaski.com/mountain-info/", "Nagano", "Nagano"),
        ("Hakuba Happo-One", "https://www.happo-one.jp/en/mountain/status/", "Nagano", "Nagano"),
        ("ABLE Goryu & Hakuba47", "https://www.hakubagoryu.com/en/winter/mountain/status", "Nagano", "Nagano"),
        ("Tsugaike Kogen", "https://www.tsugaike.gr.jp/en/gelande", "Nagano", "Nagano"),
        ("Hakuba Cortina", "https://www.h-greenplazahakuba.com/en/ski/course/", "Nagano", "Nagano"),
        ("Madarao Mountain Resort", "https://www.madarao.jp/en/ski/status", "Nagano", "Nagano"),
        ("Karuizawa Prince Hotel", "https://www.princehotels.com/en/ski/karuizawa/", "Nagano", "Nagano"),
        ("Sugadaira Kogen", "https://sugadaira-snowresort.com/en/", "Nagano", "Nagano"),
        ("Togakushi Ski Resort", "https://togakusi.com/ski/en/", "Nagano", "Nagano"),
        ("Naeba Ski Resort", "https://www.princehotels.com/en/ski/naeba/", "Niigata", "Niigata"),
        ("Kagura Ski Resort", "https://www.seibuprince.com/mtnaeba-kagura-ski-resort", "Niigata", "Niigata"),
        ("GALA Yuzawa", "https://gala.co.jp/winter/english/status/", "Niigata", "Niigata"),
        ("Joetsu Kokusai", "https://jkokusai.net/english/", "Niigata", "Niigata"),
        ("NASPA Ski Garden", "https://naspa.co.jp/en/ski/course/", "Niigata", "Niigata"),
        ("Myoko Akakura Onsen", "https://akakura-ski.com/english/", "Niigata", "Niigata"),
        ("Lotte Arai Resort", "https://www.lottehotel.com/arai-resort/en/", "Niigata", "Niigata"),
        ("Ishiuchi Maruyama", "https://ishiuchi.or.jp/en/gelande/", "Niigata", "Niigata"),
        ("Maiko Snow Resort", "https://www.maiko-resort.com/en/", "Niigata", "Niigata"),
        ("Kandatsu Kogen", "https://www.kandatsu.com/en/price/", "Niigata", "Niigata"),
        ("Zao Onsen", "http://www.zao-ski.or.jp/english/status/", "Tohoku", "Yamagata"),
        ("Appi Kogen", "https://www.appi-japan.com/weather-lift/", "Tohoku", "Iwate"),
        ("Nekoma Mountain", "https://hoshinoresorts.com/en/sp/bandaisan_snow/", "Tohoku", "Fukushima"),
        ("Geto Kogen Resort", "https://www.getokogen.com/winter_en/04activity/mountain.html", "Tohoku", "Iwate"),
        ("Hakkoda Ski Resort", "https://aomori-tourism.com/en/spot/detail_9116.html", "Tohoku", "Aomori"),
        ("Grandeco Snow Resort", "https://fukushima.travel/destination/en-resort-grandeco-hotel-ski/34", "Tohoku",
         "Fukushima"),
        ("Hachimantai Resort", "https://hachimantai-mountainhotel.com/en/news/", "Tohoku", "Iwate"),
        ("Aomori Spring", "https://aomorispringresort.com/en/", "Tohoku", "Aomori"),
        ("Tazawako Ski Resort", "https://www.tazawako-ski.com/en/", "Tohoku", "Akita"),
        ("Inawashiro Ski Resort", "https://www.inawashiro-ski.com/service/isk/?locale=en", "Tohoku", "Fukushima")
    ]

    cursor.executemany('INSERT INTO resorts (name, url, region, prefecture) VALUES (?, ?, ?, ?)', resort_data)

    conn.commit()
    conn.close()
    print(f"Successfully initialized and seeded {len(resort_data)} resorts.")


if __name__ == "__main__":
    setup_database()