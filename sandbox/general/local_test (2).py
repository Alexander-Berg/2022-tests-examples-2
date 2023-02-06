import os
import sys

import ammo
import tpl_db as tpl_db
from tpl_api_request_definitions import RequestDefinitionService
import request_log_parser


def get_resource(file_name):
    path = os.path.join(os.path.dirname(__file__), file_name)
    with open(path, 'r') as f:
        file_string = f.read()
    return file_string


if __name__ == "__main__":
    user_home = os.getenv("HOME")
    sys.path.append(user_home + '/arc/arcadia')

    resource_id = 2407682595
    resource = get_resource("/path/to/logs/click_out.txt")
    parsed = request_log_parser.parse(resource)

    print("Connecting to db...")
    db = tpl_db.TplDB(
        host='sas-zt4f5oczs9x7x8oj.db.yandex.net',
        username='market_tpl_production',
        password='***',
        dbname='market_tpl_production'
    )
    raw_request_definitions = parsed
    request_definition_service = RequestDefinitionService(db)
    request_definition_service.fill_request_definitions(raw_request_definitions)
    print('Obtained request definitions')
    print("Generating ammo...")
    ammo.generate_ammo(
        host='sas2-5712-be7-sas-market-prep--8e0-17739.gencfg-c.yandex.net:17739',
        request_definitions=raw_request_definitions
    )
    print("Done! Saving...")

    print("Saved!")
