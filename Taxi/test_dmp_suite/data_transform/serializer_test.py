from dmp_suite.data_transform.serializer import Serializer
from dmp_suite.table import Field
import unittest


class SerializerTest(unittest.TestCase):
    def test_extractors(self):
        fields = [
            Field(name='a'),
            Field(name='b')
        ]

        extractor_1 = lambda data, name: data.get(name)

        def extractor_2(data):
            return data.get('b', 0) + 10

        extractors = dict(a=extractor_1, b=extractor_2)
        serializer = Serializer(fields=fields, field_extractors=extractors)
        data = dict(a=1, b=2)
        serialized = serializer.apply(data)
        self.assertEqual(1, serialized['a'])
        self.assertEqual(12, serialized['b'])

        extractors = dict(b=extractor_2)
        serializer = Serializer(fields=fields,
                                field_extractors=extractors)
        data = dict(a=1, b=2)
        serialized = serializer.apply(data)
        self.assertEqual(1, serialized['a'])
        self.assertEqual(12, serialized['b'])

        extractors = dict(b=extractor_1)
        serializer = Serializer(fields=fields,
                                field_extractors=extractors)
        data = dict(a=1, b=2)
        serialized = serializer.apply(data)
        self.assertEqual(1, serialized['a'])
        self.assertEqual(2, serialized['b'])

        serializer = Serializer(fields=fields,
                                field_extractors=extractors)
        data = dict(a=1, b=2)
        serialized = serializer.apply(data)
        self.assertEqual(1, serialized['a'])
        self.assertEqual(2, serialized['b'])

        serializer = Serializer(fields=fields,
                                field_extractors=extractors)
        data = dict(a=1, b=2)
        serialized = serializer.apply(data)
        self.assertEqual(1, serialized['a'])
        self.assertEqual(2, serialized['b'])

        extractors = dict(c=extractor_1)
        self.assertRaises(ValueError,
                          Serializer,
                          fields=fields,
                          field_extractors=extractors)

        def bad_extractor(a, b, c): pass
        self.assertRaises(ValueError,
                          Serializer,
                          fields=fields,
                          field_extractors=dict(a=bad_extractor))

        def extractor_with_name_defaults(name=None):
            return lambda d, field_name=None: d.get(name or field_name)

        extractors = dict(a=extractor_with_name_defaults())
        serializer = Serializer(fields=fields, field_extractors=extractors)
        self.assertIsNone(serializer.apply(dict(a=1))['a'])

        extractors = dict(b=extractor_with_name_defaults('a'))
        serializer = Serializer(fields=fields, field_extractors=extractors)
        self.assertEqual(1, serializer.apply(dict(a=1))['b'])

    def test_path_extractors(self):
        fields = [
            Field(name='a'),
            Field(name='b')
        ]
        extractors = dict(
            a='b.a',
            b='b.b',
        )
        serializer = Serializer(fields=fields, field_extractors=extractors)
        self.assertEqual(
            serializer.apply(dict(b=dict(a=1, b=2))),
            dict(a=1, b=2),
        )

        fields = [
            Field(name='a.a'),
            Field(name='b.b')
        ]
        serializer = Serializer(fields=fields)
        self.assertEqual(
            serializer.apply(dict(a=dict(a=1), b=dict(b=2))),
            {'a.a': 1, 'b.b': 2},
        )

    def test_not_unique_field_names(self):
        fields = [
            Field(name='a', data_type='b'),
            Field(name='a', data_type='a')
        ]

        self.assertRaises(ValueError, Serializer, fields)
