# -*- coding: utf-8 -*-
import unittest

import mock
from nose.tools import eq_
from passport.backend.ci.release import (
    build_changelog,
    format_branch_name,
    format_release_commit_message,
    merge_changelogs,
    merge_package_names_with_versions,
    parse_changelog,
    parse_release_commit_message_to_package_names_with_versions,
)


TEST_PACKAGE_NAMES_WITH_VERSIONS = [
    ['some-package', '0.0.1'],
    ['other-package', '1.0.0'],
]

TEST_PACKAGE_NAME_TO_CHANGELOG = {
    'some-package': ' * feature 1\n * feature 2',
    'other-package': ' * feature 3\n * feature 4',
}


TEST_UUID = 'deadbeef12345678'


class TestReleaseUtils(unittest.TestCase):
    def setUp(self):
        super(TestReleaseUtils, self).setUp()

        self.uuid4_mock = mock.Mock()
        self.uuid4_mock.hex = TEST_UUID
        self.uuid4_patch = mock.patch('passport.backend.ci.release.uuid4', mock.Mock(return_value=self.uuid4_mock))
        self.uuid4_patch.start()

    def tearDown(self):
        self.uuid4_patch.stop()
        super(TestReleaseUtils, self).tearDown()

    def test_format_release_commit_message(self):
        eq_(
            format_release_commit_message(TEST_PACKAGE_NAMES_WITH_VERSIONS),
            'release other-package 1.0.0, some-package 0.0.1',
        )
        eq_(
            format_release_commit_message(TEST_PACKAGE_NAMES_WITH_VERSIONS, issue='PASSP-000'),
            'PASSP-000 release other-package 1.0.0, some-package 0.0.1',
        )

    def test_format_branch_name(self):
        eq_(
            format_branch_name(TEST_PACKAGE_NAMES_WITH_VERSIONS),
            'release_other-package_1-0-0_some-package_0-0-1_deadbeef',
        )

        packages_with_versions_long = TEST_PACKAGE_NAMES_WITH_VERSIONS + [['z' * 255, '1.0.0']]
        eq_(
            format_branch_name(packages_with_versions_long),
            'release_other-package_1-0-0_some-package_0-0-1_' + 'z' * 64 + '_deadbeef',
        )

    def test_parse_release_commit_message_to_package_names_with_versions(self):
        eq_(
            parse_release_commit_message_to_package_names_with_versions(
                'release some-package 0.0.1, other-package 1.0.0',
            ),
            TEST_PACKAGE_NAMES_WITH_VERSIONS,
        )
        eq_(
            parse_release_commit_message_to_package_names_with_versions(
                'PASSP-000 release some-package 0.0.1, other-package 1.0.0',
            ),
            TEST_PACKAGE_NAMES_WITH_VERSIONS,
        )

    def test_merge_package_names_with_versions(self):
        eq_(
            merge_package_names_with_versions(
                TEST_PACKAGE_NAMES_WITH_VERSIONS,
                [
                    ['some-package', '0.0.2'],
                    ['new-package', '2.0.0'],
                ],
            ),
            [
                ['new-package', '2.0.0'],
                ['other-package', '1.0.0'],
                ['some-package', '0.0.2'],
            ]
        )

        eq_(
            merge_package_names_with_versions(
                [
                    ['some-package', '1.77.9'],
                    ['new-package', '1.9.1'],
                    ['other-package', '9.3.5'],
                ],
                [
                    ['some-package', '1.77.10'],
                    ['new-package', '1.10.0'],
                    ['other-package', '10.0.0'],
                ],
            ),
            [
                ['new-package', '1.10.0'],
                ['other-package', '10.0.0'],
                ['some-package', '1.77.10'],
            ]
        )

    def test_build_changelog(self):
        eq_(
            build_changelog(TEST_PACKAGE_NAME_TO_CHANGELOG),
            '\n'.join([
                '[other-package]',
                ' * feature 3',
                ' * feature 4',
                '',
                '[some-package]',
                ' * feature 1',
                ' * feature 2',
            ]),
        )

    def test_build_changelog_simple(self):
        eq_(
            build_changelog({'some-package': ' * feature 1'}),
            ' * feature 1',
        )

    def test_parse_changelog(self):
        eq_(
            parse_changelog(
                build_changelog(TEST_PACKAGE_NAME_TO_CHANGELOG),
                package_names=TEST_PACKAGE_NAME_TO_CHANGELOG.keys(),
            ),
            TEST_PACKAGE_NAME_TO_CHANGELOG,
        )

    def test_parse_changelog_simple(self):
        eq_(
            parse_changelog(
                ' * feature 1',
                package_names=['some-package'],
            ),
            {'some-package': ' * feature 1'},
        )

    def test_merge_changelogs(self):
        eq_(
            merge_changelogs(
                first_changelog_str=build_changelog(TEST_PACKAGE_NAME_TO_CHANGELOG),
                first_package_names=TEST_PACKAGE_NAME_TO_CHANGELOG.keys(),
                second_changelog_str=build_changelog({
                    'some-package': ' * feature 5',
                    'new-package': ' * feature 6',
                }),
                second_package_names=['some-package', 'new-package'],
            ),
            '\n'.join([
                '[new-package]',
                ' * feature 6',
                '',
                '[other-package]',
                ' * feature 3',
                ' * feature 4',
                '',
                '[some-package]',
                ' * feature 1',
                ' * feature 2',
                ' * feature 5',
            ]),
        )

    def test_merge_changelogs_simple(self):
        eq_(
            merge_changelogs(
                first_changelog_str=build_changelog({
                    'some-package': ' * feature 1',
                }),
                first_package_names=['some-package'],
                second_changelog_str=build_changelog({
                    'new-package': ' * feature 2',
                }),
                second_package_names=['new-package'],
            ),
            '\n'.join([
                '[new-package]',
                ' * feature 2',
                '',
                '[some-package]',
                ' * feature 1',
            ]),
        )
