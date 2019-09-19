#!/usr/bin/python3


from gevent import monkey
monkey.patch_all() 
import time
import threading
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from gas_detection import GasDetection
from alarm import Alarm

#Instantiate our Flask and Flask-SocketIO. 
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
#app.debug = True
socketio = SocketIO(app)
print("Starting server...")

#Instantiate our GasDetection class. 
#In case you already done the calibration a few times,
#you can provide your own ro value e.g smoke_detector = GasDetection(ro=4500)
 
smoke_detector = GasDetection()
#print(smoke_detector.ro)
#Instantiate our own Alarm class 
alarm = Alarm()

#Variables used for configuration as a Python dict.
config = {
    'alarm_level_threshold': 0.04,
    'alarm_update_interval': 60,
    'sensor_reading_delay': 1
}

#Our main loop which will continously measure gas concentration in air. 
last_epoch = 0 
def background_sensor_reading():
    global last_epoch
    while True:
        #Delay between sensor readings. We use gevent's sleep instead of time.sleep()    
        time.sleep(config['sensor_reading_delay'])
        
        
        #Measure concentration of all gasses in ppm.                                                   
        ppm = smoke_detector.percentage()
        #Extract smoke only (you can measure other types if you wish).  
        smoke_value = ppm[smoke_detector.SMOKE_GAS]
        # Tell socketIO to push data to the client.
        socketio.emit('readings', {'value': smoke_value}) 
        print('Current smoke value: {}'.format(smoke_value))

        #Additionally, when the smoke_value is above certain threshold(set by the user)
        #We tell Python to activate buzzer and send emails.  
        if smoke_value > config['alarm_level_threshold']:
                print('!!!!!!!!!!!!!!!FIRE ALARM!!!!!!!!!!!')
                beep_thread = threading.Thread(target = alarm.beep)
                beep_thread.start()
                if (time.time() - last_epoch) > config['alarm_update_interval']:
                        last_epoch = time.time()
                        email_thread = threading.Thread(target=alarm.send_email)
                        email_thread.start()
                        
                        

#Render our html.                      
@app.route('/')
def index():
    return render_template('index.html', **config)

#Tell SocketIO to listen to the user input. 
@socketio.on('Changing values')
def value_change(message):
    #Change our config values depending on what message was sent to the server.
    config[message['key']] = float(message['data'])
    #Push the changes made back to the clients.
    socketio.emit('update value', {'key':message['key'] , 'value': message['data']})
    
      	
if __name__ == '__main__':
    try:

        socketio.start_background_task(background_sensor_reading)
        socketio.run(app, host='0.0.0.0', use_reloader=False)
    except KeyboardInterrupt:

        print("Closing server...")
        alarm.cleanup()
    
    