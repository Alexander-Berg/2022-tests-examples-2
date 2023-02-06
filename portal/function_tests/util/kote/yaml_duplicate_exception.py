# -*- coding: utf-8 -*-
# Код для проверки на дубликаты в ямле, найден на просторах интернета, все, что происходит дальше можно считать магией
# seems was found here https://gist.github.com/pypt/94d747fe5180851196eb
# TODO need check
from yaml.constructor import ConstructorError


def no_duplicates_constructor(loader, node, deep=False):
    """Check for duplicate keys."""

    mapping = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        value = loader.construct_object(value_node, deep=deep)
        if key in mapping:
            raise ConstructorError("while constructing a mapping", node.start_mark,
                                   "found duplicate key (%s)" % key, key_node.start_mark)
        mapping[key] = value

    return loader.construct_mapping(node, deep)
