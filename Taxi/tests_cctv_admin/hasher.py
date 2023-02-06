# pylint: disable=C0103
import base64
import hashlib
import hmac


TEST_TICKET_HASH_KEY = base64.b64decode(b'MTIzNHF3ZXJhc2Rmenhjdg==')


def hash_ticket(ticket):
    return (
        hmac.new(TEST_TICKET_HASH_KEY, ticket, hashlib.sha256)
        .hexdigest()
        .encode('utf-8')
    )
