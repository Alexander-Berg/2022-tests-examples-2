#!/usr/bin/python3
import unittest
import asyncio
import logging

from functools import partial, partialmethod
from typing import List, Union
from textwrap import dedent

from comocutor.credentials import Credentials
from comocutor.devices import IosDevice, VrpDevice, JnxDevice, BasicDevice, NetconfDevice
from comocutor.devices import match_errors, term_eval, ConnFabric
from comocutor.streamer import (Stream, SockStream, Equals, FEATURE_AUTOLOGIN, FEATURE_NO_COMMAND_PROMPT,
                                FEATURE_EXEC_COMMAND_BY_WRITE, FEATURE_DO_SIMULTANEOUS_COMMANDS)
from comocutor.devices import SPACE, AutoDevice, PCDevice, EkinopsDevice
from comocutor.command import Command, Container, Question
from comocutor.connection import Connector
from comocutor.exceptions import ExecException, ExpectTimeout, BadPrompt, UnexpectedClose, AuthError
from comocutor.test_utils import Server, Send, Expect, SendEcho, CloseConn, ExpectCloseConn, _test_exprs, do_async, OK_MSG
from comocutor.utils import Expr

from data import jnx, ios, bash, ekinops
from data import DeviceWrite, MOCK_COMMAND

USERNAME = "username"
PASSWORD = "pass"
NEXT_PAGE_KEY = SPACE
EMPTY = ""


class ANY_TEXT:
    pass


VRP_MOTD = (
    "Info: The max number of VTY users is 5, the number of current VTY users online is 1, and total number of terminal users online is 1.\r\n"
    "      The current login time is 2017-03-15 12:01:23.\r\n"
    "      The last login time is 2017-02-22 13:15:27 through Terminal.\r\n")

VRP_MOTD2 = ("Info: The max number of VTY users is 10, and the number\r\n"
             "      of current VTY users on line is 2.\r\n"
             "      The current login time is 2017-01-17 23:52:29-05:13.\r\n")

JNX_ERROR1 = "      ^\r\nunknown command.\r\n\r\nroot> "


