import requests
import time
from datetime import datetime
import paho.mqtt.client as mqtt
import json  # 新增：用于JSON数据转换

class GoldFuturesSpider:
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Referer": "https://quote.eastmoney.com/"
        }
        self.api_url = "https://push2.eastmoney.com/api/qt/stock/get"
        
        # MQTT 配置（直接定义，与示例格式统一）
        self.broker = "broker.emqx.io"
        self.port = 1883
        self.topic = "sc104/maotai"  # 主题可自定义
        self.client = mqtt.Client()  # 创建MQTT客户端
        
    def connect_mqtt(self):
        """连接到MQTT服务器"""
        self.client.connect(self.broker, self.port)
        print("发布者已连接到 MQTT Broker")
        
    def get_gold_futures_data(self):
        """获取并解析茅台数据"""
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
        """解析数据并格式化为JSON"""
        return {
            'name': raw_data.get('f57', 'N/A'),
            'latest_price': raw_data.get('f43', 'N/A') / 100 if raw_data.get('f43') else 'N/A',
            'change_amount': raw_data.get('f169', 'N/A') / 100 if raw_data.get('f169') else 'N/A',
            'change_percent': raw_data.get('f170', 'N/A'),
            'update_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    def publish_data(self):
        """发布数据到MQTT主题"""
        try:
            while True:
                data = self.get_gold_futures_data()
                if data:
                    # 将数据转换为JSON字符串
                    message = json.dumps(data, ensure_ascii=False)
                    self.client.publish(self.topic, message)
                    print(f"发布消息: {message}")
                time.sleep(10)  # 每10秒发布一次
        except KeyboardInterrupt:
            print("发布者已断开连接")
            self.client.disconnect()

if __name__ == "__main__":
    spider = GoldFuturesSpider()
    spider.connect_mqtt()  # 连接MQTT
    spider.publish_data()  # 开始发布数据