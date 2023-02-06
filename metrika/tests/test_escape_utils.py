import metrika.pylib.escape_utils as mteu


def test_escape_string():
    s = b"asd\tq'w\nasd\\a"

    assert mteu.escape_string(s) == b"asd\\tq\\'w\\nasd\\\\a"


def test_list_to_string():
    l = [b"asd", b"\tqwe", b"w'z", b","]

    assert mteu.list_to_string(l) == b"['asd','\\tqwe','w\\'z',',']"
