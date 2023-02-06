from nile.api.v1 import extractors as ne
from nile.api.v1 import filters as nf


class BaseTest(object):
    def __init__(
            self,
            name,
            extract_test_id,
            extract_value,
            detect_group,
            extract_key
    ):
        if extract_value is None:
            extract_value = 'value'

        if detect_group is None:
            detect_group = 'group'

        if extract_test_id is None:
            self.extract_test_id = ne.const(None).add_hints(type=bool)
            self.use_test_id = False
        else:
            self.extract_test_id = extract_test_id
            self.use_test_id = True

        if extract_key is None:
            self.extract_key = ne.const(None).add_hints(type=bool)
            self.use_key = False
        else:
            self.extract_key = extract_key
            self.use_key = True

        self.name = name
        self.extract_value = extract_value
        self.detect_group = detect_group

    @staticmethod
    def group_validation(group):
        return group is not None and isinstance(group, bool)

    def _to_required_format(self, table, **kwargs):
        return table.project(
            ne.all(),
            test_id=self.extract_test_id,
            group=self.detect_group,
            key=self.extract_key,
            **kwargs
        ).filter(
            nf.custom(self.group_validation, 'group'),
            **kwargs
        ).project(
            'test_id', 'group', 'key',
            value=self.extract_value,
            **kwargs
        )

    def _to_required_output_format(self, table):
        if not self.use_test_id:
            return table.project(ne.all(exclude='test_id'))
        else:
            return table

    def _calc_4_table(self, table):
        raise NotImplementedError()

    def calc_4_table(self, table):
        return self._to_required_output_format(self._calc_4_table(table))

    def calc_4_table_with_name(self, table):
        return self.calc_4_table(table).project(
            ne.all(),
            name=ne.const(self.name).add_hints(type=str)
        )

    def __call__(self, table):
        return self.calc_4_table_with_name(table)
