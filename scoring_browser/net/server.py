import zmq
import threading
import time

from message import Message

DEFAULT_PORT = 9779

class Server(object):
    def __init__(self, port=DEFAULT_PORT):
        self.port = port
        self.socket = None
        self.messages = []
        self.thread = None
        self._running = False 
        self._stopped = False

    def _run(self):
        context = zmq.Context()
        self.socket = context.socket(zmq.REP)
        self.socket.bind("tcp://127.0.0.1:%s" % self.port)
        while not self._stopped:
            message_raw = self.socket.recv_json()
            message = Message.from_dict(message_raw)
            self.messages.append(message)
            self.socket.send("Ok")       

    def start(self, new_thread=True, daemon=True):
        '''Start listening.

        :param new_thread: Start the listening in a new thread.
        :param daemon: Whether to start a daemon thread.
        '''
        if self._running:
            raise Exception("Already running.")
        elif self._stopped: 
            raise Exception("Cannot restart an already stopped server.")
        if new_thread:
            self.thread = threading.Thread(target=self._run)
            self.thread.daemon = daemon
            self.thread.start()
        else:
            self._run()

    def stop(self):
        self.socket.unbind()
        if self.thread:
            self.thread.join()
            self.thread = None
        self._stopped = True
        self._running = False

    @property
    def running(self):
        return self._running

    @property
    def stopped(self):
        return self._stopped

    def has_message(self):
        return len(self.messages) > 0

    def pop_message(self):
        return self.messages.pop(0)

class Handler(object):
    '''


    The polling will automatically end when the server stops.
    '''
    def __init__(self, server, handler, polling=0.5):
        '''

        :param polling: How many seconds to wait between polls.
        :param handler: A callable object that accepts two parameters: str and numpy.ndarray
        '''
        self.server = server
        self.thread = None
        self.handler = handler
        self.polling = polling
        self._stopped = False

    def _run(self):
        while not self._stopped:
            if self.server.has_message():
                message = self.server.pop_message()
                self.handler(message.name, message.data)
            if self.server.stopped:
                self.stop()
            time.sleep(self.polling)

    def start(self):
        self.thread = threading.Thread(target=self._run)
        self.thread.daemon = True
        self.thread.start()

    def stop(self):
        self._stopped = False
        self.thread = None

if __name__ == "__main__":
    def log_message(name, data):
        print "Message: "
        print name
        print data.shape

    server = Server()
    handler = Handler(server, log_message)
    handler.start()
    server.start(False)  # Start in main thread
    