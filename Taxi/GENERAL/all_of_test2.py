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

from example_library.generated import models as example_library_models
from example_service.generated.service.swagger.models import api as api_module
from example_service.generated.service.swagger.models.api import extra as extra_module


class ExternalAllOf2:
    """ 

    Autogenerated. Do not edit the class manually.
    """
    __slots__: typing.Tuple[str, ...] = (
        '_name',
        '_age',
    )
    _use_py3_isoformat: bool = False

    _name: str
    _age: int

    def __init__(
        self,
        age: int,
        name: str,
    ) -> None:
        """Autogenerated."""
        use_py3_isoformat = self._use_py3_isoformat
        self.age = age
        self.name = name

    @classmethod
    def deserialize(
            cls,
            data: dict,
            *,
            allow_extra: bool = False,
            use_py3_isoformat: bool = False,
    ) -> 'ExternalAllOf2':
        if not isinstance(data, dict):
            raise utils.ValidationError(
                'Invalid value to deserialize ExternalAllOf2: '
                '%.1024r is not instance of dict' % data,
            )
        data = data.copy()
        use_py3_isoformat = use_py3_isoformat or cls._use_py3_isoformat
        age_ = data.pop('age', utils.SENTINEL)
        name_ = data.pop('name', utils.SENTINEL)
        return cls(
            name=name_,
            age=age_,
        )

    def serialize(self, use_py3_isoformat: bool = False) -> dict:
        self.validate_mutable_fields()
        use_py3_isoformat = use_py3_isoformat or self._use_py3_isoformat
        data: typing.Dict[str, typing.Any] = {
            'name': self._name,
            'age': self._age,
        }
        return data

    def validate_mutable_fields(self) -> None:
        """Validate fields that can be changed bypassing calling setters."""

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

    @property
    def age(self) -> int:
        return self._age

    @age.setter
    def age(self, value: int) -> None:
        if value is None or value is utils.SENTINEL:
            raise utils.ValidationError(
                'age is required property',
            )
        if not isinstance(value, int) or isinstance(value, bool):
            raise utils.ValidationError(
                'Invalid value for age: '
                '%.1024r is not instance of int' % value,
            )


        self._age = value

    def __repr__(self) -> str:
        return (
            'ExternalAllOf2('
            'name=%r'
            ', '
            'age=%r'
            ')' % (
                self.name,
                self.age,
            )
        )

    def __eq__(self, other) -> bool:
        return (
            isinstance(other, ExternalAllOf2) and
            self.name == other.name and 
            self.age == other.age
        )

    def __hash__(self) -> int:
        return hash((
            self.name, 
            self.age
        ))


