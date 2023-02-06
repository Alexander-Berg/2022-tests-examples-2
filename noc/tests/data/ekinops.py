from . import (Data, LoginPrompt, ExpectLogin, LoginEcho, PasswordEcho, PasswordPrompt, ExpectPassword, USERNAME,
               PASSWORD, Motd, CommandPrompt, AuthError, MOCK_COMMAND, WriteCommandEcho, ExpectCommand,
               WriteErrorCommand, WriteCommand, AskQuestion, PasswordError)
HOSTNAME=b"hostname"
USERNAME=b"administra"

PROMPT_VARIANTS = [
    "\r\nadministra@host-name(2137)",
    "\r\nadministra@host-name(23548",
    "\r\nadministra@host-name()>",
    "\r\nadministra@dwdm-iva-strd-4()> "
]

COMMAND_ERROR_VARIANTS = [
    b"Syntax error on the command line. \nSyntax:  \n\n get_config [-h|board_nb port_id] "
]


PAGER_VARIANTS = [
    b"\n---- <q> to exit, <ENTER> for next line, <space> for next page ---- "
]


class EkinopsSshAuthSuccess(Data):
    session = [
        Motd(HOSTNAME + b"\r\n\r"),
        CommandPrompt(USERNAME + b"@" + HOSTNAME + b"()>                                                               "
                                                   b"                                                                  "
                                                   b"                                                                  "
                                                   b"                             \r" + USERNAME + b"@" + HOSTNAME + b"()>"),

    ]


class EkinopsSshLoginFail(Data):
    # some old software use cli auth and always authenticate ssh session
    session = [
        LoginPrompt(b"\rLogin  :                                              \rLogin  : "),
        ExpectLogin(USERNAME + b"\n"),
        LoginEcho(USERNAME + b"\r\n"),
        PasswordPrompt(b"\rPasswd :                                              \rPasswd : "),
        ExpectPassword(PASSWORD + b"\n"),
        PasswordError(b"\r\n"
                      b"Password authentication failed for '"
                      + USERNAME +
                      b"', try again.\r\n"
                      ),
        LoginPrompt(b"\rLogin  :                                              \rLogin  : "),
    ]


class EkinopsSshAuthQuestion(Data):
    session = [
        AskQuestion(b'Maximum number of CLI sessions reached.\r\n'),
        AskQuestion(b'Another session is already open for this user, you may want to close it.\r\n\r'
                    b'Continue ? (y/N)                                      \rContinue ? (y/N) '),  # width = 55
        ExpectCommand(b'y\n'),
        WriteCommandEcho(b'y\r\n'),
        Motd(HOSTNAME + b"\r\n\r"),
        CommandPrompt(b"\r" + USERNAME + b"@" + HOSTNAME + b"()>                        \r" + USERNAME + b"@" + HOSTNAME + b"()>"),
    ]


class EkinopsSshSuccessCommand(EkinopsSshAuthSuccess):
    session = [
        ExpectCommand(b'uptime\n'),
        WriteCommandEcho(b'uptime\r\n'),
        WriteCommand(b'84 days, 7h:00m:50s\r\n\r'),
        CommandPrompt(USERNAME + b"@" + HOSTNAME + b"()>                                                                "
                                                  b"                                                                   "
                                                  b"                                                                   "
                                                  b"                          \r" + USERNAME + b"@" + HOSTNAME + b"()>"),
    ]


class EkinopsTelnetMockCommand(EkinopsSshAuthSuccess):
    session = [
        ExpectCommand(MOCK_COMMAND + b"\n"),
        WriteCommandEcho(MOCK_COMMAND + b"\r\n"),
        WriteErrorCommand(b'The command you entered was not found.\r\n\r'),
        CommandPrompt(USERNAME + b"@" + HOSTNAME + b"()>                        \r"
                                                    + USERNAME + b"@" + HOSTNAME + b"()>"),
    ]


class EkinopsSshSyntaxErrorCommand(EkinopsSshAuthSuccess):
    session = [
        ExpectCommand(b"get_measurements  3\n"),
        WriteCommandEcho(b"get_measurements  3\r\n"),
        WriteErrorCommand(b'Syntax error on the command line. \r\nSyntax:  \r\n \r\n get_measurements [-h|board_nb port_id] \r\n \r\n\r'),
        CommandPrompt(USERNAME + b"@" + HOSTNAME + b"()>                        \r"
                                                    + USERNAME + b"@" + HOSTNAME + b"()>"),
    ]


class EkinopsSshPager(EkinopsSshAuthSuccess):
    session = [
        ExpectCommand(b'help\n'),
        WriteCommandEcho(b'help\r\n'),
        WriteCommand(b'The following commands are available :\r\nconfigure_pm                  [confpm]\r\ndelete                        [rm]\r\ndir                           [ls]\r\n\r---- <ENTER> for next line, <space> for next page, <q> to exit ---- \r'),


        CommandPrompt(USERNAME + b"@" + HOSTNAME + b"()>                                                                "
                                                  b"                                                                   "
                                                  b"                                                                   "
                                                  b"                          \r" + USERNAME + b"@" + HOSTNAME + b"()>"),
    ]
