# MQTT 패키지 설치 - paho-mqtt
# sudo pip install paho-mqtt
 # 동시에 publish(데이터 전송[출판]) / subscribe(데이터 수신[구독])

from threading import Thread, Timer
import time # time.sleep() 사용하기 위해 선언
import json
import datetime as dt

import paho.mqtt.client as mqtt
# DHT11 온습도센서
import Adafruit_DHT as dht
# GPIO
import RPi.GPIO as GPIO

# GPIO, DHT 설정
sensor = dht.DHT11
rcv_pin = 10
green = 22
servo_pin = 18

GPIO.setwarnings(False) # 오류메세지 제거
# green led init
GPIO.setmode(GPIO.BCM)
GPIO.setup(green, GPIO.OUT)
GPIO.output(green, GPIO.HIGH) # = True
# servo init
GPIO.setup(servo_pin, GPIO.OUT)
pwm = GPIO.PWM(servo_pin, 100) # 서브모터 속도
pwm.start(3) # 각도 0도 DutyCycle 3 ~ 20

# 내가 데이터를 보내는 객체
class publisher(Thread):
    def __init__(self):
        Thread.__init__(self) # 스레드 초기화
        self.host = '192.168.0.10' # 본인 PC ip주소
        self.port = 1883 # 회사에서는 이 포트 그래도 안씁니다. 포트번호 알면 해킹위험
        self.clientId = 'IOT56'
        self.count = 0
        print('publisher 스레드 시작')
        self.client = mqtt.Client(client_id=self.clientId) # 설계대로

    def run(self):
        self.client.connect(self.host, self.port)
        #self.client.username_pw_set() # id/pwd로 로그인할때는 필요
        self.publish_data_auto()

    def publish_data_auto(self): # 파이썬에서는 선언할때 무조건 self 파라미터 선언
        humid, temp = dht.read_retry(sensor, rcv_pin)
        curr = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S') # 2023-06-14 10:39:24
        origin_data = { 'DEV_ID' : self.clientId, 
                        'CURR_DT' : curr,
                        'TYPE' : 'TEMPHUMID',
                        'STAT' : f'{temp}|{humid}' } # real data 
        pub_data = json.dumps(origin_data) # MQTT로 전송할 json데이터로 변환
        self.client.publish(topic='pknu/rpi/control/', payload=pub_data)
        print(f'Data published #{self.count}')
        self.count += 1
        Timer(2.0, self.publish_data_auto).start() # 2초마다 출판

# 다른곳 데이터를 받아오는 객체
class subscriber(Thread):
    def __init__(self): # 생성자
        Thread.__init__(self)
        self.host = '192.168.0.10' # Broker IP 
        self.port = 1883
        self.clientId = 'IOT56_SUB'
        self.topic = 'pknu/monitor/control/'
        print('subscriber 스레드 시작')
        self.client = mqtt.Client(client_id=self.clientId)
     
    def run(self): # Thread.start() 함수를 실행하면 실행되는 함수
        self.client.on_connect = self.onConnect # 접속이 연결 되면 성공시그널을 처리 
        self.client.on_message = self.onMessage # 접속후 메세지가 수신되면 처리 // 중요! 메세지가 넘어온지 안넘어온지 확인할 수 있음
        self.client.connect(self.host, self.port)
        self.client.subscribe(topic=self.topic) # 위에만든 self.topic으로 구독하겠다
        self.client.loop_forever()

    def onConnect(self, mqttc, obj, flags, rc): # onconnect 제일 중요도 떨어짐
        print(f'subscirber 연결됨 rc > {rc}')

    def onMessage(self, mqttc, obj, msg):
        rcv_msg = str(msg.payload.decode('utf-8'))
        # print(f'{msg.topic} / {rcv_msg}')
        data = json.loads(rcv_msg) # json data로 형변환
        stat = data['STAT']
        print(f'현재 STAT : {stat}')
        if (stat == 'OPEN'):
            GPIO.output(green, GPIO.LOW)
            pwm.ChangeDutyCycle(12) # 90도
        elif (stat == 'CLOSE'):
            GPIO.output(green, GPIO.HIGH)
            pwm.ChangeDutyCycle(3) # 0도

            
        time.sleep(1.0)

if __name__ == '__main__':
    thPub = publisher() # publisher 객체 생성
    thSub = subscriber() # subscirber 객체 생성
    thPub.start() # run() 자동 실행
    thSub.start()
