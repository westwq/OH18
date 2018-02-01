import os
import sys
import Adafruit_DHT
import time
import lcddriver
import RPi.GPIO as GPIO
import _thread
from subprocess import Popen
import max7219.led as led

device = led.matrix(cascaded = 4)
device.orientation(90)
display = lcddriver.lcd()

hum = 0
temp = 0
text = []
ends = False
state = 0
loop = 0
playback = False
startTime = 0
startLED = 0
elapsedW = 0

PIN_TRIG = 16
PIN_ECHO = 20
PIN_TEMP = 21
PIN_LED1 = 13
PIN_LED2 = 19
PIN_LED3 = 26
PIN_BUTTON = 24

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN_LED1, GPIO.OUT)
GPIO.setup(PIN_LED2, GPIO.OUT)
GPIO.setup(PIN_LED3, GPIO.OUT)
GPIO.setup(PIN_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def checkUltra(a):
    global ends,state,playback,startTime, startLED, elapsedW
    while True:
        time.sleep(0.1)
        if (time.time() - startTime < 60):
            continue
        #GPIO.setmode(GPIO.BCM)
        GPIO.setup(PIN_TRIG, GPIO.OUT)
        GPIO.setup(PIN_ECHO, GPIO.IN)

        GPIO.output(PIN_TRIG, False)
        time.sleep(1)

        GPIO.output(PIN_TRIG, True)
        time.sleep(0.00001)
        GPIO.output(PIN_TRIG, False)
        start = time.time()
        stop = 0
        while GPIO.input(PIN_ECHO) == 0:
            start = time.time()

        elapsedW = time.time()

        while True:
            if GPIO.input(PIN_ECHO) == 1:
                stop = time.time()
            else:
                break

            if(time.time() - elapsedW > 3600):
                break


        elapsed = stop - start
        distance = elapsed * 34300
        print(distance)
        #if(distance < 300):
            #if(time.time() - startLED >= 15):
                #_thread.start_new_thread(displayLED,(1,))
                #startLED = time.time()
        if(distance < 50):
            #text.append(["Welcome to ICT","Open House 2018"])

            if not playback and not state & 1:
                os.system('killall omxplayer.bin')
                omxc = Popen(['omxplayer', '-o', 'local','/home/pi/MoLDA.mp4'])
                playback = True
                startTime = time.time()

            elif playback and (time.time() - startTime >= 65):
                os.system('killall omxplayer.bin')
                omxc = Popen(['omxplayer', '-o', 'local','/home/pi/MoLDA.mp4'])
                playback = True
                startTime = time.time()

            state = state | 1

        if ends:
            print("Ending ultrasonic")
            break

def checkTemp(a):
    global hum, temp, ends
    while True:
        if hum != None and temp != None:
            hum, temp = Adafruit_DHT.read_retry(11,PIN_TEMP)
            #print("Temp: {0:0.1f}C Humidity: {1:0.1f}%".format(temp, hum))
            text.append(["Temp: {0:0.1f}C".format(temp), "Humidity: {0:0.1f}%".format(hum)])
        time.sleep(5)

        if ends:
            print("Ending temp")
            break

def displayLED(a):
    global ends
    device.show_message("Welcome to ICT Open House 2018")
        
def displayLCD(a):
    global ends
    while True:
        if len(text) > 0:
            display.lcd_clear()
            time.sleep(0.1)
            display.lcd_display_string(text[0][0],1)
            display.lcd_display_string(text[0][1],2)
            text.pop(0)
            time.sleep(3)

        if ends:
            print("Ending LCD")
            break

def LED(a):
    global ends, state, loop
    while True:
        if state == 3 and loop >= 2:
            #alarm
            if loop%2 == 0:
                GPIO.output(PIN_LED1,GPIO.HIGH)
                GPIO.output(PIN_LED2,GPIO.LOW)
            else:
                GPIO.output(PIN_LED1,GPIO.LOW)
                GPIO.output(PIN_LED2,GPIO.HIGH)

            if loop > 20:
                state = 0
                loop = 0
        else:
            
            if state & 1:
                GPIO.output(PIN_LED1,GPIO.HIGH)
            elif not state & 1:
                GPIO.output(PIN_LED1,GPIO.LOW)
            if state & 2:
                GPIO.output(PIN_LED2,GPIO.HIGH)
            elif not state & 2:
                GPIO.output(PIN_LED2,GPIO.LOW)
        
        if ends:
            print("Ending LED")
            break

        if state == 3:
            loop+=1
        time.sleep(0.3)
    
def pushButton(a):
    global ends, state, playback, startTime
    while True:
        if GPIO.input(PIN_BUTTON) == False:
            state = state | 2

            if not playback:
                os.system('killall omxplayer.bin')
                omxc = Popen(['omxplayer', '-o', 'local','/home/pi/TrAVEl.mp4'])
                playback = True
                startTime = time.time()
                time.sleep(1)

            elif playback and (time.time() - startTime >= 1):
                os.system('killall omxplayer.bin')
                playback = False
                #omxc = Popen(['omxplayer', '-o', 'local','/home/pi/TrAVEl.mp4'])
                #playback = True
                #startTime = time.time()
                
        if ends:
            print("Ending button")
            break

    
try:
    _thread.start_new_thread(checkTemp,(1,))
    _thread.start_new_thread(displayLCD,(1,))
    _thread.start_new_thread(checkUltra,(1,))
    _thread.start_new_thread(LED,(1,))
    _thread.start_new_thread(pushButton,(1,))
    #_thread.start_new_thread(displayLED,(1,))

    while True:
        displayLED(1)
        time.sleep(35)

except KeyboardInterrupt:
    print("Cleaning up!")
    display.lcd_clear()
    ends = True
