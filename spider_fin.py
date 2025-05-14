import requests
import pandas as pd
import time
from datetime import datetime
import sqlite3
from sqlite3 import Error


class GoldFuturesSpider:
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Referer": "https://quote.eastmoney.com/"
        }
        self.api_url = "https://push2.eastmoney.com/api/qt/stock/get"
        self.db_file = "maotai_futures.db"  # 数据库文件名
        self.create_connection()  # 初始化数据库连接
        self.create_table()  # 创建数据表

    def create_connection(self):
        """创建数据库连接"""
        self.conn = None
        try:
            self.conn = sqlite3.connect(self.db_file)
            print(f"成功连接到SQLite数据库: {self.db_file}")
        except Error as e:
            print(f"连接数据库时出错: {e}")

    def create_table(self):
        """创建数据表"""
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS gold_futures (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            latest_price REAL,
            change_amount REAL,
            change_percent REAL,
            open_price REAL,
            high_price REAL,
            low_price REAL,
            prev_close REAL,
            volume INTEGER,
            turnover REAL,
            open_interest INTEGER,
            settlement_price REAL,
            update_time TEXT
        );
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(create_table_sql)
            print("数据表已创建或已存在")
        except Error as e:
            print(f"创建表时出错: {e}")

    def get_gold_futures_data(self):
        """获取茅台数据"""
        params = {
            'secid': '1.600519',
            'fields': 'f43,f57,f58,f169,f170,f46,f44,f51,f168,f47,f164,f163,f116,f60,f45,f52,f50,f48,f167,f117,f71,f161,f49,f530,f135,f136,f137,f138,f139,f141,f142,f144,f145,f147,f148,f140,f143,f146,f149,f55,f62,f162,f92,f173,f104,f105,f84,f85,f183,f184,f185,f186,f187,f188,f189,f190,f191,f192,f107,f111,f86,f177,f78,f110,f262,f263,f264,f267,f268,f250,f251,f252,f253,f254,f255,f256,f257,f258,f266,f269,f270,f271,f273,f274,f275,f127,f199,f128,f193,f196,f194,f195,f197,f80,f280,f281,f282,f284,f285,f286,f287,f292',
            'invt': '2',
            'fltt': '2',
            '_': int(time.time() * 1000)
        }

        try:
            response = self.session.get(self.api_url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data.get('data'):
                return self.parse_data(data['data'])
            return None
        except Exception as e:
            print(f"获取数据失败: {e}")
            return None

    def parse_data(self, raw_data):
        """解析原始数据"""
        return {
            'name': raw_data.get('f57', 'N/A'),
            'latest_price': raw_data.get('f43', 'N/A') / 100 if raw_data.get('f43') else 'N/A',
            'change_amount': raw_data.get('f169', 'N/A') / 100 if raw_data.get('f169') else 'N/A',
            'change_percent': raw_data.get('f170', 'N/A'),
            'open_price': raw_data.get('f46', 'N/A') / 100 if raw_data.get('f46') else 'N/A',
            'high_price': raw_data.get('f44', 'N/A') / 100 if raw_data.get('f44') else 'N/A',
            'low_price': raw_data.get('f45', 'N/A') / 100 if raw_data.get('f45') else 'N/A',
            'prev_close': raw_data.get('f60', 'N/A') / 100 if raw_data.get('f60') else 'N/A',
            'volume': raw_data.get('f47', 'N/A'),
            'turnover': raw_data.get('f48', 'N/A'),
            'open_interest': raw_data.get('f117', 'N/A'),
            'settlement_price': raw_data.get('f46', 'N/A') / 100 if raw_data.get('f46') else 'N/A',
            'update_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    def save_to_database(self, data):
        """保存数据到数据库"""
        insert_sql = """
        INSERT INTO gold_futures (
            name, latest_price, change_amount, change_percent, open_price, 
            high_price, low_price, prev_close, volume, turnover, 
            open_interest, settlement_price, update_time
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        try:
            cursor = self.conn.cursor()
            cursor.execute(insert_sql, (
                data['name'],
                data['latest_price'],
                data['change_amount'],
                data['change_percent'],
                data['open_price'],
                data['high_price'],
                data['low_price'],
                data['prev_close'],
                data['volume'],
                data['turnover'],
                data['open_interest'],
                data['settlement_price'],
                data['update_time']
            ))
            self.conn.commit()
            print("数据已成功保存到数据库")
            return True
        except Error as e:
            print(f"保存数据到数据库时出错: {e}")
            return False

    def get_latest_data(self, limit=5):
        """从数据库获取最新的几条数据"""
        select_sql = f"""
        SELECT * FROM gold_futures 
        ORDER BY update_time DESC 
        LIMIT {limit}
        """

        try:
            cursor = self.conn.cursor()
            cursor.execute(select_sql)
            rows = cursor.fetchall()

            # 获取列名
            columns = [description[0] for description in cursor.description]

            # 将结果转换为字典列表
            results = []
            for row in rows:
                results.append(dict(zip(columns, row)))

            return results
        except Error as e:
            print(f"从数据库获取数据时出错: {e}")
            return None

    def close_connection(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()
            print("数据库连接已关闭")

    def run(self):
        """执行爬虫"""
        print("开始获取数据...")
        data = self.get_gold_futures_data()

        if data:
            print("\n获取成功！数据如下：")
            for k, v in data.items():
                print(f"{k}: {v}")

            # 保存到数据库
            if self.save_to_database(data):
                # 查询并显示最新的几条数据
                print("\n数据库中最新记录：")
                latest_records = self.get_latest_data()
                if latest_records:
                    for record in latest_records:
                        print("\n记录:")
                        for k, v in record.items():
                            print(f"{k}: {v}")
        else:
            print("未能获取有效数据")

        # 关闭数据库连接
        self.close_connection()


if __name__ == "__main__":
    spider = GoldFuturesSpider()
    spider.run()