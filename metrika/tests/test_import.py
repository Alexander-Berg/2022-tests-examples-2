import metrika.admin.python.logpusher.utils as lpu
import metrika.admin.python.logpusher.utils.utils as lpuu


def test_import():
    b = lpu.escape_array([b"a", b"b"])
    lpuu.convert_list_to_binary_data([[b]])
