from flask import Flask, render_template, Response, request, jsonify
import subprocess
import json

app = Flask(__name__)

# Load button configuration from JSON
with open('buttons.json') as f:
    button_config = json.load(f)

@app.route('/')
def index():
    return render_template('index.html', buttons=button_config)

def run_command(command, use_wsl):
    # Determine if the command should be run inside WSL
    if use_wsl:
        command = 'wsl ' + command

    process = subprocess.Popen(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )

    # Yield the output line by line
    for stdout_line in iter(process.stdout.readline, ""):
        yield stdout_line
    for stderr_line in iter(process.stderr.readline, ""):
        yield stderr_line
    process.stdout.close()
    process.stderr.close()
    return_code = process.wait()
    if return_code != 0:
        yield f"\nProcess failed with return code {return_code}\n"

@app.route('/run_command', methods=['POST'])
def run():
    data = request.json
    command = data.get('command')
    use_wsl = data.get('use_wsl', False)  # Default to False if not specified
    return Response(run_command(command, use_wsl), mimetype='text/plain')

if __name__ == '__main__':
    app.run(debug=True)
