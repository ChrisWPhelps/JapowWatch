import sqlite3

def setup_database():
    conn = sqlite3.connect('japow_watch.db')
    cursor = conn.cursor()

    #Create tables
    cursor.execute('DROP TABLE IF EXISTS resorts')
    cursor.execute('''
                   CREATE TABLE resorts
                   (
                       id         INTEGER PRIMARY KEY AUTOINCREMENT,
                       name       TEXT UNIQUE NOT NULL,
                       url        TEXT,
                       region     TEXT,
                       prefecture TEXT,
                       lat        REAL,
                       lon        REAL
                   )
                   ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS daily_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            resort_id INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            snow_depth_cm INTEGER,
            temp_celsius REAL,
            lift_status TEXT,
            live_weather TEXT,
            FOREIGN KEY (resort_id) REFERENCES resorts (id)
        )
    ''')
    #from the master resort.csv into the tables
    resort_data = [
        ("Niseko United", "https://www.niseko.ne.jp/en/status/", "Hokkaido", "Hokkaido", 42.8635, 140.7028),
        ("Rusutsu Resort", "https://rusutsu.com/en/snow-and-weather-report/", "Hokkaido", "Hokkaido", 42.7496, 140.9073),
        ("Furano Ski Resort", "https://www.princehotels.com/en/ski/furano/", "Hokkaido", "Hokkaido", 43.3417, 142.3917),
        ("Kiroro Snow World", "https://www.kiroro.co.jp/lift-status/", "Hokkaido", "Hokkaido", 43.0741, 141.0069),
        ("Hoshino Resorts TOMAMU", "https://www.snowtomamu.jp/winter/en/ski/slope/", "Hokkaido", "Hokkaido", 43.0631, 142.6311),
        ("Sapporo Teine", "https://sapporo-teine.com/snow/lang/en/", "Hokkaido", "Hokkaido", 43.0800, 141.2000),
        ("Sapporo Kokusai", "https://www.sapporo-kokusai.jp/en/status/", "Hokkaido", "Hokkaido", 43.0725, 141.0772),
        ("Kamui Ski Links", "https://www.kamui-skilinks.com/en/", "Hokkaido", "Hokkaido", 43.7333, 142.1833),
        ("Sahoro Resort", "https://sahoro.co.jp/en/ski/status", "Hokkaido", "Hokkaido", 43.1667, 142.8167),
        ("Asahidake Ropeway", "https://asahidake.hokkaido.jp/en/", "Hokkaido", "Hokkaido", 43.6500, 142.8167),
        ("Shiga Kogen", "https://www.shigakogen-ski.or.jp/lift/index-en.php", "Nagano", "Nagano", 36.7333, 138.5000),
        ("Nozawa Onsen", "https://en.nozawaski.com/mountain-info/", "Nagano", "Nagano", 36.9167, 138.4500),
        ("Hakuba Happo-One", "https://www.happo-one.jp/en/mountain/status/", "Nagano", "Nagano", 36.6982, 137.8619),
        ("ABLE Goryu & Hakuba47", "https://www.hakubagoryu.com/en/winter/mountain/status", "Nagano", "Nagano", 36.6667, 137.8333),
        ("Tsugaike Kogen", "https://www.tsugaike.gr.jp/en/gelande", "Nagano", "Nagano", 36.7500, 137.8833),
        ("Hakuba Cortina", "https://www.h-greenplazahakuba.com/en/ski/course/", "Nagano", "Nagano", 36.7833, 137.9167),
        ("Madarao Mountain Resort", "https://www.madarao.jp/en/ski/status", "Nagano", "Nagano", 36.8333, 138.2833),
        ("Karuizawa Prince Hotel", "https://www.princehotels.com/en/ski/karuizawa/", "Nagano", "Nagano", 36.3333, 138.6167),
        ("Sugadaira Kogen", "https://sugadaira-snowresort.com/en/", "Nagano", "Nagano", 36.5167, 138.3333),
        ("Togakushi Ski Resort", "https://togakusi.com/ski/en/", "Nagano", "Nagano", 36.7667, 138.0833),
        ("Naeba Ski Resort", "https://www.princehotels.com/en/ski/naeba/", "Niigata", "Niigata", 36.7917, 138.7833),
        ("Kagura Ski Resort", "https://www.seibuprince.com/mtnaeba-kagura-ski-resort", "Niigata", "Niigata", 36.8500, 138.7500),
        ("GALA Yuzawa", "https://gala.co.jp/winter/english/status/", "Niigata", "Niigata", 36.9500, 138.8000),
        ("Joetsu Kokusai", "https://jkokusai.net/english/", "Niigata", "Niigata", 37.0167, 138.8833),
        ("NASPA Ski Garden", "https://naspa.co.jp/en/ski/course/", "Niigata", "Niigata", 36.9333, 138.8000),
        ("Myoko Akakura Onsen", "https://akakura-ski.com/english/", "Niigata", "Niigata", 36.9000, 138.2000),
        ("Lotte Arai Resort", "https://www.lottehotel.com/arai-resort/en/", "Niigata", "Niigata", 37.0167, 138.1667),
        ("Ishiuchi Maruyama", "https://ishiuchi.or.jp/en/gelande/", "Niigata", "Niigata", 36.9833, 138.8500),
        ("Maiko Snow Resort", "https://www.maiko-resort.com/en/", "Niigata", "Niigata", 37.0333, 138.8500),
        ("Kandatsu Kogen", "https://www.kandatsu.com/en/price/", "Niigata", "Niigata", 36.9167, 138.8167),
        ("Zao Onsen", "http://www.zao-ski.or.jp/english/status/", "Tohoku", "Yamagata", 38.1667, 140.4000),
        ("Appi Kogen", "https://www.appi-japan.com/weather-lift/", "Tohoku", "Iwate", 40.0000, 140.9667),
        ("Nekoma Mountain", "https://hoshinoresorts.com/en/sp/bandaisan_snow/", "Tohoku", "Fukushima", 37.6333, 140.0667),
        ("Geto Kogen Resort", "https://www.getokogen.com/winter_en/04activity/mountain.html", "Tohoku", "Iwate", 39.2333, 140.9167),
        ("Hakkoda Ski Resort", "https://aomori-tourism.com/en/spot/detail_9116.html", "Tohoku", "Aomori", 40.7000, 140.8500),
        ("Grandeco Snow Resort", "https://fukushima.travel/destination/en-resort-grandeco-hotel-ski/34", "Tohoku", "Fukushima", 37.6833, 140.1167),
        ("Hachimantai Resort", "https://hachimantai-mountainhotel.com/en/news/", "Tohoku", "Iwate", 39.9167, 140.9833),
        ("Aomori Spring", "https://aomorispringresort.com/en/", "Tohoku", "Aomori", 40.7333, 140.2333),
        ("Tazawako Ski Resort", "https://www.tazawako-ski.com/en/", "Tohoku", "Akita", 39.7667, 140.7500),
        ("Inawashiro Ski Resort", "https://www.inawashiro-ski.com/service/isk/?locale=en", "Tohoku", "Fukushima", 37.5833, 140.1167)
    ]

    cursor.executemany('INSERT INTO resorts (name, url, region, prefecture, lat, lon) VALUES (?, ?, ?, ?, ?, ?)', resort_data)

    conn.commit()
    conn.close()

    #check
    print(f"Successfully initialized and seeded {len(resort_data)} resorts with coordinates.")

if __name__ == "__main__":
    setup_database()