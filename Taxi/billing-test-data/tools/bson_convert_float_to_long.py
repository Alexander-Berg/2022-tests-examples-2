import decimal
import sys

import bson


def convert_float_to_int(data_in):
    if isinstance(data_in, dict):
        for key in data_in:
            data_in[key] = convert_float_to_int(data_in[key])
    elif isinstance(data_in, list):
        data_in = list(map(convert_float_to_int, data_in))
    elif isinstance(data_in, float):
        value = decimal.Decimal(data_in)
        if value % 1 == 0:
            data_in = bson.Int64(value)
    return data_in


def main():
    with open(sys.argv[1], 'br+') as fp:
        data = bson.decode_all(fp.read())
        data = convert_float_to_int(data)
        fp.truncate()
        fp.flush()
        fp.seek(0)
        for doc in data:
            fp.write(bson.BSON.encode(doc))
            fp.flush()


main()
