USERNAME = b"username"
PASSWORD = b"pass"
MOCK_COMMAND = b"/mock_command"


class DeviceWrite:
    def __init__(self, data: bytes):
        self.data = data

    def __repr__(self):
        return "<%s %r>" %(self.__class__.__name__, self.data)

    def __bytes__(self):
        return self.data


class DeviceRead:
    def __init__(self, data: bytes):
        self.data = data

    def __repr__(self):
        return "<%s %r>" %(self.__class__.__name__, self.data)


class LoginPrompt(DeviceWrite): pass


class LoginEcho(DeviceWrite): pass


class PasswordEcho(DeviceWrite): pass


class PasswordPrompt(DeviceWrite): pass


class PasswordError(DeviceWrite): pass


class Motd(DeviceWrite): pass


class CommandPrompt(DeviceWrite): pass


class AuthError(DeviceWrite): pass


class AskQuestion(DeviceWrite): pass


class WriteCommand(DeviceWrite):
    """
    Output of a command
    """
    pass


class WriteErrorCommand(DeviceWrite):
    """
    An error output of a command
    """
    pass


class WriteCommandEcho(DeviceWrite): pass


class ExpectLogin(DeviceRead): pass


class ExpectPassword(DeviceRead): pass


class ExpectCommand(DeviceRead): pass


# TODO: add test to name since it's a data used in tests.
class Data:
    session = []

    @classmethod
    def get_full(cls):
        bases = cls.__bases__
        if len(bases) != 1:
            raise NotImplementedError
        if cls is Data:
            return cls.session

        prev = bases[0].get_full()
        return prev + cls.session

    def extract_motd_and_prompt(self):
        res = []
        for elem in self.session:
            if isinstance(elem, (Motd, CommandPrompt)):
                res.append(elem)
        if not res:
            raise Exception("motd is not found")
        return b"".join(x.data for x in res)