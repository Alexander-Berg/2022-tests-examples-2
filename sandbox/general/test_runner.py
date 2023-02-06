import unittest

from runner import external_cdict_mapper


class TestRunner(unittest.TestCase):
    def test_mapper(self):
        namespace = 'ns1'
        mapper = external_cdict_mapper(namespace)
        in_records = [
            {'key': '1', 'subkey': '', 'value': 'text1 ~0:0.5:123\ttext11:1:777'},  # correct
            {'key': '2', 'subkey': '22', 'value': 'text2 ~0:0.6:1234'},  # some value in subkey, still correct
            {'key': '1', 'value': 'text3 ~0:0.3:234'},  # no subkey, still correct
            {'key': 'bannerid', 'value': 'correct text:1:1'},  # incorrect key
            {'key': '', 'value': 'correct text2:1:1'},  # incorrect key
            {'key': '1', 'value': 'comma,is,prohibited:1:3'},  # comma is not allowed
        ]

        expected_out_tuples = [
            ('1', 'text1 ~0:0.5:123,text11:1:777'),
            ('2', 'text2 ~0:0.6:1234'),
            ('1', 'text3 ~0:0.3:234'),
        ]
        expected_out_records = [
            {'cdict_namespace': namespace, 'cdict_key': _[0], 'cdict_value': _[1]} for _ in expected_out_tuples
        ]

        out_records = [out for rec in in_records for out in mapper(rec)]
        self.assertEqual(expected_out_records, out_records)


if __name__ == '__main__':
    unittest.main()
