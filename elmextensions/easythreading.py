# pylint: disable=c-extension-no-member
''' easythreading a simple threaded function implementation.'''
import threading
import queue as Queue
from efl import ecore


class ThreadedFunction(object):
    ''' A simple Threaded function class.'''

    def __init__(self, doneCB=None):
        self._command_queue = Queue.Queue()
        self._reply_queue = Queue.Queue()
        self._done = doneCB

        # add a timer to check the data returned by the worker thread
        self._timer = ecore.Timer(0.1, self.check_reply)

        # start the working thread
        threading.Thread(target=self.thread_func).start()

    def run(self, action):
        '''Just do it'''
        self._command_queue.put(action)

    def shutdown(self):
        '''Cleanup and shutdown'''
        self._timer.delete()
        self._command_queue.put('QUIT')

    def check_reply(self):
        '''Check for reply'''
        if not self._reply_queue.empty():
            self._reply_queue.get()
            if callable(self._done):
                self._done()
        return True

    def thread_func(self):
        ''' A simple threaded function.'''
        while True:
            # wait here until an item in the queue is present
            func = self._command_queue.get()
            if callable(func):
                func()
            elif func == 'QUIT':
                break
            self._reply_queue.put('done')
