

import datetime
from builtins import map

from app.projects.utils import create_new_project
from app.db.db import new_session
from app.db.models import DebbyProject, DebbyPolicy, DebbyTag
from app.settings import ENGINE_NMAP
from app.utils import timestamp_utc_2_datetime_msk


def test_create_project():

    s = new_session()
    policy = s.query(DebbyPolicy).first()
    tags = s.query(DebbyTag).limit(2).all()
    existing_project = s.query(DebbyProject).limit(2).all()
    s.close()

    assert policy is not None

    tags_ids = list([t.id for t in tags])
    prev_ids = list([p.id for p in existing_project])

    name = 'TEST_NAME'
    target = 'TEST_TARGET'
    engine = ENGINE_NMAP
    policy_id = policy.id
    scan_start = scan_stop = datetime.datetime.now()
    interval = timestamp_utc_2_datetime_msk(0)
    tags_list = tags_ids
    project_prev_pipelines_list = prev_ids
    log_closed = False

    project_id = create_new_project(name, target, engine, policy_id,
                                    scan_start, scan_stop, interval, tags_list,
                                    project_prev_pipelines_list, log_closed)

    assert isinstance(project_id, int)

    session = new_session()
    session.query(DebbyProject).filter(DebbyProject.id == project_id).delete()
    session.commit()
    session.close()
