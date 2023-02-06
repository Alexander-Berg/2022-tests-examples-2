from typing import Dict
from typing import List
from typing import NamedTuple


class Case(NamedTuple):
    data: Dict
    not_existed_names: List[str] = []
    response_code: int = 200
    expected_response: Dict = {}

    @classmethod
    def get_args(cls) -> str:
        return ','.join(cls.__annotations__.keys())  # pylint: disable=E1101
