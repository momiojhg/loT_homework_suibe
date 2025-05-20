from machine import Pin, I2C
import ssd1306
import time
import network
import urequests

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

oled_width = 128
oled_height = 64

# 使用正确的 I2C 地址，根据实际情况选择第一个
addr = devices[0]
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c, addr=addr)

#初始化Wi-Fi接口
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
    print("tims:", max_wait)
    time.sleep(1)

if not sta_if.isconnected():
    print("Failed!")


while True:
    # 发送HTTP请求获取API数据
    response = urequests.get("https://lot-dashboard-1.onrender.com/api/price_data")
    data = response.json()
    response.close()  # 关闭连接释放资源

    # 解析数据
    current_price = data.get("current_price", 0.0)
    future_price = data.get("future_price", 0.0)

    # 将读数显示到控制台
    oled.fill(0)
    msg1 = f"cur_price: {current_price} "
    msg2 = f"FP: {future_price}"
    
    print(msg1)
    oled.text(msg1, 10, 10)
    oled.text(msg2, 10, 30)
    oled.show()
    time.sleep(10)