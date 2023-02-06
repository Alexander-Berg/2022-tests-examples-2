# -*- coding: utf-8 -*-
# pylint: disable=redefined-outer-name
import importlib
from collections import namedtuple, defaultdict
from datetime import datetime

import mock
import pathlib2
from aniso8601.utcoffset import UTCOffset

UTC = UTCOffset('UTC', 0)


def test_some(tmpdir):
    upload_phits_index_to_yt = (
        importlib.import_module('sandbox.projects.advq.impl.upload_phits_index_to_yt')
        .upload_phits_index_to_yt
    )
    yt_client = mock.MagicMock()

    yt_node_to_attr = {
        '//root/rus/spikes/table1': {'type': 'table'},
        '//root/rus/spikes/file-not-from-sandbox': {'type': 'file'},
        '//root/rus/spikes/file20170105': {
            'type': 'file',
            'sandbox_creation_time': '2017-01-05T12:00:00Z',
            'sandbox_resource_id': 123,
        },
        '//root/rus/spikes/file20170106': {
            'type': 'file',
            'sandbox_creation_time': '2017-01-06T12:00:00Z',
            'sandbox_resource_id': 456,
        },
        '//root/rus/spikes/file20170107': {
            'type': 'file',
            'sandbox_creation_time': '2017-01-07T12:00:00Z',
            'sandbox_resource_id': 789,
        },
    }

    from yt.yson.yson_types import YsonString, YsonList

    def yt_list(yt_dir, attributes):
        result = []
        for key, attrs in yt_node_to_attr.iteritems():
            elem = YsonString(key[len(yt_dir.rstrip('/')):].lstrip('/'))
            elem.attributes.update({
                attr_name: attrs[attr_name]
                for attr_name in attributes
                if attr_name in attrs
            })
            result.append(elem)
        return YsonList(result)

    yt_client.list.side_effect = yt_list

    PhitsResourceMock = namedtuple(
        'ResourceMock', 'id released path created advq_phits_type advq_db')

    sandbox_resources = [
        # Этот файл уже на YT
        PhitsResourceMock(123, 'stable', pathlib2.PosixPath('file20170105'),
                          datetime(2017, 1, 5, 12, 0, tzinfo=UTC), 'spikes', 'rus'),

        # Независимо от того, есть ли на sandbox более свежий или более старый файл,
        # файлы на YT автоматически НЕ перезаписываются.
        PhitsResourceMock(455, 'stable', pathlib2.PosixPath('file20170106'),
                          datetime(2017, 1, 6, 7, 0, tzinfo=UTC), 'spikes', 'rus'),
        PhitsResourceMock(790, 'stable', pathlib2.PosixPath('file20170107'),
                          datetime(2017, 1, 7, 17, 0, tzinfo=UTC), 'spikes', 'rus'),

        # А вот этот файл должен быть записан.
        PhitsResourceMock(777, 'stable', pathlib2.PosixPath('file20170108'),
                          datetime(2017, 1, 8, 12, 0, tzinfo=UTC), 'spikes', 'rus'),
    ]

    # Здесь бы не помешал интерфейс как в джаве
    def sandbox_list_dbs(resource_type, phits_type, dbs, release_type, extra_attrs=None):
        if extra_attrs:
            raise NotImplementedError
        result = defaultdict(lambda: defaultdict(list))
        for resource in sandbox_resources:
            if (
                    isinstance(resource, resource_type)
                    and phits_type == resource.advq_phits_type
                    and resource.advq_db in dbs
                    and release_type == resource.released
            ):
                result[resource.advq_db][resource.created.date(), 1].append(resource)
        return dict(result)

    resource_data_path = tmpdir.join('resource.data')
    resource_data_path.write('')
    resource_data = mock.MagicMock()
    resource_data.path = pathlib2.PosixPath(resource_data_path.strpath)
    upload_phits_index_to_yt(
        yt_client=yt_client,
        yt_path_template='//root/{dbname}/{phits_type}',
        advq_databases=['rus'],
        advq_phits_type='spikes',
        sandbox_list_dbs=sandbox_list_dbs,
        phits_resource_class_by_chunk={
            'spikes': PhitsResourceMock,
        },
        make_resource_data=lambda _: resource_data,
    )

    assert [c[0][1] for c in yt_client.move.call_args_list] == [
        '//root/rus/spikes/file20170108',  # новый файл
    ]
    assert {tuple(c[0]) for c in yt_client.set_attribute.call_args_list} == {
        ('//root/rus/spikes/file20170108', 'sandbox_resource_id', 777),
        ('//root/rus/spikes/file20170108', 'sandbox_creation_time', '2017-01-08T12:00:00+00:00'),
    }
