# flake8: noqa IS001

from typing import Any, Type


def as_json(obj):
    if obj is None:
        return None
    return obj.json(exclude_none=True)


class _ProxyField:
    def __init__(self, proxy_attribute_name: str, *nested_fields: str) -> None:
        self.proxy_attribute_name = proxy_attribute_name
        self.nested_fields = list(nested_fields)

    def __get__(self, instance, _owner) -> Any:
        """Get value of nested field."""
        if instance.auto_refresh:
            instance.refresh()

        proxy_object = getattr(instance, self.proxy_attribute_name)
        accessed_result = proxy_object
        for nested_field in self.nested_fields:
            if accessed_result is None:
                return None
            accessed_result = getattr(accessed_result, nested_field)
        return accessed_result

    def __set__(self, instance, value):
        """All intermediate attributes should exist."""

        proxy_object = getattr(instance, self.proxy_attribute_name)
        next_attr = proxy_object
        for nested_field in self.nested_fields[:-1]:
            next_attr = getattr(next_attr, nested_field)
        setattr(next_attr, self.nested_fields[-1], value)
        if instance.auto_save:
            instance.save()

    def __set_name__(self, _owner: Type, name: str) -> None:
        self.nested_fields.append(name)


def proxy_property(proxy_attribute_name: str, *nested_fields: str) -> Any:
    return _ProxyField(proxy_attribute_name, *nested_fields)
