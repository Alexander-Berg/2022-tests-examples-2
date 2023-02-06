import collections
import random
from typing import Counter
from typing import Dict
from typing import List
from typing import Optional
from typing import Sequence
from typing import Set
from typing import TypeVar
from typing import Union

Value = TypeVar('Value', int, float)
AnyValue = TypeVar('AnyValue')


def sum_dicts(
        dict1: Dict[str, Value], dict2: Dict[str, Value],
) -> Dict[str, Value]:
    counter: Counter[str] = collections.Counter()
    counter.update(dict1)
    counter.update(dict2)

    return dict(counter)


def sample(
        seq: Union[Set[AnyValue], Sequence[AnyValue]],
        limit: Optional[int] = None,
) -> List[AnyValue]:
    """
    Returns randomly selected elements from seq
    with limit (maximum is len(seq)).

    Args:
        seq (Union[Set[AnyValue], Sequence[AnyValue]]]): sequence
        limit (Optional[int], optional): maximum values. Defaults to None.

    Returns:
        List[AnyValue]: _description_
    """
    if limit is None or limit > len(seq):
        limit = len(seq)

    return random.sample(seq, k=limit)
