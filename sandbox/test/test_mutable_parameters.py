from sandbox.projects.yabs.qa.mutable_parameters import MutableParameters


class TestMutableParameters(object):
    def test_from_dict(self):
        source_dict = {
            'a': 1,
            'b': 'string_value',
            'c': False
        }
        parameters = MutableParameters.__from_dict__(source_dict)
        assert parameters.a == 1
        assert parameters.b == 'string_value'
        assert parameters.c is False

    def test_update(self):
        source_dict = {
            'a': 1
        }
        parameters = MutableParameters.__from_dict__(source_dict)
        assert parameters.a == 1
        update_dict = {
            'a': 2,
            'b': 3
        }
        parameters.__dict__.update(update_dict)
        assert parameters.a == 2
        assert parameters.b == 3

    def test_from_parameters(self):
        source_sequence = [
            ('a', 1),
            ('b', 'string_value'),
            ('c', False)
        ]
        '''
        The above mimics sdk2.Parameters behaviour, as iterating over them
        yields a sequence of name-value 2-tuples.
        '''
        parameters = MutableParameters.__from_parameters__(source_sequence)
        assert parameters.a == 1
        assert parameters.b == 'string_value'
        assert parameters.c is False
