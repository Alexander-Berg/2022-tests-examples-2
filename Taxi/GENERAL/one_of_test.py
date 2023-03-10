# pylint: disable=too-many-lines
# pylint: disable=invalid-string-quote
# pylint: disable=wildcard-import
# pylint: disable=ungrouped-imports
# pylint: disable=unused-wildcard-import
# pylint: disable=redefined-builtin
# pylint: disable=unused-variable
# pylint: disable=redefined-outer-name
# pylint: disable=invalid-name
# pylint: disable=unnecessary-lambda

# pylint: disable=bad-whitespace
# flake8: noqa

# pylint: disable=cyclic-import

import datetime
import json
import orjson
import re
import typing
import uuid as uuid_module

from taxi.codegen import swaggen_serialization as utils
from taxi.util import dates as dates_utils

from example_service.generated.service.swagger.models.api import new_extra as new_extra_module


class CrossRef:
    """ 

    Autogenerated. Do not edit the class manually.
    """
    __slots__: typing.Tuple[str, ...] = (
        '_name',
    )
    _use_py3_isoformat: bool = False

    _name: typing.Optional['new_extra_module.NewExtraObject']

    def __init__(
        self,
        name: typing.Union[typing.Optional['new_extra_module.NewExtraObject'], utils.Sentinel] = utils.SENTINEL,
    ) -> None:
        """Autogenerated."""
        use_py3_isoformat = self._use_py3_isoformat

        if isinstance(name, utils.Sentinel):
            self.name = None
        else:
            self.name = name

    @classmethod
    def deserialize(
            cls,
            data: dict,
            *,
            allow_extra: bool = False,
            use_py3_isoformat: bool = False,
    ) -> 'CrossRef':
        if not isinstance(data, dict):
            raise utils.ValidationError(
                'Invalid value to deserialize CrossRef: '
                '%.1024r is not instance of dict' % data,
            )
        data = data.copy()
        use_py3_isoformat = use_py3_isoformat or cls._use_py3_isoformat
        name_ = data.pop('name', utils.SENTINEL)
        if name_ not in (utils.SENTINEL, None):
            name_ = new_extra_module.NewExtraObject.deserialize(
                name_,
                allow_extra=allow_extra,
                use_py3_isoformat=use_py3_isoformat,
            )
        if data and not allow_extra:
            raise utils.ValidationError(
                'Unexpected fields: %s' % list(data.keys()),
            )

        return cls(
            name=name_,
        )

    def serialize(self, use_py3_isoformat: bool = False) -> dict:
        self.validate_mutable_fields()
        use_py3_isoformat = use_py3_isoformat or self._use_py3_isoformat
        data: typing.Dict[str, typing.Any] = {
        }
        if self._name is not None:
            data['name'] = self._name.serialize(
                use_py3_isoformat=use_py3_isoformat,
            )
        return data

    def validate_mutable_fields(self) -> None:
        """Validate fields that can be changed bypassing calling setters."""

    @property
    def name(self) -> typing.Optional['new_extra_module.NewExtraObject']:
        return self._name

    @name.setter
    def name(self, value: typing.Optional['new_extra_module.NewExtraObject']) -> None:
        if value is None or value is utils.SENTINEL:
            self._name = None
            return
        if not isinstance(value, new_extra_module.NewExtraObject):
            raise utils.ValidationError(
                'Invalid value for name: '
                '%.1024r is not instance of new_extra_module.NewExtraObject' % value,
            )


        self._name = value

    def __repr__(self) -> str:
        return (
            'CrossRef('
            'name=%r'
            ')' % (
                self.name,
            )
        )

    def __eq__(self, other) -> bool:
        return (
            isinstance(other, CrossRef) and
            self.name == other.name
        )

    def __hash__(self) -> int:
        return hash((
            utils.generic_hash(self.name)
        ))


class OneDiscriminator:
    """ 

    Autogenerated. Do not edit the class manually.
    """
    __slots__: typing.Tuple[str, ...] = (
        '_object_type',
        '_name',
    )
    _use_py3_isoformat: bool = False

    _object_type: str
    _name: str

    def __init__(
        self,
        name: str,
        object_type: str,
    ) -> None:
        """Autogenerated."""
        use_py3_isoformat = self._use_py3_isoformat
        self.name = name
        self.object_type = object_type

    @classmethod
    def deserialize(
            cls,
            data: dict,
            *,
            allow_extra: bool = False,
            use_py3_isoformat: bool = False,
    ) -> 'OneDiscriminator':
        if not isinstance(data, dict):
            raise utils.ValidationError(
                'Invalid value to deserialize OneDiscriminator: '
                '%.1024r is not instance of dict' % data,
            )
        data = data.copy()
        use_py3_isoformat = use_py3_isoformat or cls._use_py3_isoformat
        name_ = data.pop('name', utils.SENTINEL)
        object_type_ = data.pop('object_type', utils.SENTINEL)
        if data:
            raise utils.ValidationError(
                'Unexpected fields: %s' % list(data.keys()),
            )

        return cls(
            object_type=object_type_,
            name=name_,
        )

    def serialize(self, use_py3_isoformat: bool = False) -> dict:
        self.validate_mutable_fields()
        use_py3_isoformat = use_py3_isoformat or self._use_py3_isoformat
        data: typing.Dict[str, typing.Any] = {
            'object_type': self._object_type,
            'name': self._name,
        }
        return data

    def validate_mutable_fields(self) -> None:
        """Validate fields that can be changed bypassing calling setters."""

    @property
    def object_type(self) -> str:
        return self._object_type

    @object_type.setter
    def object_type(self, value: str) -> None:
        if value is None or value is utils.SENTINEL:
            raise utils.ValidationError(
                'object_type is required property',
            )
        if not isinstance(value, str):
            raise utils.ValidationError(
                'Invalid value for object_type: '
                '%.1024r is not instance of str' % value,
            )


        self._object_type = value

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        if value is None or value is utils.SENTINEL:
            raise utils.ValidationError(
                'name is required property',
            )
        if not isinstance(value, str):
            raise utils.ValidationError(
                'Invalid value for name: '
                '%.1024r is not instance of str' % value,
            )


        self._name = value

    def __repr__(self) -> str:
        return (
            'OneDiscriminator('
            'object_type=%r'
            ', '
            'name=%r'
            ')' % (
                self.object_type,
                self.name,
            )
        )

    def __eq__(self, other) -> bool:
        return (
            isinstance(other, OneDiscriminator) and
            self.object_type == other.object_type and 
            self.name == other.name
        )

    def __hash__(self) -> int:
        return hash((
            self.object_type, 
            self.name
        ))



