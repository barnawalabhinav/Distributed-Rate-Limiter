from flask import Flask, request, jsonify
from flask_cors import CORS  # Import the CORS package

app = Flask(__name__)
CORS(app)  # Enable CORS for your app


@app.route('/update_constants', methods=['POST'])
def update_constants():
    data = request.get_json()

    n_servers = data.get('N_SERVERS')
    n_clients = data.get('N_CLIENTS')
    # Getting client rates from the received data
    client_rates = data.get('CLIENT_RATES')

    with open('constants.py', 'r+') as file:
        lines = file.readlines()
        file.seek(0)
        file.truncate()

        for line in lines:
            if line.startswith('N_SERVERS'):
                file.write(f"N_SERVERS: Final[int] = {n_servers}\n")
            elif line.startswith('N_CLIENTS'):
                file.write(f"N_CLIENTS: Final[int] = {n_clients}\n")
            elif 'CLIENT_RATES' in line:  # Check if line contains CLIENT_RATES
                # Updating client rates
                file.write(f"CLIENT_RATES: List[int] = {client_rates}\n")
            else:
                file.write(line)

    return jsonify(success=True)


if __name__ == '__main__':
    app.run(debug=True)
