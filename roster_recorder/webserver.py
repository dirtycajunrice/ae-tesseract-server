from flask import Flask, request, jsonify
from flask_restful import Resource, Api, reqparse
from PIL import Image


def Server(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('token', required=True)
        args = parser.parse_args()
        if args['token'] != 'hwkBbKWXnO5bRfl9nR6ME8FOfLpU21bj':
            return jsonify({'msg': 'No.... U'})

        file = request.files['image']
        img = Image.open(file.stream)
        return jsonify({'msg': 'Great Success!'})

class Webserver():
    def __init__(self):
        self.app = Flask(__name__)
        self.api = Api(self.app)

    def Run(self):
        self.api.add_resource(Server, '/')
        self.app.run()

