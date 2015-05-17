#!/usr/bin/python

from flask import Flask, request, jsonify
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def main():
    if request.method == 'POST':
        json_data = request.get_json()
        return jsonify(json_data)
    return 'Hello World!'

if __name__ == '__main__':
    app.run(debug=True)
