class AnyString:
    def __eq__(self, other: object) -> bool:
        return isinstance(other, str)

    def __str__(self):
        return 'AnyString()'

    def __repr__(self):
        return str(self)