class ExternalAllOfWithRefToObjWithRef:
    """ 

    Autogenerated. Do not edit the class manually.
    """
    __slots__: typing.Tuple[str, ...] = (
        '_extra_name',
        '_now',
        '_job',
        '_prop',
    )
    _use_py3_isoformat: bool = False

    _extra_name: typing.Optional[str]
    _now: typing.Optional['api_module.Now']
    _job: typing.Optional['example_library_models.Job']
    _prop: typing.Optional['extra_module.ExtraProperty']

    def __init__(
        self,
        extra_name: typing.Union[typing.Optional[str], utils.Sentinel] = utils.SENTINEL,
        job: typing.Union[typing.Optional['example_library_models.Job'], utils.Sentinel] = utils.SENTINEL,
        now: typing.Union[typing.Optional['api_module.Now'], utils.Sentinel] = utils.SENTINEL,
        prop: typing.Union[typing.Optional['extra_module.ExtraProperty'], utils.Sentinel] = utils.SENTINEL,
    ) -> None:
        """Autogenerated."""
        use_py3_isoformat = self._use_py3_isoformat

        if isinstance(extra_name, utils.Sentinel):
            self.extra_name = None
        else:
            self.extra_name = extra_name

        if isinstance(job, utils.Sentinel):
            self.job = None
        else:
            self.job = job

        if isinstance(now, utils.Sentinel):
            self.now = None
        else:
            self.now = now

        if isinstance(prop, utils.Sentinel):
            self.prop = None
        else:
            self.prop = prop

    @classmethod
    def deserialize(
            cls,
            data: dict,
            *,
            allow_extra: bool = False,
            use_py3_isoformat: bool = False,
    ) -> 'ExternalAllOfWithRefToObjWithRef':
        if not isinstance(data, dict):
            raise utils.ValidationError(
                'Invalid value to deserialize ExternalAllOfWithRefToObjWithRef: '
                '%.1024r is not instance of dict' % data,
            )
        data = data.copy()
        use_py3_isoformat = use_py3_isoformat or cls._use_py3_isoformat
        extra_name_ = data.pop('extra-name', utils.SENTINEL)
        job_ = data.pop('job', utils.SENTINEL)
        if job_ not in (utils.SENTINEL, None):
            job_ = example_library_models.Job.deserialize(
                job_,
                allow_extra=allow_extra,
                use_py3_isoformat=use_py3_isoformat,
            )
        now_ = data.pop('now', utils.SENTINEL)
        if now_ not in (utils.SENTINEL, None):
            now_ = api_module.Now.deserialize(
                now_,
                allow_extra=allow_extra,
                use_py3_isoformat=use_py3_isoformat,
            )
        prop_ = data.pop('prop', utils.SENTINEL)
        if prop_ not in (utils.SENTINEL, None):
            prop_ = extra_module.ExtraProperty.deserialize(
                prop_,
                allow_extra=allow_extra,
                use_py3_isoformat=use_py3_isoformat,
            )
        return cls(
            extra_name=extra_name_,
            now=now_,
            job=job_,
            prop=prop_,
        )

    def serialize(self, use_py3_isoformat: bool = False) -> dict:
        self.validate_mutable_fields()
        use_py3_isoformat = use_py3_isoformat or self._use_py3_isoformat
        data: typing.Dict[str, typing.Any] = {
        }
        if self._extra_name is not None:
            data['extra-name'] = self._extra_name
        if self._now is not None:
            data['now'] = self._now.serialize(
                use_py3_isoformat=use_py3_isoformat,
            )
        if self._job is not None:
            data['job'] = self._job.serialize(
                use_py3_isoformat=use_py3_isoformat,
            )
        if self._prop is not None:
            data['prop'] = self._prop.serialize(
                use_py3_isoformat=use_py3_isoformat,
            )
        return data

    def validate_mutable_fields(self) -> None:
        """Validate fields that can be changed bypassing calling setters."""

    @property
    def extra_name(self) -> typing.Optional[str]:
        return self._extra_name

    @extra_name.setter
    def extra_name(self, value: typing.Optional[str]) -> None:
        if value is None or value is utils.SENTINEL:
            self._extra_name = None
            return
        if not isinstance(value, str):
            raise utils.ValidationError(
                'Invalid value for extra-name: '
                '%.1024r is not instance of str' % value,
            )


        self._extra_name = value

    @property
    def now(self) -> typing.Optional['api_module.Now']:
        return self._now

    @now.setter
    def now(self, value: typing.Optional['api_module.Now']) -> None:
        if value is None or value is utils.SENTINEL:
            self._now = None
            return
        if not isinstance(value, api_module.Now):
            raise utils.ValidationError(
                'Invalid value for now: '
                '%.1024r is not instance of api_module.Now' % value,
            )


        self._now = value

    @property
    def job(self) -> typing.Optional['example_library_models.Job']:
        return self._job

    @job.setter
    def job(self, value: typing.Optional['example_library_models.Job']) -> None:
        if value is None or value is utils.SENTINEL:
            self._job = None
            return
        if not isinstance(value, example_library_models.Job):
            raise utils.ValidationError(
                'Invalid value for job: '
                '%.1024r is not instance of example_library_models.Job' % value,
            )


        self._job = value

    @property
    def prop(self) -> typing.Optional['extra_module.ExtraProperty']:
        return self._prop

    @prop.setter
    def prop(self, value: typing.Optional['extra_module.ExtraProperty']) -> None:
        if value is None or value is utils.SENTINEL:
            self._prop = None
            return
        if not isinstance(value, extra_module.ExtraProperty):
            raise utils.ValidationError(
                'Invalid value for prop: '
                '%.1024r is not instance of extra_module.ExtraProperty' % value,
            )


        self._prop = value

    def __repr__(self) -> str:
        return (
            'ExternalAllOfWithRefToObjWithRef('
            'extra_name=%r'
            ', '
            'now=%r'
            ', '
            'job=%r'
            ', '
            'prop=%r'
            ')' % (
                self.extra_name,
                self.now,
                self.job,
                self.prop,
            )
        )

    def __eq__(self, other) -> bool:
        return (
            isinstance(other, ExternalAllOfWithRefToObjWithRef) and
            self.extra_name == other.extra_name and 
            self.now == other.now and 
            self.job == other.job and 
            self.prop == other.prop
        )

    def __hash__(self) -> int:
        return hash((
            self.extra_name, 
            utils.generic_hash(self.now), 
            utils.generic_hash(self.job), 
            utils.generic_hash(self.prop)
        ))


