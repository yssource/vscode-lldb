from . import PY2
if PY2: import Queue as queue
else: import queue
from typing import Callable, Any, Sequence

class EventLoop:
    def __init__(self, qsize=10): # type: (EventLoop, int) -> None
        self.queue = queue.Queue(qsize) # type: queue.Queue

    def dispatch(self, target, args): # type: (EventLoop, Callable[Sequence[Any]], Sequence[Any]) -> None
        '''Dispatch to function with a tuple of arguments'''
        self.queue.put((target, args))

    def dispatch1(self, target, arg): # type: (EventLoop, Callable[Any], Any) -> None
        '''Dispatch to function with 1 argument'''
        self.queue.put((target, (arg,)))

    def run(self): # type: (EventLoop) -> None
        self.stopping = False
        while not self.stopping:
            target, args = self.queue.get()
            target(*args)

    def stop(self): # type: (EventLoop) -> None
        self.stopping = True