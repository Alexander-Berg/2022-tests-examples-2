import codecs
import enum
import shlex
from typing import List, Optional


class ParsedCommand:

    def __init__(self) -> None:
        self.start_line_no: Optional[int] = None
        self.command: Optional[str] = None
        self.exit_code: str = "0"
        self.stdout: Optional[str] = None
        self.stderr: Optional[str] = None

    def validate(self) -> None:
        try:
            int(self.exit_code)
        except ValueError:
            raise RuntimeError(f"Command `{self.command}' at line {self.start_line_no} has invalid exit code")
        if self.stdout is not None and not self.stdout.endswith("\n"):
            self.stdout += "\n"
        if self.stderr is not None and not self.stderr.endswith("\n"):
            self.stderr += "\n"


class CommandMockData:

    def __init__(self, command: List[str], exit_code: int, stdout: Optional[str], stderr: Optional[str]) -> None:
        self.command = command
        self.exit_code = exit_code
        self.stdout = stdout
        self.stderr = stderr

    @staticmethod
    def from_parsed_command(parsed_command: ParsedCommand) -> "CommandMockData":
        return CommandMockData(
            command=shlex.split(parsed_command.command),
            exit_code=int(parsed_command.exit_code),
            stdout=parsed_command.stdout,
            stderr=parsed_command.stderr,
        )

    def __repr__(self):
        return (
            f"CommandMockData(command={repr(self.command)}, "
            f"exit_code={repr(self.exit_code)}, "
            f"stdout={repr(self.stdout)}, "
            f"stderr={repr(self.stderr)})"
        )


class ParseContext(enum.Enum):
    STDOUT = enum.auto()
    STDERR = enum.auto()


def parse_input_file(path: str) -> List[CommandMockData]:
    ret: List[CommandMockData] = []
    current = ParsedCommand()
    context: Optional[ParseContext] = None
    with codecs.open(path) as f:
        for i, line in enumerate(f):
            line_no = i + 1
            line = line.rstrip()
            if line.startswith("$ "):
                if current.command is not None:
                    current.validate()
                    ret.append(CommandMockData.from_parsed_command(current))
                    current = ParsedCommand()
                current.command = line.replace("$ ", "", 1)
                current.start_line_no = line_no
                context = None
            elif line.startswith("exit code: "):
                current.exit_code = line.replace("exit code: ", "", 1)
                context = None
            elif line.startswith("stdout: "):
                current.stdout = line.replace("stdout: ", "", 1)
                context = ParseContext.STDOUT
            elif line.startswith("stderr: "):
                current.stderr = line.replace("stderr: ", "", 1)
                context = ParseContext.STDERR
            else:
                if line.startswith("#"):
                    pass
                elif context is None and line.strip():
                    raise RuntimeError(f"Unknown line {line_no}: {line}")
                elif context == ParseContext.STDOUT:
                    current.stdout += "\n" + line
                elif context == ParseContext.STDERR:
                    current.stderr += "\n" + line
    current.validate()
    if current.command:
        ret.append(CommandMockData.from_parsed_command(current))
    return ret
