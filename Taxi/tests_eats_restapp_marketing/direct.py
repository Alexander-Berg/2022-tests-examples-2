import dataclasses
import typing


@dataclasses.dataclass
class Message:
    code: str
    message: str

    def asdict(self) -> dict:
        return {'Code': self.code, 'Message': self.message}


@dataclasses.dataclass
class IdResult:
    # pylint: disable=invalid-name
    id: typing.Optional[int] = None
    warnings: typing.Optional[typing.List[Message]] = None
    errors: typing.Optional[typing.List[Message]] = None

    def __post_init__(self):
        assert self.id or self.warnings or self.errors

    def asdict(self) -> dict:
        result: dict = {}

        if self.id:
            result['Id'] = self.id

        if self.warnings:
            # pylint: disable=not-an-iterable
            result['Warnings'] = [w.asdict() for w in self.warnings]

        if self.errors:
            # pylint: disable=not-an-iterable
            result['Errors'] = [e.asdict() for e in self.errors]

        return result
