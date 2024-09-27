# Modules
from datetime import datetime
from flask import Flask
from flask_cors import CORS
from flask_restful import Api, Resource
import os
import RPi.GPIO as gpio
import sys
import time

# Functions
def get_door_status():
  return gpio.input(gpio_door_sensor)

def message_out(message):
  if matrix_enabled:
    dmessage.send_matrix_message(message, matrix_room_id, matrix_token)
  message = f'{datetime.now().strftime(time_format)} | {message}'
  print(message)

def set_gpio_pins():
  gpio.setmode(gpio.BCM)
  gpio.setup(gpio_door_remote, gpio.OUT)
  gpio.setup(gpio_door_sensor, gpio.IN, pull_up_down=gpio.PUD_UP)

# Classes
class Activate(Resource):
  def get(self):
    #gpio.output(gpio_door_remote, True)   # High, reset
    gpio.output(gpio_door_remote, False)   # Low, reset
    #gpio.output(gpio_door_remote, False)  # Low, activate relay
    gpio.output(gpio_door_remote, True)    # High, activate relay
    time.sleep(activation_time)
    #gpio.output(gpio_door_remote, True)   # High, reset
    gpio.output(gpio_door_remote, False)   # Low, reset
    message = '[Remote ACTIVATED]'
    message_out(message)
    return message, 200

class Status(Resource):
  def get(self):
    door_status = get_door_status()
    if door_status:
      return 'open', 200
    else:
      return 'closed', 200

class Health(Resource):
  def get(self):
    return 'up', 200

def main():
  # GPIO
  set_gpio_pins()

  # Flask
  app = Flask(__name__)
  CORS(app)
  api = Api(app)
  api.add_resource(Activate, "/activate")
  api.add_resource(Status, "/status")
  api.add_resource(Health, "/health")
  app.run(host='0.0.0.0', port=5000)
  app.run(debug=True)
  #ssl_context='adhoc'

if __name__ == "__main__":
  # Variables
  time_format = "%a %m/%d %H:%M:%S"

  # Import params.json Data
  params_file = os.path.join(script_dir, 'params.json')
  params_json = dutils.load_json_file(params_file)
  if params_json is None:
    print(f'Unable to import {params_file} data')
    sys.exit(1)

  # Import API Data
  api_json = params_json['api']
  activation_time = api_json['activationtime']
  gpio_door_remote = api_json['gpiodoorremote']
  gpio_door_sensor = api_json['gpiodoorsensor']

  # Import Matrix Data
  if 'matrix' in params_json:
    matrix_enabled = True
    matrix_json = params_json['matrix']
    matrix_room_id = matrix_json['roomid']
    matrix_token = matrix_json['token']
  else:
    matrix_enabled = False
    matrix_room_id = None
    matrix_token = None

  # Startup
  startup = {
    'ACTIVATIONTIME': activation_time,
    'GPIODOORREMOTE': gpio_door_remote,
    'GPIODOORSENSOR': gpio_door_sensor,
    'MATRIXROOMID': matrix_room_id,
    'MATRIXTOKEN': matrix_token
  }

  print(f'{datetime.now().strftime(time_format)} | STARTING PIGARAGE API')
  for key, value in startup.items():
    print(f'{datetime.now().strftime(time_format)} | {key}: {value}')

  # Call Main Function
  main()
