import zmq

import server
import message

class Client(object):
    def __init__(self, ip="127.0.0.1", port=server.DEFAULT_PORT):
        self.port = port
        self.ip = ip

    def send_message(self, message):
        context = zmq.Context()
        socket = context.socket(zmq.REQ) 
        socket.connect("tcp://%s:%d" % (self.ip, self.port))
        socket.send_json(message.as_dict())
        response = socket.recv()
        return response == "Ok"