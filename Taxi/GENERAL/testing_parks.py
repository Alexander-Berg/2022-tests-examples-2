import logging

from taxi.core import async
from taxi.core import db

from taxi.external import billing


logger = logging.getLogger()


@async.inline_callbacks
def main():
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    logger.addHandler(handler)

    parks = yield db.parks.find().run()

    for park_doc in parks:
        email = park_doc.get('email', '')
        operator_uid = '344720065'  # my production id
        billing_client_id = yield billing.create_partner(
            operator_uid, '', park_doc.get('name'), email, park_doc['phone']
        )
        print park_doc['_id'], billing_client_id

if __name__ == '__main__':
    main()
