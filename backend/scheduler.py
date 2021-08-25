#!/usr/bin/env python3

import sys, getopt
import paho.mqtt.client as mqtt
import time
import datetime
import threading
class ScheduleItem:
    hour = None
    minute = None
    position = None
    def __init__(self, content):
        self.position = content.split(' ')[1]
        self.hour = content.split(' ')[0].split(':')[0]
        self.minute = content.split(' ')[0].split(':')[1]
    def checkTime():
        pass

def getScheduleFile(argv):
    input_file = None
    schedule_file = None
    schedule = None
    try:
        opts, args = getopt.getopt(argv,"h:i",["ifile="])
    except getopt.GetoptError:
        print ("scheduler.py -i <inputfile>")
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print ("scheduler.py -i <inputfile>")
            sys.exit()
        elif opt in ("-i", "--ifile"):
            input_file = arg
    if (input_file is not None):
        print(input_file)
        schedule_file = open(input_file, 'r')
        schedule = schedule_file.read().splitlines()
        schedule_file.close()
    else:
        print("no schedule file found")
        sys.exit()
    return schedule

def generate_schedule(schedule):
    schedule_items = []
    for item in schedule:
        schedule_items.append(ScheduleItem(item))
    return schedule_items

schedule = getScheduleFile(sys.argv[1:])

schedule_items = []

schedule_items = generate_schedule(schedule)

print(schedule_items)

def on_connect(client, userdata, flags, rc):
    print("Scheduler connected with result code "+str(rc))

def start_scheduler(schedule_items):
    while True:
        now = datetime.datetime.now()
        for schedule_item in schedule_items:
            if schedule_item.hour == str(now.hour) and schedule_item.minute == str(now.minute):
                print("Set position to "+schedule_item.position)
                client.publish(topic="schedule/lid/position", payload=schedule_item.position)
        time.sleep(60)

client = mqtt.Client()
client.connect("192.168.0.40",1883,60)
client.on_connect = on_connect

thread = threading.Thread(target=start_scheduler, args=([schedule_items]))
thread.start()

client.loop_forever()