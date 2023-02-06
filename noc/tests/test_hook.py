from unittest import TestCase
from unittest.mock import patch
import yaml
from noc.gitlabbot.botlib.bot import amplify_context, get_changed_scopes, OrderedLoader
from noc.gitlabbot.botlib import bot

ycfg='''
scopes:
  yellow:
    files:
      - plugins/pns.php
      - /.*bot-map\\.inc/
    owners:
      - shaitan
      - gescheit
      - lytboris
      - vladstar
      - azryve
      - moonug
    quorum: 1

  red:
    files:
      - owners.yml
      - plugins/*
      - scripts/*
      - export/*
      - netmap/*
      - debian/*
      - deploy/*
    owners:
      - shaitan
      - gescheit
      - azryve
      - vladstar
      - moonug
      - lytboris
    quorum: 2

  all:
    files:
      - /.*/
    owners:
      - shaitan
      - gescheit
      - azryve
      - vladstar
      - moonug
      - lytboris
    quorum: 1
'''.strip()


class TestHook(TestCase):
    def test_get_changed_scopes(self):
        config = yaml.load(ycfg, Loader=OrderedLoader)
        cases = [
            (
                ["owners.yml"],
                ["red"]
            ),
            (
                ["eee.py"],
                ["all"]
            ),
            (
                ["plugins/pns.php"],
                ["yellow"]
            ),
            (
                ["bot-map.inc"],
                ["yellow"]
            ),
            (
                ["plugins/bot-map.inc"],
                ["yellow"]
            ),
            (
                ["ee/bbat"],
                ["all"]
            ),
            (
                ["export/all.php"],
                ["red"]
            )
        ]
        for (changes, scope) in cases:
            ctx = {
                "config": config,
                "changes": changes
            }
            scopes = get_changed_scopes(ctx)
            self.assertEqual(scopes, scope, f"{changes}")

    def test_author_approves_are_ignored(self):
        ctx = {
            "project": {
                "id": 9,
            },
            "mr": {
                "iid": 1026,
                "target_branch": "master",
                "source_branch": "no_approve_from_author",
                "created_at": "2021-03-23T11:27:29.995Z",
                "work_in_progress": False,
                "labels": [],
                "author": {"username": "alan"},
            },
            "is_mr_opening": False,
            "req_note": 0,
        }

        # in real API call events would be in reversed order
        # keeping them in straight order for readability
        events = [
            {
                "target_type": None,
                "action_name": "pushed to",
                "push_data": {"ref": "no_approve_from_author"},
                "author": {"username": "alan"},
            },
            {
                "target_type": "Note",
                "action_name": "commented on",
                "note": {
                    "noteable_type": "MergeRequest",
                    "noteable_iid": 1026,
                    "author": {"username": "xornet"},
                    "id": 1,
                    "body": "!ok",
                },
            },
            {
                "target_type": "Note",
                "action_name": "commented on",
                "note": {
                    "noteable_type": "MergeRequest",
                    "noteable_iid": 1026,
                    "author": {"username": "alan"},
                    "id": 2,
                    "body": "!ok",
                },
            },
            {
                "target_type": "Note",
                "action_name": "commented on",
                "note": {
                    "noteable_type": "MergeRequest",
                    "noteable_iid": 1026,
                    "author": {"username": "moonug"},
                    "id": 3,
                    "body": "!ok",
                },
            },
            {
                "target_type": "Note",
                "action_name": "commented on",
                "note": {
                    "noteable_type": "MergeRequest",
                    "noteable_iid": 1026,
                    "author": {"username": "vladstar"},
                    "id": 4,
                    "body": "!bless",
                },
            },
            {
                "target_type": "Note",
                "action_name": "commented on",
                "note": {
                    "noteable_type": "MergeRequest",
                    "noteable_iid": 1026,
                    "author": {"username": "moonug"},
                    "id": 5,
                    "body": "!nack",
                },
            },
        ]

        with patch("noc.gitlabbot.botlib.bot.gitlab_query") as gitlab_query_mock:
            gitlab_query_mock.side_effect = [
                {"output": ycfg},  # config
                {"output": {"changes": []}},  # changes
                {"output": list(reversed(events))},  # events
                None,  # updating labels
            ]
            amplify_context(ctx)

        self.assertEqual(sorted(ctx["approved_by"]), ["vladstar", "xornet"])

    def test_add_mr_labels_already_exists(self):
        """Ensure that nothing happens when trying to add a label that already exists."""
        ctx = {
            "mr": {
                "iid": 1026,
                "labels": [bot.LABEL_DIFF_MANUALLY_APPROVED],
            },
            "project": {
                "id": 9,
            },
        }
        with patch("noc.gitlabbot.botlib.bot.gitlab_query") as gitlab_query_mock:
            bot.add_mr_labels(ctx, bot.LABEL_DIFF_MANUALLY_APPROVED)
            gitlab_query_mock.assert_not_called()

    def test_add_mr_labels(self):
        """Ensure that MR and context are updated."""
        ctx = {
            "mr": {
                "iid": 1026,
                "labels": [],
            },
            "project": {
                "id": 9,
            },
        }
        with patch("noc.gitlabbot.botlib.bot.gitlab_query") as gitlab_query_mock:
            bot.add_mr_labels(ctx, bot.LABEL_DIFF_MANUALLY_APPROVED)
            # ensure mr is updated
            gitlab_query_mock.assert_called_once()

        # ensure ctx is updated
        assert ctx["mr"]["labels"] == [bot.LABEL_DIFF_MANUALLY_APPROVED]

    def test_del_mr_labels_no_label_exists(self):
        """Ensure that nothing happens when trying to delete a label that already missing."""
        ctx = {
            "mr": {
                "iid": 1026,
                "labels": [],
            },
            "project": {
                "id": 9,
            },
        }
        with patch("noc.gitlabbot.botlib.bot.gitlab_query") as gitlab_query_mock:
            bot.del_mr_labels(ctx, bot.LABEL_DIFF_MANUALLY_APPROVED)
            gitlab_query_mock.assert_not_called()

    def test_del_mr_labels(self):
        """Ensure that MR and context are updated."""
        ctx = {
            "mr": {
                "iid": 1026,
                "labels": [bot.LABEL_DIFF_MANUALLY_APPROVED],
            },
            "project": {
                "id": 9,
            },
        }
        with patch("noc.gitlabbot.botlib.bot.gitlab_query") as gitlab_query_mock:
            bot.del_mr_labels(ctx, bot.LABEL_DIFF_MANUALLY_APPROVED)
            # ensure mr is updated
            gitlab_query_mock.assert_called_once()

        # ensure ctx is updated
        assert ctx["mr"]["labels"] == []
