
import RPi.GPIO as GPIO #pylint: disable=import-error
import time
import smtplib


class Alarm:

    def __init__(self, pin = 18):   
        self.pin = pin
        GPIO.setup(self.pin,GPIO.OUT)

    def beep(self):
        GPIO.output(self.pin, GPIO.HIGH)
        time.sleep(0.5) # make sure this number is lower than the sensor_reading_delay in app.py
        GPIO.output(self.pin, GPIO.LOW)
    def cleanup(self):
        GPIO.cleanup()

    def send_email(self):
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login("pimeros.feed@gmail.com", "jruaeyhljzctzmus")
        server.sendmail(
            "onixaze@gmail.com", 
            "onixaz@gmail.com", 
            "!!! FIRE ALARM !!!")
        server.quit()
        



