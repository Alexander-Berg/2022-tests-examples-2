import pytest

import metrika.pylib.deploy.client as deploy
from metrika.pylib.deploy.client import exceptions

CORRECT_STAGE = {
    "annotations": {
        "project": "mtutils-deploy-tests"
    },
    "labels": {
        "deploy_engine": "env_controller"
    },
    "meta": {
        "acl": [{
            "action": "allow",
            "permissions": [
                "read",
                "write",
                "create",
                "ssh_access",
                "root_ssh_access",
                "read_secrets"
            ],
            "subjects": [
                "robot-drug-deploy"
            ]
        }],
        "id": "correct_deploy_stage",
        "inherit_acl": True
    },
    "spec": {
        "deploy_units": {
            "DeployUnit1": {
                "tvm_config": {},
                "endpoint_sets": [
                    {
                        "port": 80
                    }
                ],
                "replica_set": {
                    "replica_set_template": {
                        "pod_template_spec": {
                            "spec": {
                                "disk_volume_requests": [
                                    {
                                        "quota_policy": {
                                            "capacity": 3221225472
                                        },
                                        "labels": {
                                            "used_by_infra": True
                                        },
                                        "id": "okunev-test-stage-disk-0",
                                        "storage_class": "hdd"
                                    }
                                ],
                                "host_infra": {
                                    "monitoring": {}
                                },
                                "ip6_address_requests": [
                                    {
                                        "network_id": "_SEARCHSAND_",
                                        "vlan_id": "backbone",
                                        "enable_dns": True
                                    },
                                    {
                                        "network_id": "_SEARCHSAND_",
                                        "vlan_id": "fastbone",
                                        "enable_dns": True
                                    }
                                ],
                                "resource_requests": {
                                    "memory_limit": 1073741824,
                                    "memory_guarantee": 1073741824,
                                    "vcpu_limit": 100,
                                    "vcpu_guarantee": 100
                                },
                                "pod_agent_payload": {
                                    "spec": {
                                        "boxes": [
                                            {
                                                "id": "Box1",
                                                "rootfs": {
                                                    "layer_refs": [
                                                        "layer-0",
                                                        "layer-1"
                                                    ]
                                                }
                                            }
                                        ],
                                        "workloads": [
                                            {
                                                "id": "Box1-Workload1",
                                                "start": {
                                                    "command_line": "/simple_http_server 80 'Hello!'"
                                                },
                                                "env": [
                                                    {
                                                        "name": "mySuperVariable",
                                                        "value": {
                                                            "literal_env": {
                                                                "value": "mySuperValue"
                                                            }
                                                        }
                                                    }
                                                ],
                                                "box_ref": "Box1",
                                                "transmit_logs": True,
                                                "readiness_check": {
                                                    "tcp_check": {
                                                        "port": 80
                                                    }
                                                }
                                            }
                                        ],
                                        "mutable_workloads": [
                                            {
                                                "workload_ref": "Box1-Workload1"
                                            }
                                        ],
                                        "resources": {
                                            "layers": [
                                                {
                                                    "url": "rbtorrent:edd2795d2d7674eae43c4ad0de3dad563be11f94",
                                                    "checksum": "EMPTY:",
                                                    "id": "layer-0"
                                                },
                                                {
                                                    "url": "rbtorrent:d57bb5d384702469a420e497ac67d8c14986277f",
                                                    "checksum": "EMPTY:",
                                                    "id": "layer-1"
                                                }
                                            ]
                                        }
                                    }
                                }
                            }
                        },
                        "constraints": {
                            "antiaffinity_constraints": [
                                {
                                    "max_pods": 1,
                                    "key": "node"
                                }
                            ]
                        }
                    },
                    "per_cluster_settings": {
                        "sas": {
                            "deployment_strategy": {
                                "max_unavailable": 1
                            },
                            "pod_count": 1
                        }
                    }
                },
                "network_defaults": {
                    "network_id": "_SEARCHSAND_"
                }
            }
        },
        "revision_info": {},
        "account_id": "abc:service:185",
        "revision": 1
    }
}


@pytest.fixture
def deploy_api():
    deploy_api = deploy.DeployAPI(token="fake_token")
    yield deploy_api


def test_wrong_create_stage_parameters(deploy_api):
    with pytest.raises(exceptions.DeployAPINoIDException):
        stage = CORRECT_STAGE
        stage["meta"]["id"] = ""
        deploy_api.stage.create_stage(stage)


def test_wrong_get_stage_specification_parameters(deploy_api):
    with pytest.raises(exceptions.DeployAPINoIDException):
        deploy_api.stage.get_stage_specification(None)


def test_wrong_update_stage_specification_parameters(deploy_api):
    with pytest.raises(exceptions.DeployAPINoIDException):
        deploy_api.stage.update_stage_specification(None)


def test_wrong_remove_stage_parameters(deploy_api):
    with pytest.raises(exceptions.DeployAPINoIDException):
        deploy_api.stage.remove_stage(None)
