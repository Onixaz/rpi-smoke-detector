
import RPi.GPIO as GPIO #pylint: disable=import-error
import time
import smtplib

#https://support.google.com/mail/answer/185833?hl=en how to create app specific password for Gmail
class Alarm:

    def __init__(
        self, pin = 18,
        sender_email="YOUREMAIL@gmail.com", 
        password="YOURREALORGENERATEDPASSWORD",
        receiver_email="YOUREMAIL@ANY.COM"):

        self.pin = pin
        self.sender_email = sender_email
        self.password = password
        self.receiver_email = receiver_email
        GPIO.setup(self.pin,GPIO.OUT)  
    
    def beep(self):
        GPIO.output(self.pin, GPIO.HIGH)
        # make sure time.sleep() is lower than the sensor_reading_delay in app.py
        time.sleep(0.5) 
        GPIO.output(self.pin, GPIO.LOW)
    
    def cleanup(self):
        GPIO.cleanup()

    #For this example we're using Python to connect to our Gmail account and send an email.
    def send_email(self):
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(self.sender_email, self.password)
        server.sendmail(
            self.sender_email, 
            self.receiver_email, 
            "!!! FIRE ALARM !!!")
        server.quit()
        print('EMAIL SENT')
        



