import struct
import threading

from execnet import gateway_base


class _ExitClass:
    pass


class Channel:
    _EMPTY_MARKER = object()

    def __init__(self, sock):
        self._sock = sock
        self._buffer = b''
        self._closed = False
        self._callback = None

    def send(self, data):
        pdata = gateway_base.dumps(data)
        pdata = struct.pack('!Q', len(pdata)) + pdata
        self._sock.sendall(pdata)

    def receive(self):
        assert self._callback is None
        return self._receive()

    def setcallback(self, callback, endmarker=_EMPTY_MARKER):
        assert self._callback is None
        self._callback = callback
        thread = threading.Thread(target=self._reader, args=(endmarker,))
        thread.start()

    def isclosed(self):
        return self._closed

    def close(self):
        self._closed = True
        try:
            self.send(_ExitClass())
        except Exception:
            pass
        self._sock.close()

    def _receive_size(self, size):
        buffer = [self._buffer]
        blen = len(self._buffer)
        while blen < size:
            bdata = self._sock.recv(32768)
            buffer.append(bdata)
            blen += len(bdata)
            if not bdata:
                raise ConnectionResetError
        buffer = b''.join(buffer)
        data = buffer[:size]
        self._buffer = buffer[size:]
        return data

    def _receive(self):
        try:
            size = struct.unpack('!Q', self._receive_size(8))[0]
            data = gateway_base.loads(self._receive_size(size))
            if isinstance(data, _ExitClass):
                try:
                    self._sock.close()
                except Exception:
                    pass
                raise ConnectionResetError
            return data
        except ConnectionResetError:
            self._closed = True
            raise

    def _reader(self, endmarker):
        callback = self._callback
        try:
            while True:
                data = self._receive()
                if data == endmarker:
                    self._callback = None
                    callback(data)
                    break
                callback(data)
        except Exception:
            pass
