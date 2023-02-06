def test_main_returns_hello_world():
    from src.hello import main as hello_test
    assert hello_test() == 'hello world'
