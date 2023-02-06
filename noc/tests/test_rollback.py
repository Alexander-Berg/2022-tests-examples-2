import pytest
from datetime import datetime

from comocutor.result import Result
from comocutor.streamer import Trace
from comocutor_contrib.rollback import (CommitCursorExact, Commit, CommitCursorNext, CommiterJuniper, CommiterHuawei,
                                        CommitCursorDateExact, CommiterArista)


@pytest.mark.asyncio
async def test_huawei_state(huawei_commiter):
    c = huawei_commiter
    state = await c.state()
    assert state.last().internal_id == "1000000741"


@pytest.mark.asyncio
async def test_huawei_commit(huawei_commiter):
    c = huawei_commiter
    c._conn.add_response("system", "")
    c._conn.add_response("commit trial 60", "")
    c._conn.add_response("commit", "")
    await c.commit()


@pytest.mark.asyncio
async def test_huawei_current(huawei_commiter):
    c = huawei_commiter
    cf = await c.current()
    assert isinstance(cf, CommitCursorExact)
    assert cf._target.internal_id == "1000000741"


@pytest.mark.asyncio
async def test_huawei_rollback(huawei_commiter):
    c = huawei_commiter
    cf = CommitCursorExact(Commit("1000000741"))
    c._conn.add_response("rollback configuration to commit-id 1000000741", "")
    await c.rollback(cf)


@pytest.mark.asyncio
async def test_huawei_is_in_configure(conn):
    c = CommiterHuawei(conn)
    conn.add_response("", "")
    conn.set_prompt("<ce8850-test>")
    assert not await c._is_in_configure()
    conn.set_prompt("[ce8850-test]")
    assert await c._is_in_configure()


@pytest.mark.asyncio
async def test_arista_state(arista_commiter):
    c = arista_commiter
    state = await c.state()
    assert state.last().internal_id == "ckp-20200826-3"


@pytest.mark.asyncio
async def test_arista_state_empty(arista_commiter_empty):
    c = arista_commiter_empty
    state = await c.state()
    assert state.last().internal_id == ""


@pytest.mark.asyncio
async def test_arista_commit(arista_commiter):
    c = arista_commiter
    c._conn.add_response("commit timer 0:0:5", "")
    c._conn.add_response("configure session sess-1752--1065862336-5 commit", "")
    await c.commit()


@pytest.mark.asyncio
async def test_arista_current(arista_commiter):
    c = arista_commiter
    cf = await c.current()
    assert isinstance(cf, CommitCursorNext)
    assert cf._target.internal_id == "ckp-20200826-3"


@pytest.mark.asyncio
async def test_arista_current_empty(arista_commiter_empty):
    c = arista_commiter_empty
    cf = await c.current()
    assert isinstance(cf, CommitCursorNext)
    assert cf._target.internal_id == ""


@pytest.mark.asyncio
async def test_arista_rollback(arista_commiter):
    c = arista_commiter
    cf = CommitCursorNext(Commit("ckp-20200826-2"))
    c._conn.add_response("configure checkpoint restore ckp-20200826-3", "")
    await c.rollback(cf)


@pytest.mark.asyncio
async def test_arista_is_in_configure(arista_commiter):
    c = arista_commiter
    assert not await c._is_in_configure()
    c._conn.set_prompt("vla-1x3(s1)(config-s-sess-1)#")
    assert await c._is_in_configure()


@pytest.mark.asyncio
async def test_jun_state(jun_commiter):
    c = jun_commiter
    state = await c.state()
    last = state.last()
    assert last.internal_id == "0"
    assert last.date == datetime(year=2020, month=3, day=31, hour=15, minute=41, second=21)


@pytest.mark.asyncio
async def test_jun_is_in_configure(conn):
    c = CommiterJuniper(conn)
    conn.add_response("", "")
    conn.set_prompt("{master:0}[edit]\nazryve-nocauth@qfx5210-64c-test1>")
    assert not await c._is_in_configure()
    conn.set_prompt("{master:0}[edit]\nazryve-nocauth@qfx5210-64c-test1#")
    assert await c._is_in_configure()


@pytest.mark.asyncio
async def test_jun_commit(jun_commiter):
    c = jun_commiter
    c._conn.add_response("configure exclusive", "")
    c._conn.add_response("commit confirmed 1", "")
    c._conn.add_response("commit", "")
    await c.commit()


