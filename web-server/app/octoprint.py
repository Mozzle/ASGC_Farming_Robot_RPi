# API for Octoprint

import requests

import dataclasses
import os

BASE_URL = 'http://localhost:5000/api'

# Need to get api key from OctoPrint
API_KEY = ''
if os.path.exists('API_KEY'):
    with open('API_KEY', 'r') as file:
        API_KEY = file.read().strip()

auth_header = {"X-Api-Key" : API_KEY}

@dataclasses.dataclass
class TemperatureInfo:
    name: str
    actual: float
    offset: int
    target: float | None

@dataclasses.dataclass
class SD:
    ready: bool

@dataclasses.dataclass
class State:
    text: str
    flags: dict

@dataclasses.dataclass
class PrinterInfo:
    temps: list[TemperatureInfo]
    sd: SD
    state: State



def get_current_state() -> PrinterInfo:
    url = f'{BASE_URL}/printer'

    r = requests.get(url, headers=auth_header)

    data = r.json()

    temps = [TemperatureInfo(k, v['actual'], v['offset'], v['target']) for k, v in data['temperature'].items()]
    sd = SD(data['sd']['ready'])
    state = State(data['state']['text'], data['state']['flags'])

    return PrinterInfo(temps, sd, state)


def send_gcode_command(command: str) -> dict:
    """
    Send a G-code command to the OctoPrint server
    
    Args:
        command (str): The G-code command to send (e.g., 'M112' for emergency stop)
    
    Returns:
        dict: Response from OctoPrint API
    """
    url = f'{BASE_URL}/printer/command'
    
    payload = {
        'command': command
    }
    
    try:
        response = requests.post(url, headers=auth_header, json=payload)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        return {
            'success': True,
            'message': f'Command "{command}" sent successfully',
            'status_code': response.status_code
        }
    except requests.exceptions.HTTPError as e:
        return {
            'success': False,
            'error': f'HTTP Error: {e.response.status_code}',
            'message': str(e)
        }
    except requests.exceptions.RequestException as e:
        return {
            'success': False,
            'error': 'Connection Error',
            'message': str(e)
        }


def emergency_stop() -> dict:
    """
    Send emergency stop command (M112) to the printer
    
    Returns:
        dict: Response from the emergency stop command
    """
    return send_gcode_command('M112')








