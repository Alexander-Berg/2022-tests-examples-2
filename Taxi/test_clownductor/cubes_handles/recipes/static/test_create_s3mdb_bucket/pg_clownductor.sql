INSERT INTO clownductor.namespaces ("name",created_at,updated_at,deleted_at,is_deleted) VALUES
	 ('taxi','2021-08-11 13:25:36.499397','2021-08-11 13:25:36.499397',NULL,false),
	 ('lavka','2021-08-11 13:25:36.499397','2021-08-11 13:25:36.499397',NULL,false),
	 ('eda','2021-08-11 13:25:36.499397','2021-08-11 13:25:36.499397',NULL,false),
	 ('market','2021-08-11 13:26:43.395513','2021-08-11 13:26:43.395513',NULL,false),
	 ('finservices','2021-08-11 13:26:48.351124','2021-08-11 13:26:48.351124',NULL,false),
	 ('search_portal','2021-08-11 13:26:53.388831','2021-11-22 15:01:35.615142',NULL,false);

INSERT INTO clownductor.projects (
    "id",
    "name",
    network_testing,
    network_stable,
    service_abc,
    yp_quota_abc,
    tvm_root_abc,
    owners,
    env_params,
	approving_managers,
	approving_devs,
	pgaas_root_abc,
	responsible_team,
	yt_topic,
	deleted_at,
	namespace_id
) VALUES (
    '37',
    'taxi-efficiency',
	'_TAXITESTNETS_',
	'_HWTAXINETS_',
	'quotastaxiefficiency',
	'quotastaxiefficiency',
	'taxitvmaccess',
	'{
        "groups": ["svc_vopstaxi"],
	    "logins": [
            "eatroshkin",
	        "sgrebenyukov",
            "nikkraev",
            "oxcd8o",
            "sokogen",
            "nikslim",
            "isharov"
        ]
    }',
	'{
        "stable": {
            "domain": "taxi.yandex.net",
	        "juggler_folder": "taxi.efficiency.prod"
        },
	    "general": {
            "project_prefix": "taxi",
            "docker_image_tpl": "taxi/{{ service }}/$"
        },
	    "testing": {
            "domain": "taxi.tst.yandex.net",
	    "juggler_folder": "taxi.efficiency.test"
        },
	    "unstable": {
            "domain": "taxi.dev.yandex.net"
        }
    }',
	'{
        "logins": [],
	    "cgroups": [352]
    }',
	'{
        "logins": [],
	    "cgroups": [352,493]
    }',
	'quotastaxiefficiency',
	'{
        "ops": ["yandex_distproducts_browserdev_mobile_taxi_mnt"],
	    "managers": [],
	    "developers": [],
	    "superusers": ["isharov",
	    "nikslim"]
    }',
	'{
        "path": "taxi/taxi-access-log",
	    "permissions": ["WriteTopic"]
    }',
	NULL,
	1
);

INSERT INTO clownductor.services (
    id,
    project_id,
    "name",
    production_ready,
    artifact_name,
    "cluster_type",
    wiki_path,
    abc_service,
    tvm_testing_abc_service,
    tvm_stable_abc_service,
    direct_link,
    new_service_ticket,
    requester,
    design_review_ticket,
    service_url,
    deleted_at,
    idempotency_token,
    created_at
) VALUES
	 (355218,
      37,
     'document-templator',
     false,
     'taxi/document-templator/$',
     'nanny'::cluster_type,
     'https://wiki.yandex-team.ru/taxi/backend/architecture/document-templator/',
     'taxidocumenttemplator',
     'taxidocumenttemplator',
     'taxidocumenttemplator',
     'taxi_document-templator',
     'TAXIADMIN-21701',
     'berenda',
     'https://st.yandex-team.ru/TAXIARCHREVIEW-518',
     'https://a.yandex-team.ru/arc_vcs/taxi/backend-py3/services/document-templator/service.yaml',
     NULL,
     NULL,
     1611069487
    );
