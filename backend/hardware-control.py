#!/usr/bin/env python3
import time
import threading
import ioexpander as io
import paho.mqtt.client as mqtt

SERVO_PWM = 1
TOUCH_PIN = 14

# Settings to produce a 50Hz output from the 24MHz clock.
# 24,000,000 Hz / 8 = 3,000,000 Hz
# 3,000,000 Hz / 60,000 Period = 50 Hz
DIVIDER = 8
PERIOD = 60000

ioe = io.IOE(i2c_addr=0x18)

ioe.set_pwm_period(PERIOD)
ioe.set_pwm_control(divider=DIVIDER)

ioe.set_mode(SERVO_PWM, io.PWM)

ON_THRESHOLD = 5
LONG_PRESS = 20
on_count = 0
touch_state = False
last_touch_state = not touch_state

START_POS = 1000
RANGE = 3900

#MAX_RANGE = 4500

#MIN_POS = 3500
#MAX_POS = 7500

MIN_INPUT = 0.0
MAX_INPUT = 1.0

current_position = 0
lid_in_motion = False

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("hardware/output/lid/position")

def on_message(client, userdata, msg):
    global current_position
    print(msg.payload.decode())
    payload = msg.payload.decode().split(',')

    target_position = float(payload[0])

    step_size = float(payload[1])
    update_servo_position(target_position, step_size)

def update_servo_position(target_position, step_size):
    global current_position
    global lid_in_motion

    if (current_position == target_position):
        lid_in_motion = False
        return

    if (current_position > target_position):
      lid_in_motion = True
      while current_position > target_position:
          ioe.output(SERVO_PWM, START_POS + int(RANGE * current_position))
          if (current_position - step_size < target_position):
              current_position = target_position
          else:
              current_position -= step_size
          time.sleep(1.0 / 60)
      lid_in_motion = False
      return
    if (current_position < target_position):
      lid_in_motion = True
      while current_position < target_position:
          ioe.output(SERVO_PWM, START_POS + int(RANGE * current_position))
          if (current_position + step_size > target_position):
              current_position = target_position
          else:
              current_position += step_size
          time.sleep(1.0 / 60)
      lid_in_motion = False
      return

def listen_to_input():
    global touch_state
    global last_touch_state
    global on_count
    global TOUCH_PIN
    global ON_THRESHOLD
    global LONG_PRESS
    global lid_in_motion
    while True:
        time.sleep(0.1)
        if (lid_in_motion == False):
            input_value = ioe.input(TOUCH_PIN)
            if (input_value == 1):
                on_count += 1
                if (on_count >= ON_THRESHOLD):
                    if (last_touch_state == 0):
                        print("touch start")
                        last_touch_state = 1
            else:
                if (last_touch_state == 1):
                    print("touch end")
                    if (on_count >= ON_THRESHOLD):
                        if(on_count >= LONG_PRESS):
                            print("long press detected")
                            client.publish(topic="hardware/input/touch", payload="LONG_PRESS")
                        else:
                            print("tap detected")
                            client.publish(topic="hardware/input/touch", payload="TAP")
                    last_touch_state = 0
                    on_count = 0

client = mqtt.Client()
client.connect("localhost",1883,60)

client.on_connect = on_connect
client.on_message = on_message

thread = threading.Thread(target=listen_to_input, args=())
thread.start()

client.loop_forever()


