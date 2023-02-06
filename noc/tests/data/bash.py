from . import (Data, LoginPrompt, ExpectLogin, LoginEcho, PasswordEcho, PasswordPrompt, ExpectPassword, USERNAME,
               PASSWORD, Motd, CommandPrompt, AuthError, MOCK_COMMAND, WriteCommandEcho, ExpectCommand,
               WriteErrorCommand)

COMMAND_ERROR_VARIANTS = [
    b"zsh: no such file or directory: /non_exists_command_for_comocutor"
]


class BashDefaultPrompt(Data):
    session = [
        CommandPrompt(USERNAME + b"@hostname:~$ "),
    ]


class BashMockCommand(BashDefaultPrompt):
    session = [
        ExpectCommand(MOCK_COMMAND + b'\n'),
        WriteCommandEcho(MOCK_COMMAND + b'\r\n'),
        WriteErrorCommand(b'-bash: ' + MOCK_COMMAND + b': No such file or directory\r\n'),
        CommandPrompt(USERNAME + b"@hostname:~$ "),
    ]
