import os
import subprocess
from flask import Flask, jsonify, render_template, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Get the user's current directory and append \user
cwd = os.getcwd()
cwd = os.path.join(cwd, "user")


# @app.route('/', methods = ['GET'])
@app.get('/')
def home():
    return render_template("index.html")


def run_command_in_cwd(command):
    try:
        # Always run the command in the user's cwd
        process = subprocess.Popen(
            command, shell=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        output, error = process.communicate()
        return output if output else error
    except Exception as e:
        return str(e)

@socketio.on('run_command')  # This is triggered from socket.emit running on index.html file
def handle_command(data):
    command = data.get('command')
    if command:
        output = run_command_in_cwd(command)
        socketio.emit('command_output', {'output': output})


# HTTP REST endpoint for commands via Postman
@app.route('/run_command', methods=['POST'])
def run_terminal_command():
    command = request.json.get('command')
    if command:
        socketio.emit('run_command', {'command': command})
        return jsonify({'status': 'Command sent to Socket.IO'}), 200
    
        # Below is just a POST endpoint which directly calls the run_command_in_cwd, not related to sockets,  
        # output = run_command_in_cwd(command)
        # return {'output': output}
    return {'error': 'No command provided'}, 400


# LIVE SOCKET
file_path = os.getcwd()
file_path = os.path.join(file_path, "Live\live.txt")

# Ensure the Live directory exists
os.makedirs(os.path.dirname(file_path), exist_ok=True)


# Function to append text to the live.txt file
def update_live_file(text):
    try:
        with open(file_path, 'w') as f:
            f.write(text)  # Append new text with a newline
    except Exception as e:
        print(f"Error writing to file: {str(e)}")

@socketio.on('text_input')
def handle_text_input(data):
    # Get the text input from the browser
    text = data.get('text')
    if text:
        # Write the text to the live.txt file
        update_live_file(text)
        # You can emit back the confirmation or updated file content
        emit('file_updated', {'message': 'Text written to file successfully.'})


if __name__ == '__main__':
    socketio.run(app, debug=True)
