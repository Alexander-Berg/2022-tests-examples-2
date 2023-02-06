from sandbox.common.joint import tests
from sandbox.common.joint import server


class LocalServer(tests.LocalServer):
    @server.RPC.simple
    def hang(self, timeout, terminate_timeout):
        return super(LocalServer, self).hang(timeout, terminate_timeout)

    @server.RPC.simple
    def ping(self, magic):
        return super(LocalServer, self).ping(magic)

    @server.RPC.simple
    def exception(self, serializable=True):
        return super(LocalServer, self).exception(serializable=serializable)

    @server.RPC.full
    def range(self, job, a, b):
        return super(LocalServer, self).range(job, a, b)

    @server.RPC.generator
    def empty_gen(self):
        if False:
            yield

    @server.RPC.generator(name='range2')
    def __theSameAsRangeMethodButWithYieldingAndWithoutSleeping(self, a, b):
        for i in range(a, b):
            yield i
        raise StopIteration(a + b)

    @server.RPC.dupgenerator
    def duplex_gen(self, a, b):
        for i in xrange(a, b):
            if (yield i) is True:
                break
        raise StopIteration(a + b)

    @server.RPC.dupgenerator
    def duplex_gen2(self, a, b):
        result = 0
        for i in xrange(a, b):
            if (yield i) is True:
                result += i
        raise StopIteration(result)
