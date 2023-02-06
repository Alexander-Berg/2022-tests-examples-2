from sandbox.projects.yabs.qa.tasks.YabsServerFreezeSaasSnapshots import get_new_snapshots_to_freeze, get_old_snapshots_to_freeze


class TestNewSnapshotsToFreeze(object):
    def test_empty(self):
        new = get_new_snapshots_to_freeze([], ["0"])
        assert new == []

    def test_already_frozen(self):
        saas_snapshots = [
            {
                "Status": {"Active": True, "Frozen": True},
                "Meta": {"Id": "shapshot#1", "Stream": "0"}
            },
        ]
        new = get_new_snapshots_to_freeze(saas_snapshots, ["0"])
        assert new == []

    def test_inactive_frozen(self):
        saas_snapshots = [
            {
                "Status": {"Active": False, "Frozen": False},
                "Meta": {"Id": "shapshot#1", "Stream": "0"}
            },
        ]
        new = get_new_snapshots_to_freeze(saas_snapshots, ["0"])
        assert new == []

    def test_new_snapshot(self):
        saas_snapshots = [
            {
                "Status": {"Active": True, "Frozen": False},
                "Meta": {"Id": "shapshot#1", "Stream": "0"}
            },
            {
                "Status": {"Active": True, "Frozen": False},
                "Meta": {"Id": "shapshot#2", "Stream": "1"}
            },
        ]
        new = get_new_snapshots_to_freeze(saas_snapshots, ["0"])
        assert new == [{
            "Status": {"Active": True, "Frozen": False},
            "Meta": {"Id": "shapshot#1", "Stream": "0"},
        }]

    def test_several_new_snapshots(self):
        """ Checks that for one stream will be freezed only one (last and not frozen) snapshot
        """
        saas_snapshots = [
            {
                "Status": {"Active": True, "Frozen": False},
                "Meta": {"Id": "shapshot#1", "Stream": "0"}
            },
            {
                "Status": {"Active": True, "Frozen": False},
                "Meta": {"Id": "shapshot#2", "Stream": "0"}
            },
        ]
        new = get_new_snapshots_to_freeze(saas_snapshots, ["0"])
        assert new == [{
            "Status": {"Active": True, "Frozen": False},
            "Meta": {"Id": "shapshot#2", "Stream": "0"},
        }]

    def test_new_snapshots_several_streams(self):
        saas_snapshots = [
            {
                "Status": {"Active": True, "Frozen": False},
                "Meta": {"Id": "shapshot#1", "Stream": "0"}
            },
            {
                "Status": {"Active": True, "Frozen": False},
                "Meta": {"Id": "shapshot#2", "Stream": "1"}
            },
        ]
        new = get_new_snapshots_to_freeze(saas_snapshots, ["0", "1"])
        assert new == [
            {
                "Status": {"Active": True, "Frozen": False},
                "Meta": {"Id": "shapshot#2", "Stream": "1"}
            },
            {
                "Status": {"Active": True, "Frozen": False},
                "Meta": {"Id": "shapshot#1", "Stream": "0"}
            },
        ]


class TestOldSnapshotsToFreeze(object):
    def test_empty(self):
        old = get_old_snapshots_to_freeze([], [])
        assert old == []

    def test_old_snapshots(self):
        saas_snapshots = [
            {
                "Status": {"Active": True, "Frozen": True},
                "Meta": {"Id": "shapshot#1", "Stream": "0"}
            },
        ]
        active_snapshot_metas = [
            ("0", "shapshot#1")
        ]
        old = get_old_snapshots_to_freeze(saas_snapshots, active_snapshot_metas)
        assert old == saas_snapshots

    def test_old_snapshots_absent_in_saas(self):
        saas_snapshots = [
            {
                "Status": {"Active": True, "Frozen": True},
                "Meta": {"Id": "shapshot#1", "Stream": "0"}
            },
        ]
        active_snapshot_metas = [
            ("0", "shapshot#2"),
            ("1", "shapshot#1"),
        ]
        old = get_old_snapshots_to_freeze(saas_snapshots, active_snapshot_metas)
        assert old == []
