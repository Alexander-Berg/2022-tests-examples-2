from dataclasses import dataclass

from pyspark import SparkConf
from pyspark.java_gateway import launch_gateway
from pytest_socket import enable_socket, disable_socket

from dmp_suite.func_utils import lru_cache
from dmp_suite.spark.client import _prepare_jars
from dmp_suite.spark.files import DevelopSparkUDFJar
from dmp_suite.spark.udf import UDFColumn
from init_py_env import service


def get_develop_jar_path(service):
    return _prepare_jars([DevelopSparkUDFJar(service)])


@lru_cache(1)
def get_gateway():
    conf = SparkConf()
    conf.set('spark.jars', get_develop_jar_path(service))
    conf.set('spark.ui.enabled', False)
    return launch_gateway(conf=conf)


@dataclass
class Status:
    jvm_class: str
    udf_name: str
    code: int
    message: str

    @property
    def valid(self) -> bool:
        return self.code == 0


def _validate_udf(gateway, jvm_class, udf_name):
    validate_udf = gateway.jvm.dmp_suite.py2j.ValidationUtils.validateUdf
    code = validate_udf(jvm_class, udf_name)
    msg = _get_message_mapping()[code]
    return Status(jvm_class, udf_name, code, msg)


def _validate_class(gateway, jvm_class):
    validate_class = gateway.jvm.dmp_suite.py2j.ValidationUtils.validateClass
    code = validate_class(jvm_class)
    msg = _get_message_mapping()[code]
    return Status(jvm_class, None, code, msg)


@lru_cache(1)
def _get_message_mapping():
    gw = get_gateway()
    return gw.jvm.dmp_suite.py2j.ValidationUtils.Status.mapping()


def assert_udf_method(jvm_class, udf_name):
    status = _validate_udf(get_gateway(), jvm_class, udf_name)
    assert status.valid, status.message


def assert_udf(udf_holder):
    try:
        # поднятие java gateway требует socket
        # разрешаем сокет, чтобы можно было использовать в юнит тестах
        enable_socket()
        gw = get_gateway()
        jvm_class = udf_holder.__jvm_class__

        class_status = _validate_class(gw, jvm_class)
        assert class_status.valid, f'{jvm_class}: {class_status.message}'

        udf_methods = [
            f for f in vars(udf_holder).values() if isinstance(f, UDFColumn)
        ]
        assert udf_methods
        invalid_status = []

        for udf in udf_methods:
            status = _validate_udf(gw, jvm_class, udf.name)
            if not status.valid:
                invalid_status.append(status)


        assert not invalid_status, \
            f'Invalid udf:\n' + '\n'.join(
                f'{s.jvm_class}.{s.udf_name}: {s.message}' for s in invalid_status
            )
    finally:
        disable_socket()
