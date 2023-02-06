import uuid


def test_uuid1():
    for _ in range(1000):
        assert uuid.UUID(bytes=uuid.uuid1().bytes).version == 1


def test_uuid3():
    uuid1 = uuid.uuid1()
    for _ in range(1000):
        assert uuid.UUID(bytes=uuid.uuid3(namespace=uuid1, name='test').bytes).version == 3


def test_uuid4():
    for _ in range(1000):
        assert uuid.UUID(bytes=uuid.uuid4().bytes).version == 4


def test_uuid5():
    uuid1 = uuid.uuid1()
    for _ in range(1000):
        assert uuid.UUID(bytes=uuid.uuid5(namespace=uuid1, name='test').bytes).version == 5
