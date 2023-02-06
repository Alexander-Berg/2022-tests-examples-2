import contextlib
import copy
import dataclasses
import json
from typing import Any
from typing import Dict

import pytest

from scout import version_info
from test_scout.web import persistent_storage_utils


TVM_NAME_A = 'alpha'
TVM_NAME_B = 'bravo'
TVM_NAME_C = 'charlie'


class TestServiceDestinationsParse:
    VersionInfoCls = version_info.ServiceDestinationsVersion
    STANDARD_PARAMS: Dict[str, Any] = {
        'meta_version': 10,
        'data_version': 1000,
    }

    def test_success(self):
        parsed = self.VersionInfoCls.parse(json.dumps(self.STANDARD_PARAMS))
        assert parsed == self.VersionInfoCls(**self.STANDARD_PARAMS)

    @pytest.mark.parametrize(
        'value', ['', 'null', '{}', '[]', '1000', '[1000]', 'not json at all'],
    )
    def test_invalid(self, value):
        parsed = self.VersionInfoCls.parse(value)
        assert parsed is None

    @pytest.mark.parametrize('field_name', ['meta_version', 'data_version'])
    def test_missing_field(self, field_name):
        data = copy.deepcopy(self.STANDARD_PARAMS)
        data.pop(field_name)
        parsed = self.VersionInfoCls.parse(json.dumps(data))
        assert parsed is None, f'data "{data}"'

    @pytest.mark.parametrize('field_name', ['meta_version', 'data_version'])
    def test_null_field(self, field_name):
        data = copy.deepcopy(self.STANDARD_PARAMS)
        data[field_name] = None
        parsed = self.VersionInfoCls.parse(json.dumps(data))
        assert parsed is None, f'data "{data}"'

    def test_extra_field(self):
        data = copy.deepcopy(self.STANDARD_PARAMS)
        data['extra_field'] = 2000
        parsed = self.VersionInfoCls.parse(json.dumps(data))
        assert parsed is None, f'data "{data}"'

    @pytest.mark.parametrize(
        ['field_name', 'field_values'],
        [
            ('meta_version', (10.0, '10', {})),
            ('data_version', (1000.0, '1000', {})),
        ],
    )
    def test_invalid_field_type(self, field_name, field_values):
        for value in field_values:
            data = copy.deepcopy(self.STANDARD_PARAMS)
            data[field_name] = value
            parsed = self.VersionInfoCls.parse(json.dumps(data))
            assert parsed is None, f'data "{data}"'


class TestServiceDestinationsStatus:
    VersionStatusCls = version_info.VersionStatus
    VersionInfoCls = version_info.ServiceDestinationsVersion
    META_OLDER = 9
    META_EQUAL = 10
    META_NEWER = 11
    DATA_OLDER = 900
    DATA_EQUAL = 1000
    DATA_NEWER = 1100
    STANDARD_PARAMS = {'meta_version': META_EQUAL, 'data_version': DATA_EQUAL}

    def test_none(self):
        status = self.VersionInfoCls.get_status(None, **self.STANDARD_PARAMS)
        assert status.is_older

    @pytest.mark.parametrize(
        ['meta_version', 'data_version', 'status'],
        [
            (META_OLDER, DATA_OLDER, VersionStatusCls.Older),
            (META_OLDER, DATA_EQUAL, VersionStatusCls.Older),
            (META_OLDER, DATA_NEWER, VersionStatusCls.Older),
            # ===
            (META_EQUAL, DATA_OLDER, VersionStatusCls.Older),
            (META_EQUAL, DATA_EQUAL, VersionStatusCls.Equal),
            (META_EQUAL, DATA_NEWER, VersionStatusCls.Newer),
            # ===
            (META_NEWER, DATA_OLDER, VersionStatusCls.Newer),
            (META_NEWER, DATA_EQUAL, VersionStatusCls.Newer),
            (META_NEWER, DATA_NEWER, VersionStatusCls.Newer),
        ],
    )
    def test_args(self, meta_version, data_version, status):
        client_version = self.VersionInfoCls(
            meta_version=meta_version, data_version=data_version,
        )
        client_status = self.VersionInfoCls.get_status(
            client_version, **self.STANDARD_PARAMS,
        )
        assert client_status == status, f'client_version "{client_version}"'


