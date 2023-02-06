from . import (Data, LoginPrompt, ExpectLogin, LoginEcho, PasswordEcho, PasswordPrompt, ExpectPassword, USERNAME,
               PASSWORD, Motd, CommandPrompt, AuthError, MOCK_COMMAND, WriteCommandEcho, ExpectCommand,
               WriteErrorCommand, WriteCommand, AskQuestion, PasswordError)
HOSTNAME=b"mk-ee-1"
USERNAME=b"admin"

PROMPT_VARIANTS = [
    b"[admin@mk-ee-1] > ",
    b"[admin@mk-ee-1] /interface> ",
    b"[admin@mk-ee-1] /interface ethernet> ",
    b"[admin@mk-ee-1] /user ssh-keys> ",
    b"[admin@mk-ee-1] /interface<SAFE> ",
]

COMMAND_ERROR_VARIANTS = [
    b"bad command name ttt (line 1 column 2)",
    b"syntax error (line 1 column 2)"
    b"[Safe mode released by another user]"
]

QUESTION_VARIANTS = [
    b"Reboot, yes? [y/N]:",
]

PAGER_VARIANTS = [
    b"-- [Q quit|D dump|down]"
]
