import paho.mqtt.client as mqtt
import json
import time

# MQTT 配置
BROKER = "broker.emqx.io"
PORT = 1883
TOPIC = "sc104/maotai"
CLIENT_ID = "python-maotai-subscriber"

def on_connect(client, userdata, flags, rc):
    """连接成功回调"""
    if rc == 0:
        print(f"客户端 {CLIENT_ID} 已连接到 MQTT Broker")
        client.subscribe(TOPIC)
    else:
        print(f"连接失败，返回码: {rc}")

def on_message(client, userdata, msg):
    """消息接收回调"""
    try:
        print(f"接收到消息 [{msg.topic}]: {msg.payload.decode()}")
        
        # 解析JSON数据
        json_data = json.loads(msg.payload.decode())
        
        # 提取茅台价格信息
        current_price = json_data.get('current_price', 'N/A')
        future_price = json_data.get('future_price', 'N/A')
        timestamp = json_data.get('timestamp', time.time())
        
        # 格式化时间戳
        local_time = time.ctime(timestamp)
        
        # 显示价格信息
        print("\n===== 茅台价格信息 =====")
        print(f"更新时间: {local_time}")
        print(f"当前价格: {current_price}")
        print(f"未来价格: {future_price}")
        print("=======================\n")
        
    except json.JSONDecodeError as e:
        print(f"JSON解析错误: {e}")
    except Exception as e:
        print(f"处理消息时出错: {e}")

def on_disconnect(client, userdata, rc):
    """断开连接回调"""
    print(f"已断开与MQTT Broker的连接，返回码: {rc}")
    if rc != 0:
        print("意外断开，尝试重新连接...")
        # 可添加重连逻辑

def subscribe_maotai_price():
    """订阅茅台价格数据"""
    # 创建MQTT客户端实例
    client = mqtt.Client(client_id=CLIENT_ID)
    
    # 设置回调函数
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect
    
    # 连接到MQTT代理
    try:
        client.connect(BROKER, PORT)
        print(f"正在连接到 {BROKER}:{PORT}...")
        
        # 开始循环处理网络流量
        client.loop_forever()
        
    except Exception as e:
        print(f"连接MQTT代理时出错: {e}")
        return False

if __name__ == "__main__":
    print("茅台价格订阅器已启动")
    print(f"订阅主题: {TOPIC}")
    print(f"MQTT代理: {BROKER}:{PORT}")
    
    subscribe_maotai_price()