import os

from balancer_agent.core.db import ServiceDB


def test_service_db():
    ServiceDB.PATH = "service_db"

    try:
        os.remove(ServiceDB.PATH)
    except FileNotFoundError:
        pass

    try:
        os.remove(ServiceDB.PATH + ".db")
    except FileNotFoundError:
        pass

    assert not ServiceDB.exists()
    assert ServiceDB.get_all() == {}

    assert ServiceDB.exists()
    assert not ServiceDB.get("service")

    service_id = 1

    assert not ServiceDB.update(**{"service": service_id})

    assert ServiceDB.get("service") == service_id

    ServiceDB.delete("service")
    # Multiple deletes don't fail
    ServiceDB.delete("service")

    assert not ServiceDB.get("service")

    try:
        os.remove(ServiceDB.PATH)
    except FileNotFoundError:
        pass

    try:
        os.remove(ServiceDB.PATH + ".db")
    except FileNotFoundError:
        pass

    assert not ServiceDB.exists()
    ServiceDB.delete("service")

    try:
        os.remove(ServiceDB.PATH)
    except FileNotFoundError:
        pass

    try:
        os.remove(ServiceDB.PATH + ".db")
    except FileNotFoundError:
        pass
