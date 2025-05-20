import paho.mqtt.client as mqtt
import json

# MQTT 配置
broker = "broker.emqx.io"
port = 1883
topic = "sc104/temperature"

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("订阅者已连接到 MQTT Broker")
        client.subscribe(topic)
    else:
        print(f"连接失败，返回码 {rc}")

def on_message(client, userdata, msg):
    print(f"接收到消息: {msg.topic} -> {msg.payload.decode()}")
    # {"temperature": 14, "humidity": 36} decode it to a dictionary
    json_data = json.loads(msg.payload.decode())
    print(f"Temperature: {json_data['temperature']}°C")

def subscribe_temperature():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(broker, port)
    client.loop_forever()

if __name__ == "__main__":
    subscribe_temperature()