class TestEndpointsParse:
    VersionInfoCls = version_info.EndpointVersion
    STANDARD_PARAMS: Dict[str, Any] = {
        'meta_version': 10,
        'data_version': {TVM_NAME_A: 100, TVM_NAME_B: 200},
    }

    @pytest.mark.parametrize(
        'params', [STANDARD_PARAMS, {'meta_version': 10, 'data_version': {}}],
    )
    def test_success(self, params):
        parsed = self.VersionInfoCls.parse(json.dumps(params))
        assert parsed == self.VersionInfoCls(**params)

    @pytest.mark.parametrize(
        'value', ['', 'null', '{}', '[]', '1000', '[1000]', 'not json at all'],
    )
    def test_invalid(self, value):
        parsed = self.VersionInfoCls.parse(value)
        assert parsed is None

    @pytest.mark.parametrize('field_name', ['meta_version', 'data_version'])
    def test_missing_field(self, field_name):
        data = copy.deepcopy(self.STANDARD_PARAMS)
        data.pop(field_name)
        parsed = self.VersionInfoCls.parse(json.dumps(data))
        assert parsed is None, f'data "{data}"'

    @pytest.mark.parametrize('field_name', ['meta_version', 'data_version'])
    def test_null_field(self, field_name):
        data = copy.deepcopy(self.STANDARD_PARAMS)
        data[field_name] = None
        parsed = self.VersionInfoCls.parse(json.dumps(data))
        assert parsed is None, f'data "{data}"'

    def test_extra_field(self):
        data = copy.deepcopy(self.STANDARD_PARAMS)
        data['extra_field'] = 2000
        parsed = self.VersionInfoCls.parse(json.dumps(data))
        assert parsed is None, f'data "{data}"'

    @pytest.mark.parametrize(
        ['field_name', 'field_values'],
        [
            ('meta_version', (10.0, '10', {})),
            ('data_version', (100, '100', [], {TVM_NAME_A: 100.0})),
        ],
    )
    def test_invalid_field_type(self, field_name, field_values):
        for value in field_values:
            data = copy.deepcopy(self.STANDARD_PARAMS)
            data[field_name] = value
            parsed = self.VersionInfoCls.parse(json.dumps(data))
            assert parsed is None, f'data "{data}"'


@dataclasses.dataclass(frozen=True)
class EndpointMock:
    version: int


@contextlib.asynccontextmanager
async def make_endpoints_persist(path):
    make = persistent_storage_utils.make_persistent_component
    async with make(dir_path=path) as storage:
        storage.store(TVM_NAME_A, EndpointMock(version=1000))
        storage.store(TVM_NAME_B, EndpointMock(version=2000))
        storage.store(TVM_NAME_C, EndpointMock(version=3000))
        storage.store('tango', EndpointMock(version=9000))

        yield storage


def make_direct_link(tvm_name) -> str:
    return f'direct_link_{tvm_name}'


def make_endpoints_data(*versions_args: int) -> Dict[str, int]:
    tvm_names_list = [TVM_NAME_A, TVM_NAME_B, TVM_NAME_C]
    return {
        make_direct_link(tvm_name): version
        for tvm_name, version in zip(tvm_names_list, versions_args)
    }


