import dataclasses
from typing import List
from typing import Optional
from typing import Union


@dataclasses.dataclass
class Deeplink:
    deeplink: str


@dataclasses.dataclass
class Link:
    url: str
    title: Optional[str]
    is_external: bool


@dataclasses.dataclass
class NumberedItem:
    title: str
    subtitle: Optional[str]


@dataclasses.dataclass
class Paragraph:
    title: Optional[str]
    text: Optional[str]
    numbered_list: Optional[List[NumberedItem]]


@dataclasses.dataclass
class Button:
    text: str
    action: Union[Link, Deeplink]


@dataclasses.dataclass
class ScreenConstructor:
    main_title: str
    constructor: List[Paragraph]
    button: Button


@dataclasses.dataclass
class Payloads:
    achieved: ScreenConstructor
    achievable: Optional[ScreenConstructor]
