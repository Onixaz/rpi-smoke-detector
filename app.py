#!/usr/bin/python3

from gevent import monkey, sleep
monkey.patch_all()

import time
import threading
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from gas_detection import GasDetection
from alarm import Alarm

app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

print("Starting server...")
smoke_detector = GasDetection()
alarm = Alarm()

config = {
    'alarm_level_threshold': 0.04,
    'alarm_update_interval': 60,
    'sensor_reading_delay': 1
}


last_epoch = 0
   
def background_sensor_reading():
    global last_epoch
    while True:       
        time.sleep(config['sensor_reading_delay'])                                                   
        ppm = smoke_detector.percentage()
        smoke_value = ppm[smoke_detector.SMOKE_GAS] 
        socketio.emit('readings', {'data': 'This  is data', 'smoke_value': smoke_value})
        print('Current smoke value: {}'.format(smoke_value))      
        if smoke_value > config['alarm_level_threshold']:
                print('!!!!!!!!!!!!!!!FIRE ALARM!!!!!!!!!!!')  
                beep_thread = threading.Thread(target = alarm.beep, daemon=True)
                beep_thread.start()
                if (time.time() - last_epoch) > config['alarm_update_interval']:
                        last_epoch = time.time()
                        email_thread = threading.Thread(target=alarm.send_email, daemon=True)
                        email_thread.start()
                        print('EMAIL SENT')
                

        
@app.route('/')
def index():
        return render_template('index.html', **config)

@socketio.on('Changing values')
def value_change(message):
    config[message['key']] = float(message['data'])
    emit('update value', message, broadcast=True)
    
	
if __name__ == '__main__':
    try:
        socketio.start_background_task(background_sensor_reading)
        socketio.run(app, host='0.0.0.0', use_reloader=False)
    except KeyboardInterrupt:
        print("Closing server")
        alarm.cleanup()
    
    