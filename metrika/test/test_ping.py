import logging

logger = logging.getLogger(__name__)


def test_ping(client):
    response = client.get("/ping")

    logger.info("Response headers:\n{}".format(response.headers))

    assert b"OK" == response.data
