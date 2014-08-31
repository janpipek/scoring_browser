import zmq

import server
import message

class Client(object):
    def __init__(self, ip="127.0.0.1", port=server.DEFAULT_PORT):
        self.port = port
        self.ip = ip

    def _send_message(self, a_message):
        context = zmq.Context()
        socket = context.socket(zmq.REQ) 
        socket.connect("tcp://%s:%d" % (self.ip, self.port))
        socket.send_json(a_message.as_dict())
        response = socket.recv()
        return response == "Ok"

    def send(self, data, name="data"):
        '''Send data to the server.

        :param data: a numpy array to send
        :param name: name of the data
        '''
        a_message = message.Message(name, data)
        return self._send_message(a_message)