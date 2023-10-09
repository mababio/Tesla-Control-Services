import json
from config import settings
from logs import logger
import teslapy
from flask import Flask, request, Response
import os

app = Flask(__name__)


@app.route('/set_lock_state/<state>')
def set_lock_state(state):
    with teslapy.Tesla(settings['production']['teslapy']['email']) as tesla:
        run_this = ''
        if str(state).lower() == 'unlock':
            run_this = "UNLOCK"
        else:
            run_this = "LOCK"
        vehicles = tesla.vehicle_list()
        vehicles[0].sync_wake_up()
        vehicles[0].command(run_this)
        js = json.dumps({'status': True})
        return Response(js, status=200, mimetype='application/json')


@app.route('/set_temp')
def set_temp(temp):
    if isinstance(temp['temp'], float):
        with teslapy.Tesla(settings['production']['teslapy']['email']) as tesla:
            vehicles = tesla.vehicle_list()
            vehicles[0].sync_wake_up()
            professor = vehicles[0]
            tesla_data_climate = professor.api('VEHICLE_DATA')['response']['climate_state']
            if not tesla_data_climate['is_climate_on']:
                professor.command('CLIMATE_ON')
            professor.command('CHANGE_CLIMATE_TEMPERATURE_SETTING', driver_temp=temp['temp'],
                              passenger_temp=temp['temp'])
            return True
    else:
        logger.error("Function Control::::: Set Temp::: input invalid" + str(type(temp[0])))
        return False


@app.route('/climate_off')
def climate_off():
    with teslapy.Tesla(settings['production']['teslapy']['email']) as tesla:
        vehicles = tesla.vehicle_list()
        vehicles[0].sync_wake_up()
        professor = vehicles[0]
        tesla_data_climate = professor.api('VEHICLE_DATA')['response']['climate_state']
        if tesla_data_climate['is_climate_on'] and not tesla_data_climate['climate_keeper_mode'] == 'dog':
            professor.command('CLIMATE_OFF')
            return True
        else:
            return False


@app.route('/', methods=['GET','POST'])
def tesla_control():
    try:
        request_json = request.get_json()
        logger.info("tesla_control:::::: {}".format(str(request_json)))
        command = str(request_json['command'])
        if 'args' in request_json:
            args = dict(request_json['args'])
    except Exception as e:
        logger.error('Tesla Control Cloud Function::::: Issue with function inputs :::::' + str(e))
        raise

    match command:
        case "TURN_OFF_CLIMATE":
            return json.dumps({'executed': climate_off()})
        case "SET_TEMP":
            return json.dumps({'executed': set_temp(args)})
        case "LOCK_CAR":
            return json.dumps({'executed': set_lock_state("lock")})
        case "UNLOCK_CAR":
            return set_lock_state("unlock")
        case _:
            logger.error("Tesla Control Cloud Function::::: faced error with http request")
            return json.dumps({'executed': False})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8081)))
