import abc

import six
import gevent

from sandbox.common.joint import server
from sandbox.common.joint import errors


class ServerSideException(errors.ServerError):
    pass


@six.add_metaclass(abc.ABCMeta)
class LocalServer(server.RPC):
    class LocalServerSideException(BaseException):
        pass

    def __init__(self, ctx):
        super(LocalServer, self).__init__(ctx)

        self.server = server.Server(ctx)
        # Register server connection handlers
        self.server.register_connection_handler(self.get_connection_handler())

    def start(self):
        super(LocalServer, self).start()
        self.server.start()
        return self

    def stop(self):
        self.server.stop()
        self.server.join()
        super(LocalServer, self).stop()
        super(LocalServer, self).join()
        return self

    def on_stalled_jobs(self, stalled):
        self.ctx.stalled = stalled

    @abc.abstractmethod
    def hang(self, timeout, terminate_timeout):
        try:
            gevent.sleep(timeout)
        except gevent.GreenletExit:
            gevent.sleep(terminate_timeout)

    @abc.abstractmethod
    def ping(self, magic):
        return magic

    @abc.abstractmethod
    def exception(self, serializable=True):
        raise (ServerSideException if serializable else self.LocalServerSideException)("Something wrong!", 42)

    @abc.abstractmethod
    def range(self, job, a, b):
        for i in range(a, b):
            gevent.sleep(0.01)
            job.state(i)
        return a + b

    @abc.abstractmethod
    def empty_gen(self):
        if False:
            yield

    @abc.abstractmethod
    def __theSameAsRangeMethodButWithYieldingAndWithoutSleeping(self, a, b):
        pass

    @abc.abstractmethod
    def duplex_gen(self, a, b):
        pass

    @abc.abstractmethod
    def duplex_gen2(self, a, b):
        pass
