import os

from library.python import resource
import yt.wrapper as ytw
import yt.yson as yson

from sandbox.projects.yabs.export_keywords_from_proto_to_yt.main import main, SNAPSHOTS_DIRECTORY_NAME, \
    SNAPSHOT_VERSION_DELIMITER


class FakeSandboxTask:
    def __init__(self, task_id):
        self.id = task_id

    def set_info(self, *__, **___):
        pass


def do_export(tables_dir, should_create_new_snapshot=True, should_change_links=True, snapshot_id="", sb_task=None):
    SCHEMA_RESOURCE_NAMES = (
        ("Keyword", "sandbox/projects/yabs/export_keywords_from_proto_to_yt/Keyword-schema.yson"),
        ("KeywordType", 'sandbox/projects/yabs/export_keywords_from_proto_to_yt/KeywordType-schema.yson'),
        ("KeywordDataType", 'sandbox/projects/yabs/export_keywords_from_proto_to_yt/KeywordDataType-schema.yson'),
    )
    schemas_by_table_name = {}
    for table_name, resource_name in SCHEMA_RESOURCE_NAMES:
        schema_resource_data = resource.find(resource_name)
        schema = yson.loads(schema_resource_data)
        schemas_by_table_name[table_name] = schema
    tables_path = f"//tmp/{tables_dir}"
    snapshots_path = f"{tables_path}/{SNAPSHOTS_DIRECTORY_NAME}"
    if not ytw.exists(snapshots_path):
        ytw.create("map_node", snapshots_path, recursive=True)
    if sb_task is None:
        sb_task = FakeSandboxTask(1337)
    main(schemas_by_table_name,
         [os.environ.get("YT_PROXY")],
         tables_path,
         snapshot_id=snapshot_id,
         should_create_new_snapshot=should_create_new_snapshot,
         should_change_links=should_change_links,
         sandbox_task=sb_task)


def test_non_full_modes():
    tables_dir = "partial-modes"
    tables_path = f"//tmp/{tables_dir}"
    snapshots_path = f"{tables_path}/{SNAPSHOTS_DIRECTORY_NAME}"
    do_export(tables_dir, snapshot_id="100500")
    nodes = set(ytw.list(snapshots_path))
    assert len(nodes) > 0
    for node in nodes:
        assert node.endswith(f"{SNAPSHOT_VERSION_DELIMITER}100500")

    # Test create only
    do_export(tables_dir, should_change_links=False, sb_task=FakeSandboxTask(200500))
    new_nodes = set(ytw.list(snapshots_path))
    assert len(new_nodes) == len(nodes) * 2
    for node in new_nodes - nodes:
        assert node.endswith(f"{SNAPSHOT_VERSION_DELIMITER}200500")
    assert ytw.get(f"{tables_path}/Keyword&/@target_path").endswith(f"{SNAPSHOT_VERSION_DELIMITER}100500")  # noqa
    assert ytw.get(f"{tables_path}/KeywordType&/@target_path").endswith(f"{SNAPSHOT_VERSION_DELIMITER}100500")  # noqa
    assert ytw.get(f"{tables_path}/KeywordDataType&/@target_path").endswith(f"{SNAPSHOT_VERSION_DELIMITER}100500")  # noqa

    do_export(tables_dir, should_change_links=False, sb_task=FakeSandboxTask(300500))

    # Test change links only
    nodes = set(ytw.list(snapshots_path))
    do_export(tables_dir, should_create_new_snapshot=False, snapshot_id="300500")
    assert ytw.get(f"{tables_path}/Keyword&/@target_path").endswith(f"{SNAPSHOT_VERSION_DELIMITER}300500")  # noqa
    assert ytw.get(f"{tables_path}/KeywordType&/@target_path").endswith(f"{SNAPSHOT_VERSION_DELIMITER}300500")  # noqa
    assert ytw.get(f"{tables_path}/KeywordDataType&/@target_path").endswith(f"{SNAPSHOT_VERSION_DELIMITER}300500")  # noqa
    new_nodes = set(ytw.list(snapshots_path))
    assert nodes == new_nodes  # Check that no new snapshots were created when not requested

    assert len(list(ytw.read_table(f"{tables_path}/Keyword"))) > 0
