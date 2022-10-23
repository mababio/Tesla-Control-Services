import math
import json
from config import settings
from logs import logger
import teslapy
from google.cloud import scheduler_v1
from google.protobuf import field_mask_pb2


def disable_job():
    client = scheduler_v1.CloudSchedulerClient()
    request = scheduler_v1.PauseJobRequest(name=settings['production']['job_scheduler']['job_name'],)
    return client.pause_job(request=request)


def set_lock_state(state):
    with teslapy.Tesla(settings['production']['teslapy']['email']) as tesla:
        run_this = ''
        if str(state).lower() == 'unlock':
            run_this = "UNLOCK"
        else:
            run_this = "LOCK"
            disable_job()
        vehicles = tesla.vehicle_list()
        vehicles[0].sync_wake_up()
        vehicles[0].command(run_this)
        return True


def set_temp(temp):
    if isinstance(temp[0], float):
        with teslapy.Tesla(settings['production']['teslapy']['email']) as tesla:
            vehicles = tesla.vehicle_list()
            vehicles[0].sync_wake_up()
            professor = vehicles[0]
            tesla_data_climate = professor.api('VEHICLE_DATA')['response']['climate_state']
            if not tesla_data_climate['is_climate_on']:
                professor.command('CLIMATE_ON')
            professor.command('CHANGE_CLIMATE_TEMPERATURE_SETTING', driver_temp=temp, passenger_temp=temp)
            return True
    else:
        logger.error("Function Control::::: Set Temp::: input invalid" + str(type(temp[0])))
        return False


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


def tesla_control(request):
    try:
        request_json = request.get_json()
        command = str(request_json['command'])
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
            return json.dumps({'executed': set_lock_state("unlock")})
        case _:
            logger.error("Tesla Control Cloud Function::::: faced error with http request")
            return json.dumps({'executed': False})

#
# if __name__ == "__main__":
#     set_temp([23.0])
