DROP SCHEMA IF EXISTS clownductor;
CREATE SCHEMA clownductor;

--
-- Types
--

CREATE TYPE CLUSTER_TYPE AS ENUM (
    'conductor',
    'nanny',
    'postgres'
);

CREATE TYPE ENVIRONMENT_TYPE AS ENUM (
    'unstable',
    'testing',
    'prestable',
    'stable'
);

--
-- Projects
--

CREATE TABLE clownductor.projects (
    -- just an id
    id SERIAL UNIQUE PRIMARY KEY,
    -- name of the project
    name TEXT NOT NULL,
    -- network for all non-production branches
    network_testing TEXT NOT NULL,
    -- network for all production branches
    network_stable TEXT NOT NULL,
    -- ABC-service slug associated with all services inside the project
    service_abc TEXT NOT NULL,
    -- ABC-service slug containing YP quota for all services inside the project
    yp_quota_abc TEXT NOT NULL,
    -- ABC-service slug with all tvm subservices
    tvm_root_abc TEXT NOT NULL,

    UNIQUE (name)
);

--
-- Services
--

CREATE TABLE clownductor.services (
    -- just an id
    id SERIAL UNIQUE PRIMARY KEY,
    -- part of what project this service is
    project_id INTEGER REFERENCES
        clownductor.projects (id) ON DELETE CASCADE,
    -- name of the service
    name TEXT NOT NULL,
    -- if this service started to receive production traffic
    production_ready BOOLEAN DEFAULT FALSE,
    -- what we want to deploy here (usually docker image name)
    artifact_name TEXT NOT NULL,
    -- what type of cluster we have here (nanny, conductor, postgres, etc.)
    cluster_type CLUSTER_TYPE NOT NULL,
    -- path to the wiki page with service description
    wiki_path TEXT DEFAULT NULL,
    -- path to the repo where the source code lives
    repo_path TEXT DEFAULT NULL,
    -- ABC-service associated with this service
    abc_service TEXT DEFAULT NULL,
    -- ABC-service with test tvm
    tvm_testing_abc_service TEXT DEFAULT NULL,
    -- ABC-service with stable tvm
    tvm_stable_abc_service TEXT DEFAULT NULL,
    -- StarTrek task where this service was developed
    st_task TEXT NOT NULL,
    -- direct link to service in nanny/conductor/whatever
    direct_link TEXT DEFAULT NULL,

    UNIQUE (project_id, name)
);

CREATE INDEX clownductor_services_project_id_cluster_type
    ON clownductor.services (project_id, cluster_type);

--
-- Branches
--

CREATE TABLE clownductor.branches (
    -- just an id
    id SERIAL UNIQUE PRIMARY KEY,
    -- part of what service this branch is
    service_id INTEGER REFERENCES
        clownductor.services (id) ON DELETE CASCADE,
    -- name of the branch
    name TEXT NOT NULL,
    -- environment type
    env ENVIRONMENT_TYPE NOT NULL DEFAULT 'unstable',
    -- direct link to the cluster (at condector, nanny, pgaas, etc.)
    direct_link TEXT DEFAULT NULL,
    -- version of the artifact currently deployed to this branch
    artifact_version TEXT DEFAULT NULL,

    UNIQUE (service_id, name)
);

--
-- Hosts
--

CREATE TABLE clownductor.hosts (
    -- fqdn of the host
    name TEXT NOT NULL UNIQUE PRIMARY KEY,
    -- part of what branch this host is
    branch_id INTEGER REFERENCES
        clownductor.branches (id) ON DELETE CASCADE,
    -- datacenter name
    datacenter TEXT NOT NULL,
    -- parent host if it is virtual machine
    dom0_name TEXT DEFAULT NULL,
    -- when dom0 was determined
    dom0_updated_at INTEGER DEFAULT NULL
);

CREATE INDEX clownductor_hosts_dom0_name
    ON clownductor.hosts (dom0_name);
CREATE INDEX clownductor_hosts_datacenter
    ON clownductor.hosts (datacenter);
