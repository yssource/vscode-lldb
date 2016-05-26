import threading
import logging
import lldb
from typing import Callable

log = logging.getLogger(__name__)

class AsyncListener:
    def __init__(self, listener, event_sink): # type: (AsyncListener, lldb.SBListener, Callable[[lldb.SBEvent], None]) -> None
        assert listener.IsValid()
        self.listener = listener
        self.event_sink = event_sink

        self.stopping = False
        self.read_thread = threading.Thread(None, self.pump_events)
        self.read_thread.start()

    def __del__(self): # type: (AsyncListener) -> None
        self.stopping = True
        self.read_thread.join()

    def pump_events(self): # type: (AsyncListener) -> None
        event = lldb.SBEvent()
        while not self.stopping:
            if self.listener.WaitForEvent(1, event):
                if log.isEnabledFor(logging.DEBUG):
                    descr = lldb.SBStream()
                    event.GetDescription(descr)
                    log.debug('### Debug event: %s %s', event.GetDataFlavor(), descr.GetData())
                self.event_sink(event)
                event = lldb.SBEvent()
