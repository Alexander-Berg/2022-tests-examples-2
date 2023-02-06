# -*- coding: utf-8 -*-

from datetime import (
    datetime,
    timedelta,
)
import os
import uuid

from passport.backend.profile.utils.helpers import to_date_str


PREFIX = '//tmp/passport-profile/test'


def create_table_from_path(yt, original_path, target_path, extra_attributes):
    attributes = yt.list(original_path + "/@")
    node = yt.get(original_path, attributes=attributes)

    target_attributes = {}
    for attribute in ('_format', '_read_schema'):
        if attribute in node.attributes:
            target_attributes[attribute] = node.attributes[attribute]

    target_attributes.update(extra_attributes)
    yt.create('table', target_path, attributes=target_attributes, recursive=True)


def create_temp_tree(yt, tables):
    base_path = os.path.join(PREFIX, str(uuid.uuid4()))

    yt.mkdir(base_path, recursive=True)

    for table in tables:
        date = table.get('date', to_date_str(datetime.today()))
        if 'target_path' in table:
            target_path = os.path.join(base_path, table['target_path'].strip('/'), date)
        else:
            target_path = os.path.join(base_path, table['original_path'].strip('/'), date)
        create_table_from_path(
            # В качестве исходной берем достаточно свежую таблицу, из которой получаем только метаданные
            yt=yt,
            original_path=os.path.join(table['original_path'], to_date_str(datetime.today() - timedelta(days=5))),
            target_path=target_path,
            extra_attributes=table.get('attributes', {}),
        )
        yt.write_table(target_path, table['rows'], raw=False)

    return base_path


class YtTestWrapper(object):
    def __init__(self, yt, tables):
        self.yt = yt
        self.tables = tables

    def start(self):
        self.base_path = create_temp_tree(self.yt, self.tables)

    def stop(self):
        pass

    def wrap_path(self, path):
        return os.path.join(self.base_path, path.strip('/'))
