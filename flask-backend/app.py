from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins="http://localhost:3000")

@app.route("/member", methods=['GET'])
def member():
    return jsonify({"Member": "Armando"}), 200


if __name__ == "__main__":
    app.run(Debug=True)