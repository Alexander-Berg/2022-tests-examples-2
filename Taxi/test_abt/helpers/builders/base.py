import abc
import typing as tp


class BaseBuilder(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def build(self) -> tp.Union[dict, tp.List[dict]]:
        raise NotImplementedError

    def build_apply(self, func) -> tp.Any:
        return func(self.build())
