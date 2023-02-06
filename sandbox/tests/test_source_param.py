from sandbox.projects.geosearch.tools.source_param import (
    render_experimental_sources_from_yp,
    render_experimental_sources_from_nanny,
)

# result of yp_lite.get_endpoint_sets('addrs_base_d1')
BASE_D1_YP_ENDPOINT_SETS = {
    "SAS": [
        {
            "status": {
                "endpoints": [
                    {
                        "port": 80,
                        "ip6Address": "2a02:6b8:c08:199:0:4a44:f66:0",
                        "protocol": "TCP",
                        "ip4Address": "",
                        "fqdn": "addrs-base-d1-1.sas.yp-c.yandex.net"
                    }
                ]
            },
            "meta": {
                "version": "df636bbf-c4da-4850-a5e1-c7d0ddcff01a",
                "serviceId": "addrs_base_d1",
                "id": "addrs_base_d1-1",
                "ownership": "USER"
            },
            "spec": {
                "protocol": "TCP",
                "port": 80,
                "podFilter": "[/labels/shard_id]=\"1\"",
                "description": "addrs_base_d1 shard 1"
            }
        },
        {
            "status": {
                "endpoints": [
                    {
                        "port": 80,
                        "ip6Address": "2a02:6b8:c08:3a9:0:4a44:bb37:0",
                        "protocol": "TCP",
                        "ip4Address": "",
                        "fqdn": "addrs-base-d1-18.sas.yp-c.yandex.net"
                    }
                ]
            },
            "meta": {
                "version": "71e35cf4-f545-408d-97ca-4f8084a2cc09",
                "serviceId": "addrs_base_d1",
                "id": "addrs_base_d1-18",
                "ownership": "USER"
            },
            "spec": {
                "protocol": "TCP",
                "port": 80,
                "podFilter": "[/labels/shard_id]=\"18\"",
                "description": "addrs_base_d1 shard 18"
            }
        }
    ]
}

# result of nanny.get_isolated_instances('addrs_wizard_p4')
WIZARD_P4_NANNY_INSTANCES = [
    {
        "engine": "",
        "network_settings": "MTN_ENABLED",
        "container_hostname": "addrs-wizard-p4-6.vla.yp-c.yandex.net",
        "hostname": "vla3-3598.search.yandex.net",
        "port": 80,
        "itags": ["a_geo_vla", "a_dc_vla", "a_itype_wizard", "a_ctype_test", "a_prj_addrs-wizard-p4", "a_metaprj_addrs", "a_tier_none", "use_hq_spec", "enable_hq_report", "enable_hq_poll"]
    },
    {
        "engine": "",
        "network_settings": "MTN_ENABLED",
        "container_hostname": "addrs-wizard-p4-7.vla.yp-c.yandex.net",
        "hostname": "vla3-4886.search.yandex.net",
        "port": 80,
        "itags": ["a_geo_vla", "a_dc_vla", "a_itype_wizard", "a_ctype_test", "a_prj_addrs-wizard-p4", "a_metaprj_addrs", "a_tier_none", "use_hq_spec", "enable_hq_report", "enable_hq_poll"]
    }
]


def test_business_from_yp_endpoint_sets():
    sources = render_experimental_sources_from_yp('base', BASE_D1_YP_ENDPOINT_SETS)
    assert sources == [
        'business!addrs-base-000:sd://sas@addrs_base_d1-1',
        'business!addrs-base-017:sd://sas@addrs_base_d1-18',
    ]


def test_wizard_from_nanny_instance_list():
    sources = render_experimental_sources_from_nanny('wizard', WIZARD_P4_NANNY_INSTANCES)
    assert sources == [
        'wizard:addrs-wizard-p4-6.vla.yp-c.yandex.net:80/wizard',
        'wizard:addrs-wizard-p4-7.vla.yp-c.yandex.net:80/wizard',
    ]


def test_metasearch_from_nanny_instance_list():
    # Looks strange, but parent tasks which create betas rely on such behavior
    sources = render_experimental_sources_from_nanny('meta', WIZARD_P4_NANNY_INSTANCES)
    assert sources == [
        'addrs-wizard-p4-6.vla.yp-c.yandex.net:80',
        'addrs-wizard-p4-7.vla.yp-c.yandex.net:80',
    ]
