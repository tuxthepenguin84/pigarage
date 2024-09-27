# Modules
from datetime import datetime, timedelta
import os
import requests
import sys
import time

# Functions
def message_out(message):
  if matrix_enabled:
    dmessage.send_matrix_message(message, matrix_room_id, matrix_token)
  message = f'{datetime.now().strftime(time_format)} | {message}'
  print(message)

def main():
  # Variables
  delay_push_notif = datetime.now()
  delay_uptime_ping = datetime.now()
  previous_state = 'unknown'
  current_state = 'unknown'

  while True:
    previous_state = current_state
    current_state = requests.get(api_url + 'status', timeout=api_timeout).json()
    if current_state == 'open' and datetime.now() >= delay_push_notif:
      message_out('Door OPEN')
      if db_enabled:
        db_values = (
          datetime.now().strftime(date_only),
          datetime.now().strftime(time_only),
          current_state
        )
        ddatabase.insert_into_db(db_connection_info, db_table, db_columns, db_values)
      delay_push_notif = datetime.now() + timedelta(seconds=matrix_message_delay)
    elif current_state == 'closed' and previous_state == 'open':
      message_out('Door CLOSED')
      if db_enabled:
        db_values = (
          datetime.now().strftime(date_only),
          datetime.now().strftime(time_only),
          current_state
        )
        ddatabase.insert_into_db(db_connection_info, db_table, db_columns, db_values)
    elif current_state == 'unknown':
      message_out('Door ERROR - EXITING')
      if db_enabled:
        db_values = (
          datetime.now().strftime(date_only),
          datetime.now().strftime(time_only),
          current_state
        )
        ddatabase.insert_into_db(db_connection_info, db_table, db_columns, db_values)
      sys.exit(1)
    if datetime.now() >= delay_uptime_ping and uptime_enabled:
      dutils.ping_uptime(uptime_id)
      delay_uptime_ping = datetime.now() + timedelta(seconds=uptime_delay)
    time.sleep(api_status_refresh)

if __name__ == "__main__":
  # Variables
  date_only = "%m/%d/%Y"
  time_format = "%a %m/%d %H:%M:%S"
  time_only = "%H:%M:%S"

  # Import params.json Data
  params_file = os.path.join(script_dir, 'params.json')
  params_json = dutils.load_json_file(params_file)
  if params_json is None:
    print(f'Unable to import {params_file} data')
    sys.exit(1)

  # Import Database Connection Data
  if 'database' in params_json:
    db_enabled = True
    db_json = params_json['database']
    db_columns = db_json['columns']
    db_connection_info = db_json['connection']
    db_retries = db_json['retries']
    db_table = db_json['table']
  else:
    db_enabled = False
    db_columns = None
    db_connection_info = None
    db_retries = None
    db_table = None

  # Import Matrix Data
  if 'matrix' in params_json:
    matrix_enabled = True
    matrix_json = params_json['matrix']
    matrix_message_delay = matrix_json['messagedelay']
    matrix_room_id = matrix_json['roomid']
    matrix_token = matrix_json['token']
  else:
    matrix_enabled = False
    matrix_message_delay = None
    matrix_room_id = None
    matrix_token = None

  # Import Notifier Data
  notifier_json = params_json['notifier']
  api_status_refresh = notifier_json['statusrefresh']
  api_timeout = notifier_json['timeout']
  api_url = notifier_json['url']

  # Import Uptime Data
  if 'uptime' in params_json:
    uptime_enabled = True
    uptime_json = params_json['uptime']
    uptime_delay = uptime_json['delay']
    uptime_id = uptime_json['id']
  else:
    uptime_enabled = False
    uptime_delay = None
    uptime_id = None

  # Startup
  startup = {
    'APISTATUSREFRESH': api_status_refresh,
    'APITIMEOUT': api_timeout,
    'APIURL': api_url,
    'DB_COLUMNS': db_columns,
    'DB_CONN_INFO': db_connection_info,
    'DB_RETRIES': db_retries,
    'DB_TABLE': db_table,
    'MATRIXMESSAGEDELAY': matrix_message_delay,
    'MATRIXROOMID': matrix_room_id,
    'MATRIXTOKEN': matrix_token,
    'UPTIMEDELAY': uptime_delay,
    'UPTIMEID': uptime_id
  }

  print(f'{datetime.now().strftime(time_format)} | STARTING PIGARAGE NOTIFIER')
  for key, value in startup.items():
    print(f'{datetime.now().strftime(time_format)} | {key}: {value}')

  # Call Main Function
  main()
