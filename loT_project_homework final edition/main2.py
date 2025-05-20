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
MQTT_TOPIC_SUBSCRIBE = "sc104/maotai"  # 订阅主题

# 设置 I2C
i2c = I2C(0, scl=Pin(4), sda=Pin(5), freq=400000)  # 增加I2C频率提高稳定性

# 等待一段时间，确保总线初始化
time.sleep(1)  # 延长等待时间确保初始化完成

# 扫描 I2C 设备
devices = i2c.scan()

if devices:
    print('I2C devices found:', devices)
else:
    print('No I2C devices found')
    raise SystemExit

oled_width = 128
oled_height = 64

# 使用正确的 I2C 地址（确保地址正确，常见OLED地址为0x3C或0x3D）
addr = devices[0]  # 建议手动确认地址，如0x3C
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c, addr=addr)

# 初始化Wi-Fi接口
sta_if = network.WLAN(network.STA_IF)

# 激活Wi-Fi接口
if not sta_if.active():
    sta_if.active(True)
    time.sleep(2)  # 延长激活等待时间

# 连接到Wi-Fi
sta_if.connect("Momio5288", "12345678")

# 等待连接建立
max_wait = 30  # 延长最大等待时间
print("connecting...")
while max_wait > 0:
    if sta_if.isconnected():
        print("successful!")
        print("config:", sta_if.ifconfig())
        break
    max_wait -= 1
    print(f"time left: {max_wait}s")
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
        json_data = json.loads(msg.payload.decode())
        
        # 清空屏幕并显示数据（确保价格为字符串类型）
        oled.fill(0)
        oled.text("Maotai Price:", 10, 10)
        oled.text(f"Topic: {msg.topic}", 10, 25)
        
        # 格式化价格显示（保留两位小数）
        cp = f"CP: {json_data.get('current_price', 0.0):.2f}"
        fp = f"FP: {json_data.get('future_price', 0.0):.2f}"
        
        oled.text(cp, 10, 40)
        oled.text(fp, 10, 50)
        oled.show()
        
    except Exception as e:
        print(f"处理MQTT消息错误: {e}")
        oled.fill(0)
        oled.text("Error!", 10, 40)
        oled.show()

# 初始化MQTT客户端（增加遗嘱消息确保异常断开提示）
client = network.mqtt.MQTTClient(
    client_id="esp32_maotai_client",
    server=MQTT_BROKER,
    port=MQTT_PORT,
    keepalive=60
)

# 设置回调函数
client.set_callback(on_message)

# 连接MQTT代理（增加异常处理）
try:
    client.connect()
    print("已连接到MQTT代理")
    client.connect()
    print("已连接到MQTT代理")
    client.set_last_will(MQTT_TOPIC_PUBLISH, b"Client disconnected")  # 设置遗嘱消息
except Exception as e:
    oled.text("MQTT Error", 10, 40)
    oled.show()
    time.sleep(5)
    raise SystemExit

# 主循环
while True:
    try:
        client.check_msg()  # 非阻塞式检查消息
        
        # 发送HTTP请求获取数据
        response = urequests.get("https://lot-dashboard-1.onrender.com/api/price_data")
        data = response.json()
        response.close()
        
        # 解析数据（确保数据存在）
        current_price = data.get("current_price", 0.0)
        future_price = data.get("future_price", 0.0)
        
        # 发布数据到MQTT（格式化数值为字符串避免传输问题）
        publish_data = {
            "current_price": float(current_price),
            "future_price": float(future_price),
            "timestamp": time.time()
        }
        client.publish(MQTT_TOPIC_PUBLISH, json.dumps(publish_data))
        print(f"已发布: {publish_data}")
        
        # 显示数据到OLED（确保价格为字符串类型）
        oled.fill(0)
        oled.text("API Data:", 10, 10)
        oled.text(f"CP: {current_price:.2f}", 10, 30)
        oled.text(f"FP: {future_price:.2f}", 10, 50)
        oled.text("MQTT: Online", 10, 60)  # 显示在最后一行
        oled.show()
        
        time.sleep(10)
        
    except urequests.exceptions.MissingSchema:
        print("API地址错误")
        oled.text("API Error", 10, 40)
        oled.show()
    except json.JSONDecodeError:
        print("数据解析失败")
        oled.text("JSON Error", 10, 40)
        oled.show()
    except Exception as e:
        print(f"主循环错误: {e}")
        oled.fill(0)
        oled.text("Main Error", 10, 40)
        oled.show()
        time.sleep(5)