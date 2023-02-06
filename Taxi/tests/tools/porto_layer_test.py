from tools.porto_layer import (
    DEFAULT_PORTO_SCRIPT_TEMPLATE_PATH,
    DEFAULT_PORTO_REQUIREMENTS_PATH,
    DEFAULT_PORTO_SCRIPT_PATH,
)


def test_generated_file():
    with open(
        DEFAULT_PORTO_REQUIREMENTS_PATH,
        'rt',
        encoding='utf-8',
    ) as src, open(
        DEFAULT_PORTO_SCRIPT_TEMPLATE_PATH,
        'rt',
        encoding='utf-8',
    ) as tml, open(
        DEFAULT_PORTO_SCRIPT_PATH,
        'rt',
        encoding='utf-8',
    ) as dst:
        requirements = src.read()
        expected = tml.read().format(python_requirements=requirements)
        actual = dst.read()

        assert (
            actual == expected
        ), 'Porto layer generation scripts mismatch. Run `python3 -m tools.porto_layer generate` to fix'
