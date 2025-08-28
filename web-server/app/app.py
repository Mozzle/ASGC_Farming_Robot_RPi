import flask
from flask import request, jsonify

import camera
import octoprint

app = flask.Flask(__name__, template_folder='templates/')

@app.route('/')
def index():
    printer_info: octoprint.PrinterInfo = octoprint.get_current_state()
    camera.take_photo()

    return flask.render_template('index.j2')


@app.route('/emergency_stop', methods=['POST'])
def emergency_stop():
    """
    Endpoint to handle emergency stop requests from the frontend
    """
    try:
        # Get the command from the request (optional, defaults to M112)
        data = request.get_json() or {}
        command = data.get('command', 'M112')
        
        # Validate that it's an emergency stop command
        if command != 'M112':
            return jsonify({
                'success': False,
                'error': 'Invalid command',
                'message': 'Only M112 emergency stop command is allowed'
            }), 400
        
        # Send the emergency stop command via octoprint module
        result = octoprint.emergency_stop()
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': 'Emergency stop command sent successfully',
                'command': command
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Unknown error'),
                'message': result.get('message', 'Failed to send emergency stop')
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Server error',
            'message': str(e)
        }), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)

