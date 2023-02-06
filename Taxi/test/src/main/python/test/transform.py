def my_func(s):
    return s.upper()


def func():
    from pyflink.table.udf import udf
    from pyflink.table import DataTypes
    return udf(my_func, result_type=DataTypes.STRING())