CREATE INDEX clownductor_hosts_branch_id
    ON clownductor.hosts (branch_id);

--
-- Task Processing
--

DROP SCHEMA IF EXISTS task_manager;
CREATE SCHEMA task_manager;

--
-- Types
--

CREATE TYPE JOB_STATUS AS ENUM (
    'in_progress',
    'success',
    'failed',
    'canceled'
);

--
-- Jobs
--

CREATE TABLE task_manager.jobs (
    -- just a unique identifier
    id SERIAL UNIQUE PRIMARY KEY,
    -- service id associated with the job
    service_id INTEGER NOT NULL REFERENCES
        clownductor.services (id) ON DELETE CASCADE,
    -- branch id associated with the job (or null for service-level jobs)
    branch_id INTEGER DEFAULT NULL REFERENCES
        clownductor.branches (id) ON DELETE CASCADE,
    -- name of the recipe
    name TEXT,
    -- login of the author
    initiator TEXT,
    -- current job status
    status JOB_STATUS DEFAULT 'in_progress'::JOB_STATUS,
    -- creation time
    created_at INTEGER DEFAULT EXTRACT (epoch FROM NOW()),
    -- reason for error or cancelation
    error_message TEXT DEFAULT NULL,
    -- finish time
    finished_at INTEGER DEFAULT NULL
);

CREATE INDEX task_manager_jobs_service_id_branch_id
    ON task_manager.jobs (service_id, branch_id);
CREATE INDEX task_manager_jobs_status
    ON task_manager.jobs (status);

-- Variables are updated on almost every step of the job processing.
-- Since each update relocates the row and all indexes should be updated,
-- let's make separate table for this data with only one index.
-- (Also it just seems a bit wrong to me, though currently I don't know how
--  to make right, so making this part separate makes me feel a bit better.)
CREATE TABLE task_manager.job_variables (
    -- job id associated with these variables
    job_id INTEGER UNIQUE NOT NULL REFERENCES
        task_manager.jobs (id) ON DELETE CASCADE,
    -- json-encoded dict variables
    variables TEXT NOT NULL DEFAULT '{}'
);

--
-- Tasks
--

CREATE TABLE IF NOT EXISTS task_manager.tasks (
    -- just a unique identifier
    id SERIAL UNIQUE PRIMARY KEY,
    -- what job this task belongs to
    job_id INTEGER NOT NULL REFERENCES
        task_manager.jobs (id) ON DELETE CASCADE,
    -- name of the cube used for this task
    name TEXT NOT NULL,
    -- until what time we do not want to pay attention to this task
    sleep_until INTEGER DEFAULT 0,
    -- json-encoded mapping of the job variables to task's variables
    input_mapping TEXT,
    -- json-encoded mapping of the task payload content to job variables
    output_mapping TEXT,
    -- arbitrary json-encoded data used as a task state
    payload TEXT DEFAULT '{}',
    -- amount of successive retries made because of internal errors
    retries INTEGER DEFAULT 0,
    -- status of the task
    status JOB_STATUS DEFAULT 'in_progress'::JOB_STATUS,
    -- reason for error or cancelation
    error_message TEXT DEFAULT NULL,
    -- unix-timestamp of creation time
    created_at INTEGER DEFAULT EXTRACT (epoch FROM NOW()),
    -- unix-timestamp of last update time
    updated_at INTEGER DEFAULT NULL
);

CREATE INDEX task_manager_tasks_job_id
    ON task_manager.tasks (job_id);
CREATE INDEX task_manager_tasks_sleep_until_status
    ON task_manager.tasks (status, sleep_until);

CREATE TABLE IF NOT EXISTS task_manager.task_deps (
    -- identifier of the "previous" task
    prev_task_id INTEGER NOT NULL REFERENCES
        task_manager.tasks (id) ON DELETE CASCADE,
    -- identifier of the "next" task
    next_task_id INTEGER NOT NULL REFERENCES
        task_manager.tasks (id) ON DELETE CASCADE,

    UNIQUE (prev_task_id, next_task_id)
);
