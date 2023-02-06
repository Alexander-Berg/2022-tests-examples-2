"""
This source file is Python3-only, but there's no any option in Pycharm to mark single file in a project
as Python3 or disable any inspections for the whole file.
"""
import typing

from sandbox.common.joint import tests
from sandbox.common.joint import server
from sandbox.common.joint import client


class LocalServer(tests.LocalServer):
    @server.RPC.simple
    def hang(self, timeout: int, terminate_timeout: int) -> None:
        return super().hang(timeout, terminate_timeout)

    @server.RPC.simple
    def ping(self, magic: int) -> int:
        return super().ping(magic)

    @server.RPC.simple
    def exception(self, serializable: bool = True) -> None:
        return super().exception(serializable=serializable)

    @server.RPC.full
    def range(self, job: client.RPCJob, a: int, b: int) -> int:
        return super().range(job, a, b)

    @server.RPC.generator
    def empty_gen(self) -> typing.Iterator[None]:
        yield from super().empty_gen()

    @server.RPC.generator(name="range2")
    def __theSameAsRangeMethodButWithYieldingAndWithoutSleeping(
        self, a: int, b: int
    ) -> typing.Generator[int, None, int]:
        for i in range(a, b):
            yield i
        return a + b

    @server.RPC.dupgenerator
    def duplex_gen(self, a: int, b: int) -> typing.Generator[int, bool, int]:
        for i in range(a, b):
            if (yield i) is True:
                break
        return a + b

    @server.RPC.dupgenerator
    def duplex_gen2(self, a: int, b: int) -> typing.Generator[int, bool, int]:
        result = 0
        for i in range(a, b):
            if (yield i) is True:
                result += i
        return result