@pytest.mark.asyncio
async def test_jun_current(jun_commiter):
    c = jun_commiter
    cf = await c.current()
    assert isinstance(cf, CommitCursorDateExact)
    assert cf._target.internal_id == "0"
    assert cf._target.date == datetime(year=2020, month=3, day=31, hour=15, minute=41, second=21)


@pytest.mark.asyncio
async def test_jun_rollback(jun_commiter):
    c = jun_commiter
    target = Commit(internal_id="", date=datetime(year=2020, month=3, day=30, hour=12, minute=58, second=10))
    cf = CommitCursorDateExact(target)
    c._conn.add_response("configure exclusive", "")
    c._conn.add_response("rollback 2", "")
    c._conn.add_response("commit", "")
    await c.rollback(cf)


@pytest.fixture
def conn():
    return MockConnection()


@pytest.fixture
def huawei_commiter(conn):
    conn.set_prompt("<mock-huawei>")
    conn.add_response("display configuration commit list",
                      """
                  -----------------------------------------------------------------------------------------------------------------------------------
                  No.  CommitId     Label                                                            User            TimeStamp
                  -----------------------------------------------------------------------------------------------------------------------------------
                  1    1000000741   -                                                                azryve-nocauth  2020-08-26 11:34:42+03:00
                  2    1000000740   -                                                                azryve-nocauth  2020-08-26 11:34:41+03:00
                  3    1000000739   -                                                                azryve-nocauth  2020-08-26 11:34:40+03:00
                      """)
    conn.add_response("", "")
    return CommiterHuawei(conn)


@pytest.fixture
def arista_commiter(conn):
    c = CommiterArista(conn)
    conn.add_response("show configuration checkpoints",
                      """
                      Maximum number of checkpoints: 20
                      Filename               Date                      User
                      --------------- ------------------------- --------------
                      ckp-20200826-2     2020-08-26 09:37:01    azryve-nocauth
                      ckp-20200826-3     2020-08-26 09:37:34    azryve-nocauth
                      """)
    conn.add_response("show configuration sessions",
                      """
                      Maximum number of completed sessions: 5
                      Maximum number of pending sessions: 20

                      Name                       State         User              Terminal
                      ----------------------- ------------- -------------------- --------
                      * sess-1752--1065862336-5    pending       azryve-nocauth    vty5
                      """)
    conn.add_response("", "")
    conn.set_prompt("vla-1x3(s1)#")
    return c


@pytest.fixture
def arista_commiter_empty(conn):
    c = CommiterArista(conn)
    conn.add_response("show configuration checkpoints",
                      """
                      Maximum number of checkpoints: 20
                      Filename    Date    User
                      -------- ---------- ----

                      """)
    conn.add_response("show configuration sessions",
                      """
                      Maximum number of completed sessions: 5
                      Maximum number of pending sessions: 20

                      Name                       State         User              Terminal
                      ----------------------- ------------- -------------------- --------
                      * sess-1752--1065862336-5    pending       azryve-nocauth    vty5
                      """)
    conn.add_response("", "")
    conn.set_prompt("vla-1x3(s1)#")
    return c


@pytest.fixture
def jun_commiter(conn):
    c = CommiterJuniper(conn)
    out = """
    0   2020-03-31 15:41:21 MSK by glazgoo-nocauth via cli
    1   2020-03-31 15:38:01 MSK by glazgoo-nocauth via cli
    2   2020-03-30 12:58:10 MSK by glazgoo-nocauth via cli
    3   2020-03-27 13:27:13 MSK by root via other
    """
    conn.add_response("show system commit", out)
    conn.add_response("run show system commit", out)
    conn.add_response("", "")
    return c


class MockConnection:
    def __init__(self):
        self._responses = {}
        self._prompt = ""

    def add_response(self, cmd, resp):
        self._responses[cmd] = resp

    def set_prompt(self, prompt):
        self._prompt = prompt

    async def cmd(self, cmd, questions=None, timeout=None):
        if cmd not in self._responses:
            raise RuntimeError("Unknown cmd: %s" % cmd)
        out = self._responses[cmd]
        log = Trace()
        log.add("write", cmd.encode())
        log.add("read", " ".join([out, self._prompt]).encode())
        res = Result(
            cmd=cmd,
            out=out,
            err=None,
            mixed=None,
            exceptions=None,
            log=log,
            duration=0,
            ts=0
        )
        return res
