from typing import List


_DEFAULT = {'taxi': {'orders_provider': 'taxi', 'reset_modes': ['orders']}}


class Group:
    def __init__(
            self, name: str, orders_provider: str, reset_modes: List[str],
    ):
        self._name = name
        self._orders_provider = orders_provider
        self._reset_modes = reset_modes

    def name(self):
        return self._name

    def settings(self):
        return {
            'orders_provider': self._orders_provider,
            'reset_modes': self._reset_modes,
        }


def default_groups():
    return [Group(name='taxi', orders_provider='taxi', reset_modes=['orders'])]


def values(groups: List[Group]):
    return {g.name(): g.settings() for g in groups}


def default_values():
    return values(default_groups())
