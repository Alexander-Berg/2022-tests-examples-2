import dataclasses
import enum
import typing


class Theme(str, enum.Enum):
    Light = 'light'
    Dark = 'dark'


@dataclasses.dataclass
class Color:
    theme: Theme
    color: str

    def as_layout_model(self) -> dict:
        return {'theme': self.theme, 'value': self.color}


@dataclasses.dataclass
class ColoredText:
    text: str
    text_key: str
    color: typing.List[Color]
    background: typing.List[Color]

    def as_layout_model(self, translations: typing.Dict[str, str]) -> dict:
        return {
            'text': translations[self.text_key],
            'color': [color.as_layout_model() for color in self.color],
            'background': [
                background.as_layout_model() for background in self.background
            ],
        }


@dataclasses.dataclass
class ThemedColorV2:
    dark: str
    light: str


@dataclasses.dataclass
class ColoredIconV2:
    uri: str
    color: typing.Optional[ThemedColorV2] = None
