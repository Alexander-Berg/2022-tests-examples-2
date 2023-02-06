

from app.tasks.utils import save_events_to_db, get_events_from_db
from app.db.db import new_session
from app.db.models import DebbyScan
from app.settings import STATE_FINISHED


def test_save_get():
    s = new_session()

    scan = DebbyScan(state=STATE_FINISHED, all_targets_tasked=True)
    s.add(scan)
    s.commit()
    scan_id = scan.id
    s.close()

    events = [
        {
            "protocol": "ipv4",
            "event_type": "info",
            "tags": [
                "INTERNAL",
                "IPv4",
                "IPv6"
            ],
            "projectName": "test_test_test",
            "logClosed": False,
            "taskId": 964,
            "transport": "tcp",
            "dest_port": 22,
            "scanId": scan_id,
            "scanStartTime": 1541678338,
            "enabled": True,
            "portState": "open",
            "time": 1541678339,
            "dest_ip": "5.255.255.5",
            "service_name": "SSH",
            "service_product": "",
            "service_version": None,
            "scripts": {
                "banner": "SSH_BANNER",
                "banner1": "SSH_BANNER1"
            }
        },
        {
            "protocol": "ipv4",
            "event_type": "info",
            "tags": [
                "INTERNAL",
                "IPv4",
                "IPv6"
            ],
            "projectName": "test_test_test",
            "logClosed": False,
            "taskId": 964,
            "transport": "tcp",
            "dest_port": 22,
            "scanId": scan_id,
            "scanStartTime": 1541678338,
            "enabled": True,
            "portState": "open",
            "time": 1541678339,
            "dest_ip": "5.255.255.5",
            "service_name": None,
            "service_product": None,
            "service_version": None,
            "scripts": {}
        },
    ]

    expected = [
        {
            "transport": "tcp",
            "dest_port": 22,
            "scanId": scan_id,
            "enabled": True,
            "portState": "open",
            "time": 1541678339,
            "dest_ip": "5.255.255.5",
            "service_name": "SSH",
            "service_product": "",
            "service_version": None,
            "scripts": {
                "banner": "SSH_BANNER",
                "banner1": "SSH_BANNER1"
            }
        },
        {
            "transport": "tcp",
            "dest_port": 22,
            "scanId": scan_id,
            "enabled": True,
            "portState": "open",
            "time": 1541678339,
            "dest_ip": "5.255.255.5",
            "service_name": None,
            "service_product": None,
            "service_version": None,
            "scripts": {}
        },
    ]

    save_events_to_db(events)
    res_events = get_events_from_db(scan_id)

    assert res_events == expected
