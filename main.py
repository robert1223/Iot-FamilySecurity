#!/usr/bin/python3
import RPi.GPIO as GPIO
import subprocess


GPIO.setmode(GPIO.BOARD)

PIN = 11
GPIO.setup(PIN, GPIO.IN)
previousStatus = None
try:
	while True:
		input = GPIO.input(PIN)
		if input == GPIO.LOW and previousStatus == GPIO.HIGH:
           		# 開啟子程序，執行拍照及傳送圖片
			subprocess.Popen("python3 /home/pi/Python_project/HW_3/SendMessage.py", shell=True)
			#print("Here")
		previousStatus = input

except KeyboardInterrupt:
	print ("Error")
finally:
	GPIO.cleanup()