class TestEndpointsStatus:
    VersionStatusCls = version_info.VersionStatus
    VersionInfoCls = version_info.EndpointVersion

    TVM_NAMES_TO_DIRECT_LINK = {
        tvm_name: make_direct_link(tvm_name)
        for tvm_name in [TVM_NAME_A, TVM_NAME_B, TVM_NAME_C]
    }

    META_OLDER = 9
    META_EQUAL = 10
    META_NEWER = 11

    DATA_A_OLDER = 900
    DATA_A_EQUAL = 1000
    DATA_A_NEWER = 1100

    DATA_B_OLDER = 1900
    DATA_B_EQUAL = 2000
    DATA_B_NEWER = 2100

    DATA_C_OLDER = 2900
    DATA_C_EQUAL = 3000
    DATA_C_NEWER = 3100

    DATA_ALL_OLDER = make_endpoints_data(
        DATA_A_OLDER, DATA_B_OLDER, DATA_C_OLDER,
    )
    DATA_ALL_EQUAL = make_endpoints_data(
        DATA_A_EQUAL, DATA_B_EQUAL, DATA_C_EQUAL,
    )
    DATA_ALL_NEWER = make_endpoints_data(
        DATA_A_NEWER, DATA_B_NEWER, DATA_C_NEWER,
    )

    DATA_1OLDER_2EQUAL = make_endpoints_data(
        DATA_A_OLDER, DATA_B_EQUAL, DATA_C_EQUAL,
    )
    DATA_1NEWER_2EQUAL = make_endpoints_data(
        DATA_A_NEWER, DATA_B_EQUAL, DATA_C_EQUAL,
    )
    DATA_1OLDER_1EQUAL_1NEWER = make_endpoints_data(
        DATA_A_OLDER, DATA_B_EQUAL, DATA_C_NEWER,
    )

    @pytest.mark.parametrize('tvm_names', [{}, TVM_NAMES_TO_DIRECT_LINK])
    async def test_none(self, storage_dir, tvm_names):
        async with make_endpoints_persist(storage_dir) as storage:
            client_status = self.VersionInfoCls.get_status(
                None,
                meta_version=self.META_EQUAL,
                tvm_names_to_endpoints=storage,
                tvm_names_to_direct_link=tvm_names,
            )
            assert client_status.is_older

    @pytest.mark.parametrize(
        ['meta_version', 'data_version', 'status'],
        [
            (META_OLDER, DATA_ALL_OLDER, VersionStatusCls.Older),
            (META_OLDER, DATA_ALL_EQUAL, VersionStatusCls.Older),
            (META_OLDER, DATA_ALL_NEWER, VersionStatusCls.Older),
            (META_OLDER, DATA_1OLDER_2EQUAL, VersionStatusCls.Older),
            (META_OLDER, DATA_1NEWER_2EQUAL, VersionStatusCls.Older),
            (META_OLDER, DATA_1OLDER_1EQUAL_1NEWER, VersionStatusCls.Older),
            # ===
            (META_EQUAL, DATA_ALL_OLDER, VersionStatusCls.Equal),
            (META_EQUAL, DATA_ALL_EQUAL, VersionStatusCls.Equal),
            (META_EQUAL, DATA_ALL_NEWER, VersionStatusCls.Equal),
            (META_EQUAL, DATA_1OLDER_2EQUAL, VersionStatusCls.Equal),
            (META_EQUAL, DATA_1NEWER_2EQUAL, VersionStatusCls.Equal),
            (META_EQUAL, DATA_1OLDER_1EQUAL_1NEWER, VersionStatusCls.Equal),
            # ===
            (META_NEWER, DATA_ALL_OLDER, VersionStatusCls.Newer),
            (META_NEWER, DATA_ALL_EQUAL, VersionStatusCls.Newer),
            (META_NEWER, DATA_ALL_NEWER, VersionStatusCls.Newer),
            (META_NEWER, DATA_1OLDER_2EQUAL, VersionStatusCls.Newer),
            (META_NEWER, DATA_1NEWER_2EQUAL, VersionStatusCls.Newer),
            (META_NEWER, DATA_1OLDER_1EQUAL_1NEWER, VersionStatusCls.Newer),
        ],
    )
    async def test_args_without_tvm_names(
            self, storage_dir, meta_version, data_version, status,
    ):
        client_version = self.VersionInfoCls(
            meta_version=meta_version, data_version=data_version,
        )

        async with make_endpoints_persist(storage_dir) as storage:
            client_status = self.VersionInfoCls.get_status(
                client_version,
                meta_version=self.META_EQUAL,
                tvm_names_to_endpoints=storage,
                tvm_names_to_direct_link={},
            )
            assert (
                client_status == status
            ), f'client_version "{client_version}"'

    @pytest.mark.parametrize(
        ['meta_version', 'data_version', 'status'],
        [
            (META_OLDER, DATA_ALL_OLDER, VersionStatusCls.Older),
            (META_OLDER, DATA_ALL_EQUAL, VersionStatusCls.Older),
            (META_OLDER, DATA_ALL_NEWER, VersionStatusCls.Older),
            (META_OLDER, DATA_1OLDER_2EQUAL, VersionStatusCls.Older),
            (META_OLDER, DATA_1NEWER_2EQUAL, VersionStatusCls.Older),
            (META_OLDER, DATA_1OLDER_1EQUAL_1NEWER, VersionStatusCls.Older),
            # ===
            (META_EQUAL, DATA_ALL_OLDER, VersionStatusCls.Older),
            (META_EQUAL, DATA_ALL_EQUAL, VersionStatusCls.Equal),
            (META_EQUAL, DATA_ALL_NEWER, VersionStatusCls.Newer),
            (META_EQUAL, DATA_1OLDER_2EQUAL, VersionStatusCls.Older),
            (META_EQUAL, DATA_1NEWER_2EQUAL, VersionStatusCls.Newer),
            (META_EQUAL, DATA_1OLDER_1EQUAL_1NEWER, VersionStatusCls.Newer),
            # ===
            (META_NEWER, DATA_ALL_OLDER, VersionStatusCls.Newer),
            (META_NEWER, DATA_ALL_EQUAL, VersionStatusCls.Newer),
            (META_NEWER, DATA_ALL_NEWER, VersionStatusCls.Newer),
            (META_NEWER, DATA_1OLDER_2EQUAL, VersionStatusCls.Newer),
            (META_NEWER, DATA_1NEWER_2EQUAL, VersionStatusCls.Newer),
            (META_NEWER, DATA_1OLDER_1EQUAL_1NEWER, VersionStatusCls.Newer),
        ],
    )
    async def test_args_with_tvm_names_all(
            self, storage_dir, meta_version, data_version, status,
    ):
        client_version = self.VersionInfoCls(
            meta_version=meta_version, data_version=data_version,
        )

        async with make_endpoints_persist(storage_dir) as storage:
            client_status = self.VersionInfoCls.get_status(
                client_version,
                meta_version=self.META_EQUAL,
                tvm_names_to_endpoints=storage,
                tvm_names_to_direct_link=self.TVM_NAMES_TO_DIRECT_LINK,
            )
            assert (
                client_status == status
            ), f'client_version "{client_version}"'

    @pytest.mark.parametrize(
        ['meta_version', 'data_version', 'status'],
        [
            (META_OLDER, DATA_ALL_OLDER, VersionStatusCls.Older),
            (META_OLDER, DATA_ALL_EQUAL, VersionStatusCls.Older),
            (META_OLDER, DATA_ALL_NEWER, VersionStatusCls.Older),
            (META_OLDER, DATA_1OLDER_2EQUAL, VersionStatusCls.Older),
            (META_OLDER, DATA_1NEWER_2EQUAL, VersionStatusCls.Older),
            (META_OLDER, DATA_1OLDER_1EQUAL_1NEWER, VersionStatusCls.Older),
            # ===
            (META_EQUAL, DATA_ALL_OLDER, VersionStatusCls.Older),
            (META_EQUAL, DATA_ALL_EQUAL, VersionStatusCls.Older),
            (META_EQUAL, DATA_ALL_NEWER, VersionStatusCls.Newer),
            (META_EQUAL, DATA_1OLDER_2EQUAL, VersionStatusCls.Older),
            (META_EQUAL, DATA_1NEWER_2EQUAL, VersionStatusCls.Newer),
            (META_EQUAL, DATA_1OLDER_1EQUAL_1NEWER, VersionStatusCls.Newer),
            # ===
            (META_NEWER, DATA_ALL_OLDER, VersionStatusCls.Newer),
            (META_NEWER, DATA_ALL_EQUAL, VersionStatusCls.Newer),
            (META_NEWER, DATA_ALL_NEWER, VersionStatusCls.Newer),
            (META_NEWER, DATA_1OLDER_2EQUAL, VersionStatusCls.Newer),
            (META_NEWER, DATA_1NEWER_2EQUAL, VersionStatusCls.Newer),
            (META_NEWER, DATA_1OLDER_1EQUAL_1NEWER, VersionStatusCls.Newer),
        ],
    )
    async def test_args_with_tvm_names_ac(
            self, storage_dir, meta_version, data_version, status,
    ):
        new_data_version = copy.deepcopy(data_version)
        new_data_version.pop(make_direct_link(TVM_NAME_B))

        client_version = self.VersionInfoCls(
            meta_version=meta_version, data_version=new_data_version,
        )

        async with make_endpoints_persist(storage_dir) as storage:
            client_status = self.VersionInfoCls.get_status(
                client_version,
                meta_version=self.META_EQUAL,
                tvm_names_to_endpoints=storage,
                tvm_names_to_direct_link=self.TVM_NAMES_TO_DIRECT_LINK,
            )
            assert (
                client_status == status
            ), f'client_version "{client_version}"'
