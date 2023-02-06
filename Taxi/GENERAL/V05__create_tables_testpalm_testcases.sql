CREATE TABLE  eats_automation_statistics.newtests (
    testcase_id VARCHAR(500) NOT NULL,
    snapshot_time NUMERIC NOT NULL,
    created_time NUMERIC,
    status VARCHAR(500),
    is_autotest VARCHAR(500),
    automation_status VARCHAR(500),
    priority VARCHAR(500),
    case_group VARCHAR(500),
    PRIMARY KEY(testcase_id, snapshot_time)
);

CREATE TABLE  eats_automation_statistics.iosclient (
    testcase_id VARCHAR(500) NOT NULL,
    snapshot_time NUMERIC NOT NULL,
    created_time NUMERIC,
    status VARCHAR(500),
    is_autotest VARCHAR(500),
    automation_status VARCHAR(500),
    priority VARCHAR(500),
    case_group VARCHAR(500),
    PRIMARY KEY(testcase_id, snapshot_time)
);
