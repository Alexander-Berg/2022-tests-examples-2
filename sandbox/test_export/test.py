import json

import library.python.resource as resource
import yatest.common
import yt.wrapper as yt
import yt.yson as yson

from sandbox.projects.tycoon.TycoonAdverts.generate_adverts import main, parse_arguments


# read content from existing table on yt:
#  ya tool yt --proxy hahn read-table '//home/geoadv/geoprod_backend/integration_test/export/smvp_campaign_adv_org' --format '<encode_utf8=%false>json'
# read schema of existing table on yt:
#  ya tool yt --proxy hahn get --format '<encode_utf8=%false>json' '//home/geoadv/geoprod_backend/integration_test/export/smvp_campaign_adv_org/@schema'
def create_input_table(cluster, path, resource_name, schema):
    cluster.create(
        type='table',
        path=path,
        ignore_existing=True,
        attributes={
            'schema': schema
        }
    )
    res = resource.find(resource_name)
    cluster.write_table(path, map(json.loads, filter(lambda x: bool(x), res.split('\n'))))


class TestExport(object):

    def test_diff_xml(self):
        hahn = yt.YtClient(proxy='hahn')

        create_input_table(
            cluster=hahn,
            path='//home/geoadv/geoprod_backend/integration_test/export/campaign_owned_organizations',
            resource_name='/test_diff_xml/campaign_owned_organizations.jsonl',
            schema=yson.YsonList([
                {'name': 'campaign_id', 'type': 'int64', 'required': False},
                {'name': 'permanent_id', 'type': 'int64', 'required': False},
            ]))
        create_input_table(
            cluster=hahn,
            path='//home/geoadv/geoprod_backend/integration_test/export/smvp_latest_moderated_advert',
            resource_name='/test_diff_xml/smvp_latest_moderated_advert.jsonl',
            schema=yson.YsonList([
                {"name": "active", "required": False, "type": "boolean",
                 "type_v3": {"type_name": "optional", "item": "bool"}},
                {"name": "body", "required": False, "type": "any",
                 "type_v3": {"type_name": "optional", "item": "yson"}},
                {"name": "campaign_id", "required": False, "type": "int64",
                 "type_v3": {"type_name": "optional", "item": "int64"}},
                {"name": "id", "required": False, "type": "int64",
                 "type_v3": {"type_name": "optional", "item": "int64"}},
                {"name": "name", "required": False, "type": "string",
                 "type_v3": {"type_name": "optional", "item": "string"}},
                {"name": "type", "required": False, "type": "any",
                 "type_v3": {"type_name": "optional", "item": "yson"}},
                {"name": "version_id", "required": False, "type": "int64",
                 "type_v3": {"type_name": "optional", "item": "int64"}}
            ]))
        create_input_table(
            cluster=hahn,
            path='//home/geoadv/geoprod_backend/integration_test/export/smvp_campaign_adv_org',
            resource_name='/test_diff_xml/smvp_campaign_adv_org.jsonl',
            schema=yson.YsonList([
                {"name": "advert_id", "required": False, "type": "int64",
                 "type_v3": {"type_name": "optional", "item": "int64"}},
                {"name": "campaign_id", "required": False, "type": "int64",
                 "type_v3": {"type_name": "optional", "item": "int64"}},
                {"name": "partner_links_disabled", "required": False, "type": "boolean",
                 "type_v3": {"type_name": "optional", "item": "bool"}},
                {"name": "permalink", "required": False, "type": "int64",
                 "type_v3": {"type_name": "optional", "item": "int64"}},
                {"name": "priority_disabled", "required": False, "type": "boolean",
                 "type_v3": {"type_name": "optional", "item": "bool"}},
                {"name": "priority_disabled_in_flight", "required": True, "type": "boolean",
                 "type_v3": "bool"},
                {"name": "priority_poi_disabled", "required": False, "type": "boolean",
                 "type_v3": {"type_name": "optional", "item": "bool"}},
                {"name": "type", "required": False, "type": "any", "type_v3": {"type_name": "optional", "item": "yson"}}
            ]))

        output_path = yatest.common.output_path()
        param = [output_path, "-ni", "-se", "integration_test", "-de", "integration_test"]
        main(parse_arguments(param))
        output_file = output_path + "/ads.xml"
        return yatest.common.canonical_file(output_file, local=True)
