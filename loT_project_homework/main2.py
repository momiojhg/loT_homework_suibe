from machine import Pin, I2C
import ssd1306
import time
import network
import urequests
import json

# MQTT配置
MQTT_BROKER = "broker.emqx.io"
MQTT_PORT = 1883
MQTT_TOPIC_PUBLISH = "sc104/maotai"  # 发布主题
MQTT_TOPIC_SUBSCRIBE = "sc104/temperature"  # 订阅主题

# 设置 I2C
i2c = I2C(0, scl=Pin(4), sda=Pin(5))

# 等待一段时间，确保总线初始化
time.sleep(0.5)

# 扫描 I2C 设备
devices = i2c.scan()

if devices:
    print('I2C devices found:', devices)
else:
    print('No I2C devices found')
    raise SystemExit

oled_width = 128
oled_height = 64

# 使用正确的 I2C 地址
addr = devices[0]
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c, addr=addr)

# 初始化Wi-Fi接口
sta_if = network.WLAN(network.STA_IF)

# 激活Wi-Fi接口
if not sta_if.active():
    sta_if.active(True)
    time.sleep(1)  # 等待接口完全激活

# 连接到Wi-Fi
sta_if.connect("Momio5288", "12345678")

# 等待连接建立
max_wait = 20  # 最大等待时间（秒）
print("connecting...")
while max_wait > 0:
    if sta_if.isconnected():
        print("successful!")
        print("config:", sta_if.ifconfig())
        break
    max_wait -= 1
    print("time left:", max_wait)
    time.sleep(1)

if not sta_if.isconnected():
    print("Failed to connect to WiFi!")
    raise SystemExit

# MQTT回调函数
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("MQTT连接成功")
        client.subscribe(MQTT_TOPIC_SUBSCRIBE)
    else:
        print(f"MQTT连接失败，返回码: {rc}")

def on_message(client, userdata, msg):
    try:
        print(f"收到MQTT消息: {msg.topic} -> {msg.payload.decode()}")
        # 解析JSON数据
        json_data = json.loads(msg.payload.decode())
        # 在OLED上显示温度数据
        oled.fill(0)
        oled.text("MQTT Data:", 10, 10)
        oled.text(f"Topic: {msg.topic}", 10, 25)
        if 'temperature' in json_data:
            oled.text(f"Temp: {json_data['temperature']}°C", 10, 40)
        oled.show()
    except Exception as e:
        print(f"处理MQTT消息时出错: {e}")

# 初始化MQTT客户端
client = network.mqtt.MQTTClient(
    client_id="esp32_client",
    server=MQTT_BROKER,
    port=MQTT_PORT
)

# 设置回调函数
client.set_callback(on_message)
client.set_connect_cb(on_connect)

# 连接MQTT代理
try:
    client.connect()
    print("已连接到MQTT代理")
except Exception as e:
    print(f"MQTT连接错误: {e}")

# 主循环
while True:
    try:
        # 检查是否有MQTT消息
        client.check_msg()
        
        # 发送HTTP请求获取API数据
        response = urequests.get("https://lot-dashboard-1.onrender.com/api/price_data")
        data = response.json()
        response.close()  # 关闭连接释放资源

        # 解析数据
        current_price = data.get("current_price", 0.0)
        future_price = data.get("future_price", 0.0)
        
        # 准备MQTT发布数据
        publish_data = {
            "current_price": current_price,
            "future_price": future_price,
            "timestamp": time.time()
        }
        
        # 发布数据到MQTT
        client.publish(MQTT_TOPIC_PUBLISH, json.dumps(publish_data))
        print(f"已发布到MQTT: {publish_data}")

        # 将读数显示到OLED
        oled.fill(0)
        msg1 = f"CP: {current_price}"
        msg2 = f"FP: {future_price}"
        
        oled.text(msg1, 10, 10)
        oled.text(msg2, 10, 30)
        oled.text("MQTT: Connected", 10, 50)
        oled.show()
        
        time.sleep(10)  # 每10秒更新一次
    except Exception as e:
        print(f"主循环错误: {e}")
        time.sleep(5)  # 出错时等待更长时间