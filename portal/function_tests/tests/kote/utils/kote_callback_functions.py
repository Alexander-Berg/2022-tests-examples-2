def HOME_77872_callback_example(response, test_path):
    assert response['logic']['int'] == 1, 'Failed on callback function HOME_77872_callback_example\nFailed on test {}'.format(test_path)
