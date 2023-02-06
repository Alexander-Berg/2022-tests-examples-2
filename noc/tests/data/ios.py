from . import (Data, LoginPrompt, ExpectLogin, LoginEcho, PasswordEcho, PasswordPrompt, ExpectPassword, USERNAME,
               PASSWORD, Motd, CommandPrompt, AuthError, MOCK_COMMAND, WriteCommandEcho, ExpectCommand,
               WriteErrorCommand)


PROMPT_VARIANTS = [
    b'\r\nRP/0/RSP0/CPU0:m9-p1#',
]

PAGER_VARIANTS = [
    b"\n--More--"
]

COMMAND_ERROR_VARIANTS = [
    b"% Bad IP address or host name% Unknown command or computer name, or unable to find computer address",
    b'% Ambiguous command:  "dis clock"',
    b"                  ^\n% Ambiguous command at '^' marker.",
    b"Permission denied. /isan/bin/nxpython: can't open file '/isan/bin/pipejson': [Errno 13] Permission denied",
    b"% Invalid input (privileged mode required)",  # arista
]


class IosTelnetAuth(Data):
    session = [
        LoginPrompt(b"Nexus 3000 Switch\r\n"
                    b"login: "),
        ExpectLogin(USERNAME + b"\n"),
        LoginEcho(USERNAME + b"\r\n"),
        PasswordEcho(b"\r\n"),
        PasswordPrompt(b"Password: "),
        ExpectPassword(PASSWORD + b"\n"),
    ]


class IosTelnetSuccessAuth(IosTelnetAuth):
    session = [
        Motd(b'\r\n'
             b'Bad terminal type: "network". Will assume vt100.\r\n'
             b'Cisco Nexus Operating System (NX-OS) Software\r\n'
             b'TAC support: http://www.cisco.com/tac\r\n'
             b'Copyright (c) 2002-2015, Cisco Systems, Inc. All rights reserved.\r\n'
             b'The copyrights to certain works contained in this software are\r\n'
             b'owned by other third parties and used and distributed under\r\n'
             b'license. Certain components of this software are licensed under\r\n'
             b'the GNU General Public License (GPL) version 2.0 or the GNU\r\n'
             b'Lesser General Public License (LGPL) Version 2.1. A copy of each\r\n'
             b'such license is available at\r\n'
             b'http://www.opensource.org/licenses/gpl-2.0.php and\r\n'
             b'http://www.opensource.org/licenses/lgpl-2.1.php\r\n'
             b'\r\x00'
             ),
        CommandPrompt(b"n3k-test# "),
    ]


class IosTelnetAuthFail(IosTelnetAuth):
    session = [
        AuthError(b'\r\n'
                  b'Login incorrect\r\n\r\n'),
        LoginPrompt(b"login: "),
        # IosTelnetAuth.session after this
    ]


class IosTelnetMockCommand(IosTelnetSuccessAuth):
    session = [
        ExpectCommand(MOCK_COMMAND + b'\n'),
        WriteCommandEcho(MOCK_COMMAND + b'\r\n'),
        WriteErrorCommand(b"            ^\n% Invalid command at '^' marker.\n"),
        CommandPrompt(b"n3k-test# "),
    ]