class SockStreamWrapper(SockStream):
    def __init__(self, *args, need_auth=True, command_prompt=True, sim_commands=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.env = {}
        self.features.append(FEATURE_EXEC_COMMAND_BY_WRITE)
        if not need_auth:
            self.features.append(FEATURE_AUTOLOGIN)
        if not command_prompt:
            self.features.append(FEATURE_NO_COMMAND_PROMPT)
        if sim_commands:
            self.features.append(FEATURE_DO_SIMULTANEOUS_COMMANDS)

    def open_session_wrapper(self, *args, **kwargs):
        logging.debug("open_session_wrapper")
        return self

    def open_stream(self, *args, **kwargs):
        logging.debug("open_stream")
        return self

    def __await__(self, timeout=30):
        return self
        yield None


class TestDevice(unittest.TestCase):
    cmd_time_limit = 5

    def one_cmd_test(self, dialog, send_cmd, dev_cls, out, err="", exc_count=0, send_init_nl=False, write_nl="\n", need_auth=True,
                     command_prompt=True, sim_commands=False):
        self.server.server_q.put(dialog)
        fabric = [ConnFabric(stream=partial(SockStreamWrapper, self.server.host, self.server.port, need_auth=need_auth,
                                            command_prompt=command_prompt, sim_commands=sim_commands))]

        host = dev_cls(Credentials(login=USERNAME, password=PASSWORD), fabric, write_nl=write_nl,
                       send_init_nl=send_init_nl)

        async def test():
            nonlocal send_cmd
            logging.debug("call host.connect()")
            await host.connect()
            if send_cmd:
                if isinstance(send_cmd, Command):
                    send_cmd = Command(send_cmd.cmd, suppress_error=[Exception], questions=send_cmd.questions,
                                       time_limit=self.cmd_time_limit)
                else:
                    send_cmd = Command(send_cmd, suppress_error=[Exception], time_limit=self.cmd_time_limit)
                res = await host.cmd(send_cmd)
            else:
                res = None
            await host.close()
            return res

        result = self.do_async(test())

        if not send_cmd:
            self.assertEqual(None, result)
        else:
            logging.debug("result.err=%r", result.err)
            logging.debug("result.out=%r", result.out)
            logging.debug("result.exceptions=%r", result.exceptions)
            if err is not ANY_TEXT:
                self.assertEqual(result.err, err, "error parameter mismatch")
            if out is not ANY_TEXT:
                self.assertEqual(out, result.out)
            if exc_count is not False:
                self.assertEqual(len(result.exceptions), exc_count)

    def _auth_test(self, dialog, dev_cls, send_init_nl=False, write_nl="\n", expect_exception=None,
                   username=USERNAME, password=PASSWORD):
        self.server.server_q.put(dialog)
        fabric = [ConnFabric(stream=partial(SockStream, self.server.host, self.server.port))]
        host = dev_cls(Credentials(login=username, password=password), fabric, write_nl=write_nl,
                       send_init_nl=send_init_nl)

        async def test():
            await host.connect()
            await host.close()

        self.do_async(test(), expect_exception=expect_exception)

    def _post_login_test(self, dialog, dev_cls, send_init_nl=False, write_nl="\n", expect_exception=None):
        self.server.server_q.put(dialog)
        fabric = [ConnFabric(stream=partial(SockStreamWrapper, self.server.host, self.server.port, need_auth=False))]
        host = dev_cls(Credentials(login=USERNAME, password=PASSWORD), fabric, write_nl=write_nl,
                       send_init_nl=send_init_nl)

        async def test():
            await host.connect()
            await host.close()

        self.do_async(test(), expect_exception=expect_exception)

    def container_test(self, dialog, cmds, dev_cls, expected, send_init_nl=False, write_nl="\n"):
        self.server.server_q.put(dialog)
        fabric = [ConnFabric(stream=partial(SockStreamWrapper, self.server.host, self.server.port))]
        host = dev_cls(Credentials(login=USERNAME, password=PASSWORD), fabric, write_nl=write_nl, send_init_nl=send_init_nl)
        container = Container(host)
        for cmd in cmds:
            if not isinstance(cmd, Command):
                cmd = Command(cmd, suppress_error=[Exception])
            container.add_cmd(cmd)

        async def test():
            connector = await Connector(keepalive=False)
            await connector.run_container(container)
            logging.debug("container is done")
            await connector.stop()
            await asyncio.sleep(0.01)
            return container.results

        result = self.do_async(test())
        self.assertEqual(len(expected), len(result))
        for i in range(len(expected)):
            self.assertEqual(expected[i][0], result[i].out, "stdout mismatch")
            self.assertEqual(expected[i][1], result[i].err, "stderr mismatch")
            self.assertEqual(expected[i][2], len(result[i].exceptions), "exceptions count mismatch")

    def coro_test(self, dialog, coroutine_fn, dev_cls, send_init_nl=False, write_nl="\n"):
        self.server.server_q.put(dialog)
        fabric = [ConnFabric(stream=partial(SockStreamWrapper, self.server.host, self.server.port))]
        host = dev_cls(Credentials(login=USERNAME, password=PASSWORD), fabric, write_nl=write_nl, send_init_nl=send_init_nl)

        async def test(conn):
            await conn.connect()
            await coroutine_fn(conn)
            logging.debug("coroutine %s is done" % coroutine_fn)

        self.do_async(test(host))

    def setUp(self):
        logging.debug("setup %s", self)
        self.maxDiff = None
        self.read_timeout = 0.1
        self.loop = asyncio.get_event_loop()
        self.old_stream_expect = Stream.expect

        self.server = Server()
        self.server.start_server()
        Stream.expect = partialmethod(Stream.expect, overall_timeout=self.read_timeout * 5, read_timeout=self.read_timeout)

    def tearDown(self):
        self.server.close()
        Stream.expect = self.old_stream_expect

    def do_async(self, fn, expect_exception=None):
        try:
            res = do_async(fn)
        except Exception as e:
            logging.debug("got exception: %r", e)
            res = e
        if isinstance(res, Exception):
            if expect_exception and isinstance(res, expect_exception):
                pass
            else:
                self._check_server_answer()
                self.server.force_close("expected exception %s wasn't raised" % expect_exception)
                raise res
        self._check_server_answer()
        return res

    def _check_server_answer(self):
        ans = self.server.client_q.get(timeout=0.1)
        # ans = NO_MSG
        if ans != OK_MSG:
            self.fail("server answer: %s" % ans)


class TestIos(TestDevice):
    """
    При работе с серийным портом нужно посывать \n без \r.
    """
    auth_dialog = [
        Send('\n\r\n\r\n\r\n\r\n\r\n\rPress RETURN to get started.\n\r\n\r'),
        Expect('\n'),
        Send('\r\n\r\n'
             'IMPORTANT:  READ CAREFULLY\r\n'
             'Welcome to the Demo Version of Cisco IOS XRv (the "Software").\r\n'
             'The Software is subject to and governed by the terms and conditions\r\n'
             'of the End User License Agreement and the Supplemental End User\r\n'
             'License Agreement accompanying the product, made available at the\r\n'
             'time of your order, or posted on the Cisco website at\r\n'
             'www.cisco.com/go/terms (collectively, the "Agreement").\r\n'
             'As set forth more fully in the Agreement, use of the Software is\r\n'
             'strictly limited to internal use in a non-production environment\r\n'
             'solely for demonstration and evaluation purposes.  Downloading,\r\n'
             'installing, or using the Software constitutes acceptance of the\r\n'
             'Agreement, and you are binding yourself and the business entity\r\n'
             'that you represent to the Agreement.  If you do not agree to all\r\n'
             'of the terms of the Agreement, then Cisco is unwilling to license\r\n'
             'the Software to you and (a) you may not download, install or use the\r\n'
             'Software, and (b) you may return the Software as more fully set forth\r\n'
             'in the Agreement.\r\n\r\n\r\n'
             'Please login with any configured user/password, or cisco/cisco\r\n\r\n\r\n'
             'User Access Verification\r\n\r\n'
             'Username: '),
        Expect(USERNAME + '\n'),
        SendEcho(USERNAME + '\n'),
        Send('\r\nPassword: '),
        Expect(PASSWORD + '\n'),
    ]

    login_dialog = auth_dialog + [
        Send("\r\n\r\n\r\nRP/0/0/CPU0:ios#"),
        ExpectCloseConn,
        CloseConn,
    ]

    show_int_dialog = auth_dialog + [
        Send("\r\n\r\n\r\nRP/0/0/CPU0:ios#"),
        Expect("show int Null0\n"),
        SendEcho("show int Null0\n"),
        Send('\n\r'
             'Sun Nov 13 11:08:12.259 UTC\r\n'
             '\x1b[KNull0 is up, line protocol is up \r\n'
             '  Interface state transitions: 1\r\n'
             '  Hardware is Null interface\r\n'
             '  Internet address is Unknown\r\n'
             '  MTU 1500 bytes, BW 0 Kbit\r\n'
             '     reliability 255/255, txload Unknown, rxload Unknown\r\n'
             '  Encapsulation Null,  loopback not set,\r\n'
             '  Last link flapped 03:44:33\r\n'
             '  Last input never, output never\r\n'
             '  Last clearing of "show interface" counters never\r\n'
             '  5 minute input rate 0 bits/sec, 0 packets/sec\r\n'
             '  5 minute output rate 0 bits/sec, 0 packets/sec\r\n'
             '     0 packets input, 0 bytes, 0 total input drops\r\n'
             '     0 drops for unrecognized upper-level protocol\r\n'
             '     Received 0 broadcast packets, 0 multicast packets\r\n'
             '     0 packets output, 0 bytes, 0 total output drops\r\n'
             '     Output 0 broadcast packets, 0 multicast packets'
             '\r\n\r\n\r\n\r\x1b[K'
             'RP/0/0/CPU0:ios#'),
        ExpectCloseConn,
        CloseConn,
    ]

    show_int_dialog_with_pager = auth_dialog + [
        Send("\n\r\n\r\nRP/0/0/CPU0:ios#"),
        Expect("show int\n"),
        SendEcho("show int\n"),
        Send('\n\r'
             'Sun Nov 13 11:46:40.690 UTC\r\n\x1b[K'
             'Null0 is up, line protocol is up \r\n'
             '  Interface state transitions: 1\r\n'
             '  Hardware is Null interface\r\n'
             '  Internet address is Unknown\r\n'
             '  MTU 1500 bytes, BW 0 Kbit\r\n'
             '     reliability 255/255, txload Unknown, rxload Unknown\r\n'
             '  Encapsulation Null,  loopback not set,\r\n'
             '  Last link flapped 04:23:01\r\n'
             '  Last input never, output never\r\n'
             '  Last clearing of "show interface" counters never\r\n'
             '  5 minute input rate 0 bits/sec, 0 packets/sec\r\n'
             '  5 minute output rate 0 bits/sec, 0 packets/sec\r\n'
             '     0 packets input, 0 bytes, 0 total input drops\r\n'
             '     0 drops for unrecognized upper-level protocol\r\n'
             '     Received 0 broadcast packets, 0 multicast packets\r\n'
             '     0 packets output, 0 bytes, 0 total output drops\r\n'
             '     Output 0 broadcast packets, 0 multicast packets\r\n\r\n'
             'MgmtEth0/0/CPU0/0 is administratively down, line protocol is administratively down \r\n'
             '  Interface state transitions: 0\r\n'
             '  Hardware is Management Ethernet, address is 0800.2714.be34 (bia 0800.2714.be34)\r\n'
             '  Internet address is Unknown\r\n'
             '  MTU 1514 bytes, BW 1000000 Kbit (Max: 1000000 Kbit)\r\n'
             '\x1b[K --More-- '),
        Expect(" "),
        Send('\x08 \x08\x08 \x08\x08 \x08\x08 \x08\x08 \x08\x08 \x08\x08 \x08\x08 \x08\x08 \x08\x08 \x08\x1b[K'
             '     reliability 255/255, txload 0/255, rxload 0/255\r\n'
             '  Encapsulation ARPA,\r\n'
             '  Duplex unknown, 1000Mb/s, unknown, link type is autonegotiation\r\n'
             '  output flow control is off, input flow control is off\r\n'
             '  Carrier delay (up) is 10 msec\r\n'
             '  loopback not set,\r\n'
             '  Last input never, output never\r\n'
             '  Last clearing of "show interface" counters never\r\n'
             '  5 minute input rate 0 bits/sec, 0 packets/sec\r\n'
             '  5 minute output rate 0 bits/sec, 0 packets/sec\r\n'
             '     0 packets input, 0 bytes, 0 total input drops\r\n'
             '     0 drops for unrecognized upper-level protocol\r\n'
             '     Received 0 broadcast packets, 0 multicast packets\r\n'
             '              0 runts, 0 giants, 0 throttles, 0 parity\r\n'
             '     0 input errors, 0 CRC, 0 frame, 0 overrun, 0 ignored, 0 abort\r\n'
             '     0 packets output, 0 bytes, 0 total output drops\r\n'
             '     Output 0 broadcast packets, 0 multicast packets\r\n'
             '     0 output errors, 0 underruns, 0 applique, 0 resets\r\n'
             '     0 output buffer failures, 0 output buffers swapped out\r\n'
             '     0 carrier transitions\r\n'
             '\r\n\r\n\x1b[K'
             'RP/0/0/CPU0:ios#'),
        ExpectCloseConn,
        CloseConn,
    ]

    def test_nexus_5k_login(self):
        dialog = [
            Send("Cisco Nexus Operating System (NX-OS) Software\r\nbla bla bla\r\n\rhostname# "),
            ExpectCloseConn,
            CloseConn,
        ]
        self.one_cmd_test(dialog, "", IosDevice, ANY_TEXT, ANY_TEXT, False)

    def test_XRV_con_login(self):
        dialog = self.login_dialog
        self.one_cmd_test(dialog, "", IosDevice, ANY_TEXT, ANY_TEXT, False, send_init_nl=True)

    def test_XRV_con_cmd_show_int(self):
        dialog = self.show_int_dialog
        send_cmd = "show int Null0"

        self.one_cmd_test(dialog, send_cmd, IosDevice, ANY_TEXT, EMPTY, 0, send_init_nl=True)

    def test_XRV_con_cmd_pager(self):
        # из результата выполнения команды должны быть удалены куски пейджера и последовательности \x1b[K
        dialog = self.show_int_dialog_with_pager

        out = dedent("""
        Sun Nov 13 11:46:40.690 UTC
        Null0 is up, line protocol is up
          Interface state transitions: 1
          Hardware is Null interface
          Internet address is Unknown
          MTU 1500 bytes, BW 0 Kbit
             reliability 255/255, txload Unknown, rxload Unknown
          Encapsulation Null,  loopback not set,
          Last link flapped 04:23:01
          Last input never, output never
          Last clearing of "show interface" counters never
          5 minute input rate 0 bits/sec, 0 packets/sec
          5 minute output rate 0 bits/sec, 0 packets/sec
             0 packets input, 0 bytes, 0 total input drops
             0 drops for unrecognized upper-level protocol
             Received 0 broadcast packets, 0 multicast packets
             0 packets output, 0 bytes, 0 total output drops
             Output 0 broadcast packets, 0 multicast packets

        MgmtEth0/0/CPU0/0 is administratively down, line protocol is administratively down
          Interface state transitions: 0
          Hardware is Management Ethernet, address is 0800.2714.be34 (bia 0800.2714.be34)
          Internet address is Unknown
          MTU 1514 bytes, BW 1000000 Kbit (Max: 1000000 Kbit)
             reliability 255/255, txload 0/255, rxload 0/255
          Encapsulation ARPA,
          Duplex unknown, 1000Mb/s, unknown, link type is autonegotiation
          output flow control is off, input flow control is off
          Carrier delay (up) is 10 msec
          loopback not set,
          Last input never, output never
          Last clearing of "show interface" counters never
          5 minute input rate 0 bits/sec, 0 packets/sec
          5 minute output rate 0 bits/sec, 0 packets/sec
             0 packets input, 0 bytes, 0 total input drops
             0 drops for unrecognized upper-level protocol
             Received 0 broadcast packets, 0 multicast packets
                      0 runts, 0 giants, 0 throttles, 0 parity
             0 input errors, 0 CRC, 0 frame, 0 overrun, 0 ignored, 0 abort
             0 packets output, 0 bytes, 0 total output drops
             Output 0 broadcast packets, 0 multicast packets
             0 output errors, 0 underruns, 0 applique, 0 resets
             0 output buffer failures, 0 output buffers swapped out
             0 carrier transitions
        """).strip()

        send_cmd = "show int"

        self.one_cmd_test(dialog, send_cmd, IosDevice, out, EMPTY, 0, send_init_nl=True)

    def test_XRV_con_invalid_input(self):
        """
        проверка генерации ошибок и stderr из неправильной команды
        """
        dialog = [
            Send('\r\n\rRP/0/0/CPU0:ios#'),
            Expect("invalid input\n"),
            SendEcho("invalid input\n"),
            Send("\n\r                  ^\r\n% Invalid input detected at '^' marker.\r\n"),
            Send("RP/0/0/CPU0:ios#"),
            ExpectCloseConn,
            CloseConn,
        ]

        send_cmd = "invalid input"
        err = "                  ^\n% Invalid input detected at '^' marker."

        self.one_cmd_test(dialog, send_cmd, IosDevice, EMPTY, err, 1)

    def test_nexus_pager(self):
        dialog = [
            Send('\ntest# '),
            Expect('show run\n'),
            SendEcho('show run\n'),
            Send("\r\n\r\n!Command: show running-config\r\n\x1b[7m--More--\x1b[27m"),
            Expect(NEXT_PAGE_KEY),
            Send("\r!Command: show running-config2\r\n\x1b[7m--More--\x1b[27m"),
            Expect(NEXT_PAGE_KEY),
            Send("\r!Command: show running-config3"),
            Send('\r\n\r\n\r\n\rtest# '),
            ExpectCloseConn,
            CloseConn,
        ]

        send_cmd = "show run"
        out = "!Command: show running-config\n!Command: show running-config2\n!Command: show running-config3"

        self.one_cmd_test(dialog, send_cmd, IosDevice, out, EMPTY, 0)

    # TODO: этот тест не работает так как после промта добавлен часть команды до знака вопроса
    def _test_nexus_pager2(self):
        dialog = [
            Send('\ntest# '),
            Expect('show ?'),
            SendEcho('show ?'),
            Send("\r\n  aaa                 Show aaa information\r\n  access-lists\r\n-- More --"),
            Expect(NEXT_PAGE_KEY),
            Send('Xml agent\r\n\r\n\x1b[17D\x1b[J\rtest# show'),
            ExpectCloseConn,
            CloseConn,
        ]

        send_cmd = Command("show ?", nl=False)
        out = 'aaa                 Show aaa information\n  access-lists\nXml agent'

        self.one_cmd_test(dialog, send_cmd, IosDevice, out, EMPTY, 0)

    def test_nexus_perm_denied(self):
        dialog = [
            Send('\r\n\rtest(config)# '),
            Expect('root cmd\n'),
            SendEcho('root cmd\n'),
            Send("\r\r\n% Permission denied for the role\r\n\rtest(config)# "),
            ExpectCloseConn,
            CloseConn,
        ]

        send_cmd = "root cmd"
        err = "% Permission denied for the role"

        self.one_cmd_test(dialog, send_cmd, IosDevice, EMPTY, err, 1)

    def test_nexus_echo(self):
        dialog = [
            Send('\r\n\rtest# '),
            Expect('show lldp neighbors interface Eth5/6\n'),
            SendEcho('show lldp neighbors interface Eth5/6\r\r\n'),
            Send("data\r\n\rmyt-2d1# "),
            ExpectCloseConn,
            CloseConn,
        ]

        send_cmd = "show lldp neighbors interface Eth5/6"

        self.one_cmd_test(dialog, send_cmd, IosDevice, 'data', EMPTY, 0)

    def test_ASR_perm_denied(self):
        dialog = [
            Send('RP/0/RSP0/CPU0:test(config)#'),
            Expect('no snmp-server traps syslog\n'),
            SendEcho('no snmp-server traps syslog\r\n'),
            Send("\r% This command is not authorized\r\n"),
            Send("RP/0/RSP0/CPU0:m9-p1(config)#"),
            ExpectCloseConn,
            CloseConn,
        ]
        self.one_cmd_test(dialog,
                          "no snmp-server traps syslog",
                          IosDevice,
                          EMPTY,
                          "% This command is not authorized",
                          1)

    def test_ASR_commit_error(self):
        dialog = [
            Send('RP/0/RSP0/CPU0:test(config)#'),
            Expect('commit\n'),
            SendEcho('commit\r\n'),
            Send(
                ("\r% Failed to commit one or more configuration items during a pseudo-atomic operation. All changes "
                 "made have been reverted. Please issue 'show configuration failed' from this session to view "
                 "the errors\r\n")),
            Send("RP/0/RSP0/CPU0:m9-p1(config)#"),
            ExpectCloseConn,
            CloseConn,
        ]
        self.one_cmd_test(dialog,
                          "commit",
                          IosDevice,
                          EMPTY,
                          ("% Failed to commit one or more configuration items during a pseudo-atomic operation. All "
                           "changes made have been reverted. Please issue 'show configuration failed' from this "
                           "session to view the errors"),
                          1)

    # FIXME: нерабочий тест. так ведет себя ASR в случае команды превышающей длину терминала
    def _test_ASR_long_line(self):
        dialog = [
            Send('RP/0/RSP0/CPU0:test(config)#'),
            Expect('no snmp-server traps ospf state-change if-state-change\n'),
            SendEcho(
                ('no snmp-server traps ospf state-change if-state-ch\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08'
                 '\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08'
                 '\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08$ate-change if-state-cha                        '
                 '  \x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08'
                 '\x08\x08nge\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08'
                 '\x08\x08\x08\x08\x08no snmp-server traps ospf state-change if-state-c$\x08\x08\x08\x08\r\n\r')),
            Send("RP/0/RSP0/CPU0:m9-p1(config)#"),
            ExpectCloseConn,
            CloseConn,
        ]
        self.one_cmd_test(dialog,
                          "no snmp-server traps ospf state-change if-state-change",
                          IosDevice,
                          EMPTY,
                          "",
                          0)

    def test_nexus_invalid_command(self):
        dialog = [
            Send('\r\n\rtest# '),
            Expect('show ewrwq\n'),
            SendEcho('show ewrwq\n'),
            Send("\r\n                  ^\r\n% Invalid command at '^' marker.\r\n\rtest# "),
            ExpectCloseConn,
            CloseConn,
        ]

        send_cmd = "show ewrwq"
        err = "                  ^\n% Invalid command at '^' marker."

        self.one_cmd_test(dialog, send_cmd, IosDevice, EMPTY, err, 1)

    def test_nexus_invalid_command2(self):
        dialog = [
            Send('\r\n\rtest# '),
            Expect('show interface port-channel\n'),
            SendEcho('show interface port-channel\n'),
            Send(("\r\n                                       ^\r\nInvalid command (incomplete interface)"
                  " at '^' marker.\r\n\rtest# ")),
            ExpectCloseConn,
            CloseConn,
        ]

        send_cmd = "show interface port-channel"
        err = "                                       ^\nInvalid command (incomplete interface) at '^' marker."

        self.one_cmd_test(dialog, send_cmd, IosDevice, EMPTY, err, 1)

    def test_nexus_invalid_command3(self):
        dialog = [
            Send('\r\n\rtest# '),
            Expect('show int nonexists\n'),
            SendEcho('show int nonexists\n'),
            Send("\r\n                     ^\r\nInvalid interface format at '^' marker.\r\n\rtest# "),
            ExpectCloseConn,
            CloseConn,
        ]
        self.server.server_q.put(dialog)

        send_cmd = "show int nonexists"
        err = "                     ^\nInvalid interface format at '^' marker."

        self.one_cmd_test(dialog, send_cmd, IosDevice, EMPTY, err, 1)

    def test_asr_nl(self):
        # ASR'ы замечаны за подтасовской переносов строк
        dialog = [
            Send('\r\n\r\nRP/0/RSP0/CPU0:m9-p1#'),
            Expect('conf t\n'),
            SendEcho('conf t\r\n\r'),
            Send("Thu Apr 20 15:18:45.622 MSK\r\nRP/0/RSP0/CPU0:m9-p1(config)#"),
            Expect('no snmp-server traps snmp linkup\n'),
            SendEcho('no snmp-server traps snmp linkup\r\n\r'),
            Send('RP/0/RSP0/CPU0:m9-p1(config)#'),
            Expect('exit\n'),
            SendEcho('exit\r\n\r'),
            CloseConn,
            # ExpectCloseConn,
        ]
        self.server.server_q.put(dialog)

        exp = [
            ["Thu Apr 20 15:18:45.622 MSK", EMPTY, 0],
            [EMPTY, EMPTY, 0],
            [EMPTY, EMPTY, 1],  # UnexpectedClose
        ]

        self.container_test(dialog, ["conf t", "no snmp-server traps snmp linkup", Command("exit", suppress_error=UnexpectedClose)],
                            IosDevice, exp)

    def test_catalyst_perm_denied(self):
        dialog = [
            Send('\r\n\rtest# '),
            Expect('save\n'),
            SendEcho('save\n'),
            Send(
                'Translating "save"...domain server (10.0.0.1)\r\n% Unknown command or computer name, or unable to find computer address\r\ntest#'),
            ExpectCloseConn,
            CloseConn,
        ]

        send_cmd = "save"
        err = "% Unknown command or computer name, or unable to find computer address"
        out = 'Translating "save"...domain server (10.0.0.1)'
        self.one_cmd_test(dialog, send_cmd, IosDevice, out, err, 1)

    def test_aironet_bad_oid(self):
        dialog = [
            Send('\r\n\rtest(config)# '),
            Expect('snmp-server view default-ro ololo.* included\n'),
            SendEcho('snmp-server view default-ro ololo.* included\n'),
            Send('%Bad OID\r\ntest(config)#'),
            ExpectCloseConn,
            CloseConn,
        ]

        send_cmd = "snmp-server view default-ro ololo.* included"
        err = "%Bad OID"
        out = ""
        self.one_cmd_test(dialog, send_cmd, IosDevice, out, err, 1)


class TestVrp(TestDevice):
    def test_vrp_login(self):
        dialog = [
            Send('\r\nWarning: Telnet is not a secure protocol, and it is recommended to use Stelnet.\r\ntest\r\n'),
            Send('\r\nUsername:'),
            Expect(USERNAME + "\n"),
            SendEcho(USERNAME + "\n"),
            Send("Password:"),
            Expect(PASSWORD + "\n"),
            Send(VRP_MOTD + "<test>"),
            ExpectCloseConn,
            CloseConn,
        ]
        self.one_cmd_test(dialog,
                          "",
                          VrpDevice,
                          ANY_TEXT,
                          ANY_TEXT,
                          False,
                          write_nl="\n")

    def test_vrp_login2(self):
        dialog = [
            Send('\r\nWarning: Telnet is not a secure protocol, and it is recommended to use Stelnet.\r\ntest\r\n'),
            Send('\r\nUsername:'),
            Expect(USERNAME + "\n"),
            SendEcho(USERNAME + "\n"),
            Send("Password:"),
            Expect(PASSWORD + "\n"),
            Send('\r\nError: '),
            Send('Authentication fail'),
            Send('\r\n'),
            Send('\r\nUsername:'),
            # ExpectCloseConn,
            CloseConn,
        ]
        self._auth_test(dialog, dev_cls=VrpDevice, expect_exception=AuthError)

    def test_vrp_cmd(self):
        dialog = [
            Send("\r\n" + VRP_MOTD2 + "<test> "),
            Expect('disp int XGigabitEthernet0/0/47 | include current state\n'),
            SendEcho('disp int XGigabitEthernet0/0/47 | include current state\n'),
            Send("\nXGigabitEthernet0/0/47 current state : UP\r\nLine protocol current state : UP\r\n\r\n<test>"),
            ExpectCloseConn,
            CloseConn,
        ]
        self.one_cmd_test(dialog,
                          "disp int XGigabitEthernet0/0/47 | include current state",
                          VrpDevice,
                          "XGigabitEthernet0/0/47 current state : UP\nLine protocol current state : UP",
                          EMPTY,
                          0)

    def test_incomplete_command(self):
        dialog = [
            Send('\r\n<test>'),
            Expect('disp\n'),
            SendEcho('disp\n'),
            Send("\n                       ^\r\nError:Incomplete command found at '^' position.\r\n<test>"),
            ExpectCloseConn,
            CloseConn,
        ]
        self.one_cmd_test(dialog,
                          "disp",
                          VrpDevice,
                          EMPTY,
                          "Incomplete command",
                          1)

    def test_stderr1(self):
        dialog = [
            Send('\r\n<test>'),
            Expect('system-view\n'),
            SendEcho('system-view\r\n'),
            Send('\r\n[~test]'),
            Expect('stelnet server enable\n'),
            SendEcho('stelnet server enable\n'),
            Send("Info: The STelnet server is already started.\r\n[~test]"),
            ExpectCloseConn,
            CloseConn,
        ]
        exp = [
            [EMPTY, EMPTY, 0],
            [EMPTY, "Info: The STelnet server is already started.", 0],
        ]

        self.container_test(dialog, ["system-view", "stelnet server enable"], VrpDevice, exp, write_nl="\n")

    def test_prompt_configure(self):
        dialog = [
            Send('\r\n<test>'),
            Expect('system-view\n'),
            SendEcho('system-view\r\n'),
            Send('[test]'),
            Expect('quit\n'),
            SendEcho('quit\r\n'),
            Send("\r\n<test>"),
            ExpectCloseConn,
            CloseConn,
        ]
        exp = [
            [EMPTY, EMPTY, 0],
            [EMPTY, EMPTY, 0],
        ]
        self.container_test(dialog, ["system-view", "quit"], VrpDevice, exp)

    def test_prompt_uncommitted(self):
        # в случае получения промпта с незакомиченными измнениями должен быть получен BadPrompt
        dialog = [
            Send('\r\n[*test]'),
            # ExpectCloseConn,
            CloseConn,
        ]
        exp = [
            [EMPTY, EMPTY, 0],
            [EMPTY, EMPTY, 0],
        ]

        with self.assertRaises(BadPrompt):
            self.container_test(dialog, [""], VrpDevice, exp)

    def test_bad_command(self):
        dialog = [
            Send('\r\n<test>'),
            Expect('ololo\n'),
            SendEcho('ololo\n'),
            Send("\n                  ^\r\nError: Unrecognized command found at '^' position.\r\n<test>"),
            ExpectCloseConn,
            CloseConn,
        ]
        self.one_cmd_test(dialog,
                          "ololo",
                          VrpDevice,
                          EMPTY,
                          "Unrecognized command",
                          1)

    def test_perm_denied(self):
        dialog = [
            Send('\r\n<test>'),
            Expect('local-user monitor privilege level 10\n'),
            SendEcho('local-user monitor privilege level 10\n'),
            Send("\nError: Low-level users are not allowed to create, delete, or modify high-level users.\r\n[test-aaa]"),
            ExpectCloseConn,
            CloseConn,
        ]
        self.one_cmd_test(dialog,
                          "local-user monitor privilege level 10",
                          VrpDevice,
                          EMPTY,
                          "Low-level users are not allowed to create, delete, or modify high-level users.",
                          1)

    def test_question_yn(self):
        dialog = [
            Send('\r\n<test>'),
            Expect('save\n'),
            SendEcho('save\n'),
            Send("\nThe current configuration will be written to the device.\r\nAre you sure to continue?[Y/N]"),
            Expect('Y\n'),
            SendEcho('Y\n'),
            Send('\nNow saving the current configuration to the slot 0.\r\nSave the configuration successfully.\r\n<test>'),
            ExpectCloseConn,
            CloseConn,
        ]
        qh = Question(r".*Are you sure to continue\?\[Y/N\]", "Y")
        self.one_cmd_test(dialog,
                          Command("save", questions=qh),
                          VrpDevice,
                          'Now saving the current configuration to the slot 0.\nSave the configuration successfully.',
                          EMPTY,
                          0)

    def test_question_yn2(self):
        # отличается от test_question_yn тем что тут переносы не те что пишет модуль
        # например на Huawei 12800 так
        dialog = [
            Send('\r\n<test>'),
            Expect('save\n'),
            SendEcho('save\r\n'),
            Send("\nThe current configuration will be written to the device.\r\nAre you sure to continue?[Y/N]"),
            Expect('Y\n'),
            SendEcho('Y\r\n'),
            Send('\nNow saving the current configuration to the slot 0.\r\nSave the configuration successfully.\r\n<test>'),
            ExpectCloseConn,
            CloseConn,
        ]
        qh = Question(r".*Are you sure to continue\?\[Y/N\]", "Y")
        self.one_cmd_test(dialog,
                          Command("save", questions=qh),
                          VrpDevice,
                          'Now saving the current configuration to the slot 0.\nSave the configuration successfully.',
                          EMPTY,
                          0)

    def test_long_cmd(self):
        # huawei вставляет всякие esс-коды
        dialog = [
            Send('\r\n<test>'),
            Expect(
                'display curr | inc 01234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789\n'),
            SendEcho(
                'display curr | inc 0123456789012345678901234567890123456789012 \x1b[1D3456789012345678901234567890123456789012345678901234567890123456789\n'),
            Send("\n<test>"),
            ExpectCloseConn,
            CloseConn,
        ]
        self.one_cmd_test(dialog,
                          "display curr | inc 01234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789",
                          VrpDevice,
                          EMPTY,
                          EMPTY,
                          0)

    def test_long_cmd2(self):
        # huawei вставляет всякие esс-коды. пример с S5710-28C-EI
        dialog = [
            Send('\r\n<test>'),
            Expect('system-view\n'),
            SendEcho('system-view\r\n'),
            Send("Enter system view, return user view with return command.\r\n[test]"),
            Expect(
                "undo snmp-agent target-host trap address udp-domain 10.10.1.117 params securityname cipher %@%@t8p(B`T%+B&GCp$<g'{Sz!WY%@%@\n"),
            SendEcho(
                "undo snmp-agent target-host trap address udp-domain 10.10.1.117 params  \x1b[1Dsecurityname cipher %@%@t8p(B`T%+B&GCp$<g'{Sz!WY%@%@\r\n"),
            Send("Error: The specified target host does not exist.\r\n[test]"),
            ExpectCloseConn,
            CloseConn,
        ]
        exp = [
            ["Enter system view, return user view with return command.", EMPTY, 0],
            [EMPTY, "The specified target host does not exist.", 1],
        ]

        self.container_test(dialog, ["system-view",
                                     "undo snmp-agent target-host trap address udp-domain 10.10.1.117 params securityname cipher %@%@t8p(B`T%+B&GCp$<g'{Sz!WY%@%@"],
                            VrpDevice, exp)

    def test_partial_read(self):
        dialog = [
            Send('\r\n<test>'),
            Expect('disp int XGigabitEthernet0/0/47 | include current state\n'),
            Send('disp int XGigabitEthernet0/0/4', sleep=0.01),
            Send('7 | include current sta', sleep=0.01),
            Send('te\r\nXGigabitEthernet0/0/47', sleep=0.01),
            Send(" current state : UP\r\nLine protocol current state : UP\r\n\r\n<test>"),
            ExpectCloseConn,
            CloseConn,
        ]
        self.one_cmd_test(dialog,
                          "disp int XGigabitEthernet0/0/47 | include current state",
                          VrpDevice,
                          "XGigabitEthernet0/0/47 current state : UP\nLine protocol current state : UP",
                          EMPTY,
                          0)

    def test_prompt_like_text(self):
        # в выводе есть G<C9otOTKd>DV что похоже на prompt
        dialog = [
            Send('\r\n<test>'),
            Expect('display current-configuration | inc acl 1234\n'),
            SendEcho('display current-configuration | inc acl 1234\n'),
            Send(
                "\nsnmp-agent community read cipher %$%$0lWe#[*%5LR3U'H5$Lh'CX`a:wG<C9otOTKd>DVqq%O=X`dC#`vS'*K=RX%n3~=DS7S3`mCX%$%$ acl 1234"),
            Send("\r\n[test]"),
            ExpectCloseConn,
            CloseConn,
        ]
        self.one_cmd_test(dialog,
                          "display current-configuration | inc acl 1234",
                          VrpDevice,
                          "snmp-agent community read cipher %$%$0lWe#[*%5LR3U'H5$Lh'CX`a:wG<C9otOTKd>DVqq%O=X`dC#`vS'*K=RX%n3~=DS7S3`mCX%$%$ acl 1234",
                          EMPTY,
                          0)

    def test_pager(self):
        # screen-length 3
        dialog = [
            Send('\r\n<test>'),
            Expect('display current | inc XGigabitEthernet0/0/2\n'),
            SendEcho('display current | inc XGigabitEthernet0/0/2\n'),
            Send('interface XGigabitEthernet0/0/2\r\ninterface XGigabitEthernet0/0/20\r\ninterface'
                 ' XGigabitEthernet0/0/21\r\n  ---- More ----'),
            Expect(SPACE),
            Send(
                ('\x1b[42D                                          \x1b[42Dinterface XGigabitEthernet0/0/22'
                 '\r\ninterface XGigabitEthernet0/0/23\r\ninterface XGigabitEthernet0/0/24\r\n  ---- More ----')),
            Expect(SPACE),
            Send(
                ('\x1b[42D                                          \x1b[42Dinterface XGigabitEthernet0/0/25'
                 '\r\ninterface XGigabitEthernet0/0/26\r\ninterface XGigabitEthernet0/0/27\r\n  ---- More ----')),
            Expect(SPACE),
            Send('\x1b[42D                                          \x1b[42Dinterface XGigabitEthernet0/0/28'
                 '\r\ninterface XGigabitEthernet0/0/29\r\n'),
            Send("<test>"),
            ExpectCloseConn,
            CloseConn,
        ]
        out = dedent("""
            interface XGigabitEthernet0/0/2
            interface XGigabitEthernet0/0/20
            interface XGigabitEthernet0/0/21
            interface XGigabitEthernet0/0/22
            interface XGigabitEthernet0/0/23
            interface XGigabitEthernet0/0/24
            interface XGigabitEthernet0/0/25
            interface XGigabitEthernet0/0/26
            interface XGigabitEthernet0/0/27
            interface XGigabitEthernet0/0/28
            interface XGigabitEthernet0/0/29
        """).strip()
        self.one_cmd_test(dialog, "display current | inc XGigabitEthernet0/0/2", VrpDevice, out, EMPTY, 0)

    def test_login_denied(self):
        dialog = [
            Send('\r\n<test>'),
            Expect('system-view\n'),
            SendEcho('system-view\r\n'),
            Send("Error: No permission to run the command.\r\n<test>"),
            ExpectCloseConn,
            CloseConn,
        ]
        self.one_cmd_test(dialog,
                          "system-view",
                          VrpDevice,
                          EMPTY,
                          "No permission to run the command.",
                          1, write_nl="\n")

    def test_question1(self):
        # вопрос состоит из нескольких вопросов
        dialog = [
            Send('\r\n<test>'),
            Expect('system-view\n'),
            SendEcho('system-view\r\n'),
            Send("Enter system view, return user view with return command.\r\n[~test]"),
            Expect("rsa local-key-pair create\n"),
            SendEcho("rsa local-key-pair create\n"),
            Send(
                "The key name will be: test_Host\r\n% RSA keys defined for test_Host already exist.\r\nConfirm to replace them? Please select [Y/N]:"),
            Expect('Y\n'),
            SendEcho('Y\n'),
            Send(
                "The range of public key size is (512 ~ 2048).\r\nNOTE: Key pair generation will take a short while.\r\nInput the bits in the modulus [default = 2048]:"),
            Expect('2048\n'),
            SendEcho('2048\n'),
            Send('\r\n<test>'),
            ExpectCloseConn,
            CloseConn,
        ]
        qh = [
            Question(r".*Confirm to replace them\? Please select \[Y/N\]:", "Y"),
            Question(r".*Input the bits in the modulus \[default = 2048\]", "2048"),
        ]
        exp = [
            ["Enter system view, return user view with return command.", EMPTY, 0],
            [EMPTY, EMPTY, 0],
        ]
        cmd = Command("rsa local-key-pair create", questions=qh)
        self.container_test(dialog, ["system-view", cmd], VrpDevice, exp)

    def test_question2(self):
        # вопрос состоит из нескольких вопросов
        dialog = [
            Send('\r\n<test>'),
            Expect('system-view\n'),
            SendEcho('system-view\r\n'),
            Send("Enter system view, return user view with return command.\r\n[~test]"),
            Expect("undo dhcp enable\n"),
            SendEcho("undo dhcp enable\r\n"),
            Send("Warning: All DHCP functions will be disabled. Continue? [Y/N]:"),
            Expect('Y\n'),
            SendEcho('Y\n'),
            Send('\r\n[~test]'),
            ExpectCloseConn,
            CloseConn,
        ]

        qh = Question(r".*Continue\? \[Y/N\]:", "Y")
        exp = [
            ["Enter system view, return user view with return command.", EMPTY, 0],
            [EMPTY, EMPTY, 0],
        ]
        cmd = Command("undo dhcp enable", questions=qh)
        self.container_test(dialog, ["system-view", cmd], VrpDevice, exp)

    def test_echo_with_dots(self):
        # иногда хуавей может к эху подмешивать точки
        dialog = [
            Send('\r\n<test>'),
            Expect('patch run all\n'),
            SendEcho('patch run all'),
            SendEcho('...\r\n'),
            Send("Info: Succeeded in running the patch on the master board.\r\nInfo: Finished running the patch.\r\n<test>"),
            ExpectCloseConn,
            CloseConn,
        ]
        self.one_cmd_test(dialog,
                          "patch run all",
                          VrpDevice,
                          EMPTY,
                          "Info: Succeeded in running the patch on the master board.\nInfo: Finished running the patch.",
                          0)

    def test_ftp(self):
        # у команды несколько вопросов, в результате ее выполнения меняется prompt
        dialog = [
            Send('\r\n<vla1-x14>'),
            Expect('ftp 77.88.1.117\n'),
            SendEcho('ftp 77.88.1.117\r\n'),
            Send('Trying 77.88.1.117 ...\r\n'
                 'Press CTRL + K to abort\r\n'
                 'Connected to 77.88.1.117.\r\n'
                 '220 Welcome to NOC FTP service.\r\n'
                 'User(77.88.1.117:(none)):'),
            Expect('anonymous\n'),
            SendEcho('anonymous\r\n'),
            Send('331 Please specify the password.\r\n'
                 'Enter password:'),
            Expect('\n'),
            SendEcho('\r\n'),
            Send('230 Login successful.\r\n[ftp]'),
            Expect('quit\n'),
            SendEcho('quit\r\n'),
            Send('<vla1-x14>'),
            ExpectCloseConn,
            CloseConn,
        ]

        # FTP_VRP_PROMPT = Expr(ANY_NL_OR_START_EXPR + r"\[ftp\]$")
        FTP_CREDENTIALS = [
            Question(Expr(r"^User.*:$", M=1), "anonymous"),
            Question(Equals("Enter password:"), ""),
        ]

        exp = [
            (
                Command("ftp 77.88.1.117", questions=FTP_CREDENTIALS),
                # эти закоменчанные данные будут поглащены в questions. есть возможность указать store группы
                # но тогда надо аккуратно писать регулярки
                [  # 'Trying 77.88.1.117 ...\n'
                    # 'Press CTRL + K to abort\n'
                    # 'Connected to 77.88.1.117.\n'
                    # '220 Welcome to NOC FTP service.\n'
                    # 'User(77.88.1.117:(none)):anonymous\n'
                    # '331 Please specify the password.\n'
                    # 'Enter password:\n'
                    '230 Login successful.',
                    EMPTY, 0]
            ),
            (
                Command("quit"),
                [EMPTY, EMPTY, 0]
            ),
        ]
        self.container_test(dialog, [cmd for cmd, _ in exp], VrpDevice, [e for _, e in exp])

    def test_ftp_timeout(self):
        """
        проверяется прерывание залипшей команды и обработка другой в exception handler.
        Также проверяются следующие фичи:
            - cmd(echo="")
            - cmd(expect_error=)
            - корректность Result для последнего quit, когда свитч разорвал соединение
        """
        dialog = [
            Send('\r\n<vla1-x14>'),
            Expect('ftp 77.88.1.117\n'),
            SendEcho('ftp 77.88.1.117\r\n'),
            Send('Trying 77.88.1.117 ...\r\n'
                 'Press CTRL + K to abort\r\n'),
            Expect('\x0b'),
            Send('Error: Failed to connect to the remote host.\r\n'),
            Send('\r\n<vla1-x14>'),
            Expect('quit\n'),
            SendEcho('quit\r\n'),
            Send('Info: The max number of VTY users is 8, and the number of current VTY users on line is 0.'),
            CloseConn,
        ]

        async def test(conn):
            res = None
            try:
                await conn.cmd("ftp 77.88.1.117", timeout=0.2)
            except ExpectTimeout as e:
                logging.debug(repr(e))
                if b"CTRL + K" in e.auxiliary["stdout_buffer"]:
                    try:
                        await conn.cmd("\x0b", nl=False, echo="")
                    except ExecException as e2:
                        if str(e2) == "Failed to connect to the remote host.":
                            res = await conn.cmd("quit", expect_error=UnexpectedClose)
            finally:
                await conn.close()
                await asyncio.sleep(0.01)

            if res is not None:
                self.assertFalse(res)
                self.assertEqual(1, len(res.exceptions))
                self.assertEqual(EMPTY, res.out)
                self.assertEqual(
                    'Info: The max number of VTY users is 8, and the number of current VTY users on line is 0.',
                    res.err)
            else:
                self.fail("test failed")

        self.coro_test(dialog, test, VrpDevice)

    def test_interface_range_esc(self):
        dialog = [
            Send('\r\n<test>'),
            Expect('system-view\n'),
            SendEcho('system-view\r\n'),
            Send("Enter system view, return user view with return command.\r\n[~test]"),
            Expect("interface range 100GE 1/0/1 to 100GE1/0/2\n"),
            SendEcho("interface range 100GE 1/0/1 to 100GE1/0/2\r\n"),
            Send("[~test-port-group]"),
            Expect("port trunk allow-pass vlan 1\n"),
            SendEcho("port trunk allow-pass vlan 1\r\n"),
            Send("\rRunning: 33%\r"),
            Send("\rRunning: 33%\r"),
            Send('\rRunning: 66%\r'),
            Send('\rRunning: 66%\r'),
            Send('\r            \x1b[1A\r\n'),
            Send('\r\n[*test]'),
            ExpectCloseConn,
            CloseConn,
        ]

        exp = [
            ["Enter system view, return user view with return command.", EMPTY, 0],
            [EMPTY, EMPTY, 0],
            [EMPTY, EMPTY, 0],
        ]
        self.container_test(dialog, ["system-view", "interface range 100GE 1/0/1 to 100GE1/0/2", "port trunk allow-pass vlan 1"], VrpDevice,
                            exp)


class TestJnx(TestDevice):
    def test_bad_command(self):
        dialog = [
            Send('\r\n<username@test> '),
            Expect('show interfaces 40GE1/0/1:1\n'),
            SendEcho('show interfaces 40GE1/0/1:1 \r\n'),
            SendEcho(' '),
            SendEcho('\r\n'),
            Send("error: device 40GE1/0/1:1 not found\r\n\r\nusername@test> "),
            ExpectCloseConn,
            CloseConn,
        ]
        self.one_cmd_test(dialog,
                          "show interfaces 40GE1/0/1:1",
                          JnxDevice,
                          EMPTY,
                          "error: device 40GE1/0/1:1 not found",
                          1)

    def test_bad_command2(self):
        dialog = [
            Send('\r\n<username@test> '),
            Expect(
                'start shell command "cli show route receive-protocol bgp 127.0.0.1 | sed \'s/..//\' | awk \'{print $2}\' | sort -u"\n'),
            SendEcho('start'),
            SendEcho(' shell'),
            SendEcho('\r\n                    ^\r\n'
                     'syntax error, expecting <command>.\r\n\r'
                     'username@hostname> start shell   \x08\x08\x08command\r\n'
                     '                    ^\r\n'
                     'syntax error, expecting <command>.\r\n\r'
                     'username@hostname> start shellcommand   \x08\x08\x08"cli show route receive-protocol bgp 127.0.0.1 | sed \'s/..//\' | awk \'{print $2}\' | sort -u"\r\n'
                     '                    ^\r\nsyntax error, expecting <command>.\r\n'),
            Send("\r\n{master}\r\nusername@hostname>"),
            ExpectCloseConn,
            CloseConn,
        ]

        self.one_cmd_test(dialog,
                          'start shell command "cli show route receive-protocol bgp 127.0.0.1 | sed \'s/..//\' | awk \'{print $2}\' | sort -u"',
                          JnxDevice,
                          ('username@hostname> start shellcommand\n\nusername@hostname> start shellcommand"cli show route '
                           'receive-protocol bgp 127.0.0.1 | sed \'s/..//\' | awk \'{print $2}\' | sort -u"'),
                          '                    ^\nsyntax error, expecting <command>.                    ^\nsyntax error, expecting <command>.',
                          2)


class TestDeviceExprs(unittest.TestCase):
    def _test_dev_exprs_true(self, data: List[Union[bytes, str]], exprs: List[Expr]):
        for test_data in data:
            self.assertTrue(_test_exprs(exprs, test_data))

    def _test_dev_exprs_false(self, data: List[Union[bytes, str]], exprs: List[Expr]):
        for test_data in data:
            self.assertFalse(_test_exprs(exprs, test_data))

    def test_vrp_command_prompt(self):
        test_data_true = [
            "\r\n<test>",
            "\r\n[*test]",
            "\r\n[*man1-s10-40GE1/0/13]",
            "\r\n[*sas1-s411-40GE1/0/1:1]",
            "\n<tom1-s1.yndx.net>",
        ]
        test_data_false = [
            "\r\n[Slot_3]\r\n",
            "BOM=\n\n[Slot_3]\n",
        ]
        self._test_dev_exprs_true(test_data_true, VrpDevice.COMMAND_PROMPT)
        self._test_dev_exprs_false(test_data_false, VrpDevice.COMMAND_PROMPT)

    def test_ios_prompt(self):
        test_data_true = [
            "\r\nfol3-s1#",
            "\r\nfol3-s1>",
            "\r\nfol3-s1(config)#",
            "\r\n\rRP/0/RSP0/CPU0:m9-p1(config)#",
            "\rfol3-s1#",
            "\rfol3-s1>",
        ]
        self._test_dev_exprs_true(test_data_true, IosDevice.COMMAND_PROMPT)

    def test_jnx_command_prompt(self):
        test_data_true = [
            "\r\nusername@test-x1> ",
        ]
        self._test_dev_exprs_true(test_data_true, JnxDevice.COMMAND_PROMPT)

    def test_jnx_motd(self):
        test_data_true = [
            "Last login: Tue Jan 30 12:27:01 2018 from 95.108.170.150\r\n"
            "--- JUNOS 15.1F6.9 Kernel 64-bit  JNPR-10.1-20160616.329709_builder_stable_10\r\n"
            "Note: Junos is currently running in recovery mode on the OAM volume\r\n",
        ]
        self._test_dev_exprs_true(test_data_true, JnxDevice.MOTD)

    def test_vrp_prompt(self):
        self._test_dev_exprs_true([VRP_MOTD, VRP_MOTD2], VrpDevice.MOTD)

    def test_ekinops_command_prompt(self):
        test_data_true = [
            "\r\nadministra@dwdm-sas1-std(2137)",
        ]
        self._test_dev_exprs_true(test_data_true, EkinopsDevice.COMMAND_PROMPT)


class VrpQuestion(unittest.TestCase):
    def test_question(self):
        m = VrpDevice.QUESTION[0].check("\n local-user 3cd42 password irreversible-cipher $1Uf,]*kbJ$[@=cD6I3z]")
        self.assertFalse(m)


class Terminal(unittest.TestCase):
    def test_term_eval(self):
        res = b'\rRunning: 33%\r\rRunning: 33%\r\rRunning: 66%\r\rRunning: 66%\r\r            '
        m = term_eval(list(res))
        self.assertEqual(m, b"            ")


class Errors(unittest.TestCase):
    def test_match_errors_vrp(self):
        (stdout, stderr, exceptions) = match_errors(
            b"real result\n"
            b"Info: Succeeded in running the patch on the master board.\n"
            b"result line2\n"
            b"Info: Finished running the patch.\n",
            VrpDevice.COMMAND_ERROR)
        self.assertEqual(b"real result\n"
                         b"result line2\n",
                         stdout)
        self.assertEqual(b"Info: Succeeded in running the patch on the master board.\n"
                         b"Info: Finished running the patch.\n",
                         stderr)
        self.assertEqual([], exceptions)

    def test_match_errors_jun(self):
        (stdout, stderr, exceptions) = match_errors(
            b"real result\n"
            b"Info: Succeeded in running the patch on the master board.\n"
            b"result line2\n"
            b"Info: Finished running the patch.\n",
            VrpDevice.COMMAND_ERROR)
        self.assertEqual(b"real result\n"
                         b"result line2\n",
                         stdout)
        self.assertEqual(b"Info: Succeeded in running the patch on the master board.\n"
                         b"Info: Finished running the patch.\n",
                         stderr)
        self.assertEqual([], exceptions)


class AutoDeviceT(unittest.TestCase):
    def test_device_distinguisher(self):
        motd_and_prompt = (
            b"\r\n"
            b"Info: The max number of VTY users is 5, the number of current VTY users online is 1, and total number of "
            b"terminal users online is 1.\r\n      The current login time is 2018-01-01 01:01:01."
            b"\r\n      The last login time is 2018-01-01 01:91:17 from 127.0.0.1 through SSH."
            b"\r\n"
            b"<ce6850-ei-test>")
        res = AutoDevice.device_distinguisher(motd_and_prompt)
        self.assertEqual(res, [VrpDevice])

        ios_motd = ios.IosTelnetSuccessAuth().extract_motd_and_prompt()
        res = AutoDevice.device_distinguisher(ios_motd)
        self.assertEqual(res, [IosDevice])


class DataTest(TestDevice):
    def _make_dialog(self, data_class):
        session = data_class.get_full()
        res = []
        for s in session:
            if isinstance(s, DeviceWrite):
                res.append(Send(s.data))
            else:
                res.append(Expect(s.data))
        res.append(ExpectCloseConn)
        return res


class TestJnxTelnet(DataTest):
    nl = "\r\n"

    def test_jnx_telnet_auth(self):
        dialog = self._make_dialog(jnx.JnxTelnetSuccessAuth())
        self.one_cmd_test(dialog, send_cmd=None, dev_cls=JnxDevice, out="", err="", exc_count=0, write_nl=self.nl)

    def test_jnx_telnet_auth_fail(self):
        dialog = self._make_dialog(jnx.JnxTelnetAuthFail())
        self._auth_test(dialog, dev_cls=JnxDevice, write_nl=self.nl, expect_exception=AuthError)

    def test_jnx_command(self):
        target_data = jnx.JnxTelnetCompleteOnSpaceEcho()
        dialog = self._make_dialog(target_data)
        cmd = "sho ver | mat NEVER"
        self.one_cmd_test(dialog, send_cmd=cmd, dev_cls=JnxDevice, out="", err="", exc_count=0, write_nl=self.nl)

    def test_jnx_command2(self):
        target_data = jnx.JnxTelnetSuccessLongCommand()
        dialog = self._make_dialog(target_data)
        cmd = b'show interfaces et-0/0/1 | match index'
        self.one_cmd_test(dialog, send_cmd=cmd, dev_cls=JnxDevice,
                          out='  Interface index: 725, SNMP ifIndex: 802\n'
                              '  Logical interface et-0/0/1.0 (Index 633) (SNMP ifIndex 607)',
                          err="", exc_count=0, write_nl="\n", need_auth=False)

    def test_jnx_mock_command_fail(self):
        target_data = jnx.JnxTelnetMockCommand()
        dialog = self._make_dialog(target_data)
        # FIXME: не работает cmd типа bytes
        cmd = MOCK_COMMAND.decode()
        self.one_cmd_test(dialog, send_cmd=cmd, dev_cls=JnxDevice, out="", err="         ^\nunknown command.",
                          exc_count=1, write_nl=self.nl)

    def test_jnx_pager(self):
        target_data = jnx.JnxTelnetPager()
        dialog = self._make_dialog(target_data)
        cmd = "help topic interfaces mtu-protocol"
        expect = """
        Setting the Protocol MTU

           When you initially configure an interface, the protocol maximum
           transmission unit (MTU) is calculated automatically. If you subsequently
           change the media MTU, the protocol MTU on existing address families
           automatically changes.

           For a list of default protocol MTU values, see Configuring the Media MTU.

           To modify the MTU for a particular protocol family, include the mtu
           statement:

           mtu bytes;

           You can include this statement at the following hierarchy levels:

             * [edit interfaces interface-name unit logical-unit-number family
               family]
             * [edit logical-systems logical-system-name interfaces interface-name
               unit logical-unit-number family family]

           If you increase the size of the protocol MTU, you must ensure that the
           size of the media MTU is equal to or greater than the sum of the protocol
           MTU and the encapsulation overhead. For a lift of encapsulation overhead
           values, see Configuring the Media MTU. If you reduce the media MTU size,
           but there are already one or more address families configured and active
           on the interface, you must also reduce the protocol MTU size. (You
           configure the media MTU by including the mtu statement at the [edit
           interfaces interface-name] hierarchy level, as discussed in Configuring
           the Media MTU.)

                  +---------------------------------------------------------+
                  || Note: Changing the media MTU or protocol MTU causes an |
                  || interface to be deleted and added again.               |
                  +---------------------------------------------------------+

           The maximum number of data-link connection identifiers (DLCIs) is
           determined by the MTU on the interface. If you have keepalives enabled,
           the maximum number of DLCIs is 1000, with the MTU set to 5012.

           The actual frames transmitted also contain cyclic redundancy check (CRC)
           bits, which are not part of the MTU. For example, the default protocol MTU
           for a Gigabit Ethernet interface is 1500 bytes, but the largest possible
           frame size is actually 1504 bytes; you need to consider the extra bits in
           calculations of MTUs for interoperability.
        """
        expect = dedent(expect).strip()
        self.one_cmd_test(dialog, send_cmd=cmd, dev_cls=JnxDevice, out=expect, err="",
                          exc_count=0, write_nl=self.nl)


class TestIosTelnet(DataTest):
    nl = "\n"
    dev_cls = IosDevice

    def test_ios_telnet_auth(self):
        dialog = self._make_dialog(ios.IosTelnetSuccessAuth())
        self.one_cmd_test(dialog, send_cmd=None, dev_cls=self.dev_cls, out="", err="", exc_count=0, write_nl=self.nl)

    def test_ios_telnet_auth_fail(self):
        dialog = self._make_dialog(ios.IosTelnetAuthFail())
        self._auth_test(dialog, dev_cls=self.dev_cls, write_nl=self.nl, expect_exception=AuthError)

    def test_ios_mock_command_fail(self):
        target_data = ios.IosTelnetMockCommand()
        dialog = self._make_dialog(target_data)
        cmd = MOCK_COMMAND.decode()
        self.one_cmd_test(dialog, send_cmd=cmd, dev_cls=self.dev_cls, out="",
                          err="            ^\n% Invalid command at '^' marker.",
                          exc_count=1,
                          write_nl=self.nl)


class TestBash(DataTest):
    nl = "\n"
    dev_cls = PCDevice

    def test_bash_mock_command_fail(self):
        target_data = bash.BashMockCommand()
        dialog = self._make_dialog(target_data)
        cmd = MOCK_COMMAND.decode()
        self.one_cmd_test(dialog, send_cmd=cmd, dev_cls=self.dev_cls, out="",
                          err="-bash: /mock_command: No such file or directory",
                          exc_count=1,
                          write_nl=self.nl,
                          need_auth=False, command_prompt=True)


class TestEkinops(DataTest):
    nl = "\n"
    dev_cls = EkinopsDevice
    dev_cls.graceful_close = lambda x: NotImplementedError()

    def test_ekinops_auth_question(self):
        # CLI can ask question before prompt
        target_data = ekinops.EkinopsSshAuthQuestion()
        dialog = self._make_dialog(target_data)
        self._post_login_test(dialog, dev_cls=self.dev_cls, write_nl=self.nl)

    def test_ekinops_auth_fail(self):
        target_data = ekinops.EkinopsSshLoginFail()
        dialog = self._make_dialog(target_data)
        self._auth_test(dialog, dev_cls=self.dev_cls, write_nl=self.nl, username=ekinops.USERNAME,
                        password=ekinops.PASSWORD, expect_exception=AuthError)

    def test_ekinops_command_prompt(self):
        target_data = ekinops.EkinopsSshSuccessCommand()
        dialog = self._make_dialog(target_data)
        cmd = "uptime"
        self.one_cmd_test(dialog, send_cmd=cmd, dev_cls=self.dev_cls, out="84 days, 7h:00m:50s",
                          err="",
                          exc_count=0,
                          write_nl=self.nl,
                          need_auth=False)

    def test_ekinops_mock_command_fail(self):
        target_data = ekinops.EkinopsTelnetMockCommand()
        dialog = self._make_dialog(target_data)
        cmd = MOCK_COMMAND.decode()
        self.one_cmd_test(dialog, send_cmd=cmd, dev_cls=self.dev_cls, out="",
                          err="The command you entered was not found.",
                          exc_count=1,
                          write_nl=self.nl, need_auth=False)

    def test_ekinops_syntax_error_command(self):
        target_data = ekinops.EkinopsSshSyntaxErrorCommand()
        dialog = self._make_dialog(target_data)
        cmd = "get_measurements  3"
        self.one_cmd_test(dialog, send_cmd=cmd, dev_cls=self.dev_cls,
                          out=" ",  # FIXME: extra whitespace
                          err="Syntax error on the command line.\nSyntax: \n\n get_measurements [-h|board_nb port_id] ",
                          exc_count=1,
                          write_nl=self.nl, need_auth=False)


class GeneralDevice(BasicDevice):
    COMMAND_PROMPT = [Expr(r"\S+@\S+: ", name="gen_prompt")]
    CLI_INIT_QUESTION = [Expr("(.+\nEnter new password|\nRe-type new password): $", name="gen_cli_init_question")]

    def global_qhandler(self, cmd: 'Command', content: bytes):
        if content in [b'A password change is required for user username.\nEnter new password: ', b'\nRe-type new password: ']:
            return "newpass", False


class TestGeneralDevice(TestDevice):
    cmd_dialog1 = [
        Send('\nuser@host: '),
        Expect('some cmd\n'),
        SendEcho('some cmd\n'),
        Send('ok'),
        Send('\nuser@host: '),
        ExpectCloseConn,
        CloseConn,
    ]

    def test_prompt1(self):
        self.one_cmd_test(self.cmd_dialog1, send_cmd="some cmd", dev_cls=GeneralDevice, out="ok")

    def test_cli_init_question(self):
        dialog = [
            Send('A password change is required for user username.\r\nEnter new password: '),
            Expect('newpass\n'),
            Send('\nRe-type new password: '),
            Expect('newpass\n'),
            *self.cmd_dialog1
        ]
        self.one_cmd_test(dialog, send_cmd="some cmd", dev_cls=GeneralDevice, out="ok", need_auth=False)


class TestNetconf(TestDevice):
    jnx_dialog1 = [
        Send('<!-- No zombies were killed during the creation of this user interface -->\n'),
        Send('<!-- user username, class j-super-user -->\n'),
        Send('<hello xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">\n'),
        Send('  <capabilities>\n'
             '    <capability>urn:ietf:params:netconf:base:1.0</capability>\n'
             '    <capability>urn:ietf:params:netconf:capability:candidate:1.0</capability>\n'
             '    <capability>urn:ietf:params:netconf:capability:confirmed-commit:1.0</capability>\n'
             '    <capability>urn:ietf:params:netconf:capability:validate:1.0</capability>\n'
             '    <capability>urn:ietf:params:netconf:capability:url:1.0?scheme=http,ftp,file</capability>\n'
             '    <capability>urn:ietf:params:xml:ns:netconf:base:1.0</capability>\n'
             '    <capability>urn:ietf:params:xml:ns:netconf:capability:candidate:1.0</capability>\n'
             '    <capability>urn:ietf:params:xml:ns:netconf:capability:confirmed-commit:1.0</capability>\n'
             '    <capability>urn:ietf:params:xml:ns:netconf:capability:validate:1.0</capability>\n'
             '    <capability>urn:ietf:params:xml:ns:netconf:capability:url:1.0?protocol=http,ftp,file</capability>\n'
             '    <capability>urn:ietf:params:xml:ns:yang:ietf-netconf-monitoring</capability>\n'
             '    <capability>http://xml.juniper.net/netconf/junos/1.0</capability>\n'
             '    <capability>http://xml.juniper.net/dmi/system/1.0</capability>\n'
             '  </capabilities>\n'
             '  <session-id>33408</session-id>\n'
             '</hello>\n'
             ']]>]]>\n'),
        Expect(
            """<?xml version="1.0" encoding="UTF-8"?><hello xmlns="urn:ietf:params:xml:ns:netconf:base:1.0"><capabilities><capability>urn:ietf:params:netconf:base:1.0</capability>
<capability>urn:ietf:params:netconf:base:1.1</capability>
<capability>urn:ietf:params:netconf:capability:writable-running:1.0</capability>
<capability>urn:ietf:params:netconf:capability:candidate:1.0</capability>
<capability>urn:ietf:params:netconf:capability:confirmed-commit:1.0</capability>
<capability>urn:ietf:params:netconf:capability:rollback-on-error:1.0</capability>
<capability>urn:ietf:params:netconf:capability:startup:1.0</capability>
<capability>urn:ietf:params:netconf:capability:url:1.0?scheme=http,ftp,file,https,sftp</capability>
<capability>urn:ietf:params:netconf:capability:validate:1.0</capability>
<capability>urn:ietf:params:netconf:capability:xpath:1.0</capability>
<capability>urn:ietf:params:netconf:capability:notification:1.0</capability>
<capability>urn:liberouter:params:netconf:capability:power-control:1.0</capability>
<capability>urn:ietf:params:netconf:capability:interleave:1.0</capability>
<capability>urn:ietf:params:netconf:capability:with-defaults:1.0</capability></capabilities></hello>]]>]]>"""),
        # SendEcho('some cmd\n'),
        # Send('ok'),
        # Send('\nuser@host: '),
        # ExpectCloseConn,
        # CloseConn,
    ]

    def test_prompt1(self):
        cmd = "<get-system-uptime-information></get-system-uptime-information>"
        dialog = self.jnx_dialog1.copy()
        dialog.append(Expect(('<?xml version="1.0" encoding="UTF-8"?><rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" '
                              'message-id="1"><get-system-uptime-information></get-system-uptime-information></rpc>]]>]]>')))
        dialog.append(Send('<rpc-reply xmlns:junos="http://xml.juniper.net/junos/18.3R3/junos" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="1">\n'))
        dialog.append(Send(('<system-uptime-information xmlns="http://xml.juniper.net/junos/18.3R3/junos">\n<current-time>\n'
                            '<date-time junos:seconds="1596652361">2020-08-05 21:32:41 MSK</date-time>\n</current-time>\n<time-source>\n NTP CLOCK \n</time-source>\n')))
        dialog.append(Send('<system-booted-time>\n'))
        dialog.append(Send(('<date-time junos:seconds="1586889975">2020-04-14 21:46:15 MSK</date-time>\n<time-length junos:seconds="9762386">16w0d 23:46</time-length>\n'
                            '</system-booted-time>\n<protocols-started-time>\n<date-time junos:seconds="1586890069">')))
        dialog.append(Send(('2020-04-14 21:47:49 MSK</date-time>\n<time-length junos:seconds="9762292">16w0d 23:44</time-length>\n</protocols-started-time>\n'
                            '<last-configured-time>\n<date-time junos:seconds="1596546972">2020-08-04 16:16:12 MSK</date-time>\n<time-length junos:seconds="105389">'
                            '1d 05:16</time-length>\n<user>racktables</user>\n</last-configured-time>\n<uptime-information>\n<date-time junos:seconds="1596652361">\n9:32PM\n'
                            '</date-time>\n<up-time junos:seconds="9762360">\n112 days, 23:46\n</up-time>\n<active-user-count junos:format="5 users">\n5\n'
                            '</active-user-count>\n<load-average-1>\n0.33\n</load-average-1>\n<load-average-5>\n0.47\n</load-average-5>\n<load-average-15>\n0.54\n'
                            '</load-average-15>\n<user-table>\n</user-table>\n</uptime-information>\n')))
        dialog.append(Send('</system-uptime-information>\n</rpc-reply>\n]]>]]>\n'))
        dialog += [ExpectCloseConn, CloseConn]
        out = """<rpc-reply xmlns:junos="http://xml.juniper.net/junos/18.3R3/junos" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="1">
<system-uptime-information xmlns="http://xml.juniper.net/junos/18.3R3/junos">
<current-time>
<date-time junos:seconds="1596652361">2020-08-05 21:32:41 MSK</date-time>
</current-time>
<time-source>
 NTP CLOCK \n</time-source>
<system-booted-time>
<date-time junos:seconds="1586889975">2020-04-14 21:46:15 MSK</date-time>
<time-length junos:seconds="9762386">16w0d 23:46</time-length>
</system-booted-time>
<protocols-started-time>
<date-time junos:seconds="1586890069">2020-04-14 21:47:49 MSK</date-time>
<time-length junos:seconds="9762292">16w0d 23:44</time-length>
</protocols-started-time>
<last-configured-time>
<date-time junos:seconds="1596546972">2020-08-04 16:16:12 MSK</date-time>
<time-length junos:seconds="105389">1d 05:16</time-length>
<user>racktables</user>
</last-configured-time>
<uptime-information>
<date-time junos:seconds="1596652361">
9:32PM
</date-time>
<up-time junos:seconds="9762360">
112 days, 23:46
</up-time>
<active-user-count junos:format="5 users">
5
</active-user-count>
<load-average-1>
0.33
</load-average-1>
<load-average-5>
0.47
</load-average-5>
<load-average-15>
0.54
</load-average-15>
<user-table>
</user-table>
</uptime-information>
</system-uptime-information>
</rpc-reply>
"""
        self.one_cmd_test(dialog, send_cmd=cmd, dev_cls=NetconfDevice, out=out, need_auth=False, command_prompt=False,
                          sim_commands=True)
