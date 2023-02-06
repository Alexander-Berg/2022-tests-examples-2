import dataclasses
import pathlib
import typing


@dataclasses.dataclass(frozen=True)
class ConnectionInfo:
    """Mysql connection info class.

    :param port: database port
    :param hostname: database hostname
    :param user: database user
    :param password: database password
    :param dbname: database name
    """

    port: int = 3306
    hostname: str = 'localhost'
    user: typing.Optional[str] = None
    password: typing.Optional[str] = None
    dbname: typing.Optional[str] = None

    def replace(self, **kwargs) -> 'ConnectionInfo':
        """Returns new instance with attributes updated."""
        return dataclasses.replace(self, **kwargs)


@dataclasses.dataclass(frozen=True)
class ServiceSettings:
    port: int

    def get_conninfo(self) -> ConnectionInfo:
        return ConnectionInfo(port=self.port, user='root')


@dataclasses.dataclass(frozen=True)
class DatabaseConfig:
    dbname: str
    migrations: typing.List[pathlib.Path]


DatabasesDict = typing.Dict[str, DatabaseConfig]
