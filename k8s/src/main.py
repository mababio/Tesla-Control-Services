import os
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
import json
from unit_converter.converter import converts
from logs import logger
import teslapy
import notification

app = FastAPI()
TESLA_USERNAME = os.environ.get("TESLA_USERNAME")

app.add_middleware(
    CORSMiddleware,
    # allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/healthchecker")
def root():
    return {"message": "Welcome to FastAPI with MongoDB"}


@app.get('/set_lock_state/{state}')
def set_lock_state(state):
    with teslapy.Tesla(TESLA_USERNAME) as tesla:
        if str(state).lower() == 'unlock':
            run_this = "UNLOCK"
        else:
            run_this = "LOCK"
        vehicles = tesla.vehicle_list()
        timeout = 10
        try:
            vehicles[0].sync_wake_up()
            vehicles[0].command(run_this)
        except teslapy.VehicleError as e:
            notification.send_push_notification(f"Timeout of {timeout} second for car to wake was reached:{e}")
            raise teslapy.VehicleError
        js = json.dumps({'status': True})
        return Response(js)


@app.get('/set_temp/{temp}')
def set_temp(temp):
    if 60 <= int(temp) <= 80:
        with teslapy.Tesla(TESLA_USERNAME) as tesla:
            vehicles = tesla.vehicle_list()
            timeout = 10
            formatted_str = f"{int(temp)}°F"
            temp_in_c = converts(formatted_str, '°C')
            try:
                vehicles[0].sync_wake_up()
                professor = vehicles[0]
                tesla_data_climate = professor.api('VEHICLE_DATA')['response']['climate_state']
            except teslapy.VehicleError as e:
                notification.send_push_notification(f"Timeout of {timeout} second for car to wake was reached:{e}")
                raise teslapy.VehicleError
            if not tesla_data_climate['is_climate_on']:
                professor.command('CLIMATE_ON')
            professor.command('CHANGE_CLIMATE_TEMPERATURE_SETTING', driver_temp=temp_in_c,
                              passenger_temp=temp_in_c)
            return True
    else:
        logger.error(f"Function Control::::: Set Temp::: input invalid input:{temp}")
        notification.send_push_notification(f"temp input was outside the range. this was the temp provided:{temp}")
        js = json.dumps({'error': f'temp provided is outside'})
        return Response(js)


@app.get('/climate_off')
def climate_off():
    with teslapy.Tesla(TESLA_USERNAME) as tesla:
        vehicles = tesla.vehicle_list()
        timeout = 10
        try:
            vehicles[0].sync_wake_up()
            professor = vehicles[0]
            tesla_data_climate = professor.api('VEHICLE_DATA')['response']['climate_state']
        except teslapy.VehicleError as e:
            notification.send_push_notification(f"Timeout of {timeout} second for car to wake was reached:{e}")
            raise teslapy.VehicleError

        if tesla_data_climate['is_climate_on'] and not tesla_data_climate['climate_keeper_mode'] == 'dog':
            professor.command('CLIMATE_OFF')
            return True
        else:
            notification.send_push_notification("Will not turn off Climate. It either is off or dog mode is on")
            return False
