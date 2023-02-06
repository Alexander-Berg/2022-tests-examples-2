from typing import Type


def codegen(type_: Type) -> Type:
    def _eq(self, other):
        return self.serialize() == other.serialize()

    return type(f'Equatable{type_.__name__}', (type_,), {'__eq__': _eq})


def by_type(type_: Type) -> Type:
    class EqToObjWithGivenType:
        def __init__(self, *args, **kwargs):
            pass

        def __eq__(self, other):
            del self  # unused
            return isinstance(other, type_)

    return EqToObjWithGivenType
