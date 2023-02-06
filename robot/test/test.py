import yatest.common

from robot.jupiter.tools.compare_index.lib.parsers import get_parsers


def test_parser():
    parsers = get_parsers(None)

    output_file_path = yatest.common.output_path("parsed_docs")
    with open(output_file_path, 'w') as out:
        for parser in parsers:
            out.write("--- {} ---\n".format(parser.dump_mode))
            parser.test_parser(out)
            parser.reset()

    return yatest.common.canonical_file(output_file_path)
