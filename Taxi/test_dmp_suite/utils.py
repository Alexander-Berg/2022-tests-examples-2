import contextlib
import random


@contextlib.contextmanager
def random_seed(seed):
    """
    Этот контекстный менеджер устанавливает новый seed для генератора случайных чисел
    и восстанавливает прежнее состояние при выходе.

    Может быть полезен, когда тестируется поведение, использующее модуль random,
    а хочется чтобы тест работал стабильно.
    """
    previous_state = random.getstate()

    try:
        random.seed(seed)
        yield
    finally:
        random.setstate(previous_state)
