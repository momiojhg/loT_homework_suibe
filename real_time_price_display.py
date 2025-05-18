import requests
import time
from datetime import datetime

class GoldFuturesSpider:
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Referer": "https://quote.eastmoney.com/"
        }
        self.api_url = "https://push2.eastmoney.com/api/qt/stock/get"

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


if __name__ == "__main__":
    spider = GoldFuturesSpider()
    while True:
        data = spider.get_gold_futures_data()
        if data:
            print(f"茅台当前价格: {data['latest_price']}")
        else:
            print("未能获取有效数据")
        time.sleep(10)  # 每分钟更新一次