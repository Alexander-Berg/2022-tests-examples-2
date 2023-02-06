import logging
import unittest

from sandbox.projects.mobile_apps.teamcity_sandbox_runner.utils.artifacts_processor import Artifact

logger = logging.getLogger("test_artifacts_processor")


class TestArtifact(unittest.TestCase):

    def test_artifact_operations(self):
        artifact = Artifact(artifact=("+aaa/bbb", "ccc"))
        self.assertEqual(artifact.sign, "+")

        artifact = Artifact(artifact=("aaa/bbb", "ccc"))
        self.assertEqual(artifact.sign, "+")

        artifact = Artifact(artifact=("-aaa/bbb", "ccc"))
        self.assertEqual(artifact.sign, "-")

        artifact = Artifact(artifact=("$aaa/bbb", "ccc"))
        self.assertEqual(artifact.sign, "$")

    def test_artifact_sources(self):
        artifact = Artifact(artifact=("+aaa/bbb", "ccc"))
        self.assertEqual(artifact.src, "aaa/bbb")

        artifact = Artifact(artifact=("aaaa/bbb", "ccc"))
        self.assertEqual(artifact.src, "aaaa/bbb")

        artifact = Artifact(artifact=("-aaa/bbb", "ccc"))
        self.assertEqual(artifact.src, "aaa/bbb")

        artifact = Artifact(artifact=("$aaa/bbb", "ccc"))
        self.assertEqual(artifact.src, "aaa/bbb")

        artifact = Artifact(artifact=("+**/*", "ccc"))
        self.assertEqual(artifact.src, "**/*")

        artifact = Artifact(artifact=("+./*", "ccc"))
        self.assertEqual(artifact.src, "*")

        artifact = Artifact(artifact=("buildscripts/build/app.zip", "app.zip"))
        self.assertEqual(artifact.src, "buildscripts/build/app.zip")
        self.assertEqual(artifact.src_archived, True)

    def test_artifact_targets(self):
        artifact = Artifact(artifact=("+aaa/bbb", "ccc"))
        self.assertEqual(artifact.dst_basename_noext, "ccc")
        self.assertEqual(artifact.dst_archived, False)

        artifact = Artifact(artifact=("aaa/bbb", "ccc.zip"))
        self.assertEqual(artifact.dst_basename_noext, "ccc")
        self.assertEqual(artifact.dst_archived, True)

        artifact = Artifact(artifact=("aaa/bbb", "ccc/ddd/eee.zip"))
        self.assertEqual(artifact.dst_basename_noext, "ccc/ddd/eee")
        self.assertEqual(artifact.dst_archived, True)

        artifact = Artifact(artifact=("buildscripts/build/app.zip", "app.zip"))
        self.assertEqual(artifact.dst_basename_noext, "app.zip")
        self.assertEqual(artifact.dst_archived, False)

        artifact = Artifact(artifact=("+aaa/bbb", None))
        self.assertEqual(artifact.dst_basename_noext, None)
        self.assertEqual(artifact.dst_archived, False)

        artifact = Artifact(artifact=("aaa/bbb/"))
        self.assertEqual(artifact.src, "aaa/bbb/")
        self.assertEqual(artifact.dst_basename_noext, None)
