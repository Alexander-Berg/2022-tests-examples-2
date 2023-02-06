from __future__ import unicode_literals

import time

from sandbox.projects.sandbox.build_sandbox import BuildSandbox


def test_cannot_release():
    now = int(time.time())

    start_event = now - 15 * 60
    end_event = now + 15 * 60
    check_dc = BuildSandbox.check_for_dc_drills(start_event, end_event)

    assert check_dc.description == "There are DC drills right now!"
    assert not check_dc.can_release

    start_event = now + 10 * 60
    end_event = now + 30 * 60
    check_dc = BuildSandbox.check_for_dc_drills(start_event, end_event)

    assert check_dc.description == "There are DC drills less than 30 minutes!"
    assert not check_dc.can_release


def test_can_release():
    now = int(time.time())

    start_event = now - 40 * 60
    end_event = now - 30 * 60
    check_dc = BuildSandbox.check_for_dc_drills(start_event, end_event)

    assert check_dc.description == "There are no DC drills."
    assert check_dc.can_release

    start_event = now + 3 * 60 * 60
    end_event = now + 6 * 60 * 60
    check_dc = BuildSandbox.check_for_dc_drills(start_event, end_event)

    assert check_dc.description == "There are less than 6 hours left before DC drills. Hurry up for release!"
    assert check_dc.can_release

    start_event = now + 9 * 60 * 60
    end_event = now + 12 * 60 * 60
    check_dc = BuildSandbox.check_for_dc_drills(start_event, end_event)

    assert check_dc.description == "There are DC drills within 24 hours, don't forget about the release!"
    assert check_dc.can_release
