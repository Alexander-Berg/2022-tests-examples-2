import textwrap
import os
import sys

current_dir_path = os.path.dirname(__file__)
sys.path.append(os.path.join(current_dir_path, os.pardir))

splitter = '// yandex-splitter'

valid_json = textwrap.dedent("""
    {
        "hello": "world"
    }
""").strip()

valid_ugly_json = '{"hello":"world"}'

invalid_json = textwrap.dedent("""
    {
        "hello": "world",
    }
""").strip()

real_response_path = os.path.join(current_dir_path, 'real-response.txt')

try:
    with open(real_response_path, 'r') as real_response_file:
        real_response = real_response_file.read()

except IOError:
    from library.python import resource

    real_response = resource.find(real_response_path)
    if real_response is None:
        raise
