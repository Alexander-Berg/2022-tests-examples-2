from metrika.admin.python.mtapi.lib.test_utils import dump_response


def test_ping(client):
    response = client.get("/eventstat/ping")

    dump_response(response)

    assert response.status_code == 200
