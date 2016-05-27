import threading
import json
import string
import logging
import sys
from typing import Callable, Any

log = logging.getLogger(__name__)

class ProtocolHandler:

    # `read(N)`: callback to read up to N bytes from the input stream.
    # `write(buffer)`: callback to write bytes into the output stream.
    def __init__(self, read, write): # type: (ProtocolHandler, Callable[[int], bytes], Callable[[bytes], int]) -> None
        self.read = read
        self.write = write
        self.ibuffer = b''
        self.stopping = False

    # Starts a thread that reads bytes via `read`, parses them and passes
    # messages to the `handle_request` callback.
    # The thread will pump messages until either `shutdown()` is called,
    # or `read` returns zero, in which case `handle_request` will be invoked
    # one last time with the `None` argument.
    def start(self, handle_request): # type: (ProtocolHandler, Callable[[Any], None]) -> None
        self.handle_request = handle_request
        self.reader_thread = threading.Thread(None, self.pump_requests)
        self.reader_thread.start()

    def shutdown(self): # type: (ProtocolHandler) -> None
        self.stopping = True
        self.reader_thread.join()
        self.handle_request = None

    def recv_headers(self): # type: (ProtocolHandler) -> int
        while True:
            pos = self.ibuffer.find(b'\r\n\r\n')
            if pos != -1:
                headers = self.ibuffer[:pos]
                self.ibuffer = self.ibuffer[pos+4:]
                clen = None
                for header in headers.split(b'\r\n'):
                    if header.startswith(b'Content-Length:'):
                        clen = int(header[15:].strip())
                if clen != None:
                    return clen
                else:
                    log.error('No Content-Length header')

            data = self.read(1024)
            if len(data) == 0:
                raise StopIteration()
            self.ibuffer += data

    def recv_body(self, clen): # type: (ProtocolHandler, int) -> bytes
        while len(self.ibuffer) < clen:
            data = self.read(1024)
            self.ibuffer += data
        data = self.ibuffer[:clen]
        if len(data) == 0:
            raise StopIteration()
        self.ibuffer = self.ibuffer[clen:]
        return data

    def pump_requests(self): # type: (ProtocolHandler) -> None
        try:
            while not self.stopping:
                clen = self.recv_headers()
                raw_data = self.recv_body(clen)
                data = raw_data.decode('utf-8')
                log.debug('-> %s', data)
                message = json.loads(str(data))
                self.handle_request(message)
        except StopIteration: # Thrown when read() returns 0
            self.handle_request(None)
        except Exception as e:
            log.error(str(e))
            self.handle_request(None)

    def send_message(self, message): # type: (ProtocolHandler, Any) -> None
        data = json.dumps(message)
        log.debug('<- %s', data)
        raw_data = data.encode('utf-8')
        self.write(b'Content-Length: %d\r\n\r\n' % len(raw_data))
        self.write(raw_data)
