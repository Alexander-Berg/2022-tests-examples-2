# coding: utf-8

import six

import sandbox.common.types.client as ctc
import sandbox.common.types.resource as ctr

from sandbox import sdk2

from sandbox import common


class TestUnknownResource(sdk2.Resource):
    releasers = ["aripinen", "korum", "r-vetrov", "yetty"]
    releasable = True
    restart_policy = ctr.RestartPolicy.DELETE  # default value, may be changed for particular resource

    # custom attributes
    test_attr = sdk2.parameters.Integer("Test attribute", default=None)
    test_required_attr = sdk2.parameters.String("Test required attribute", required=True, default="value")


class TestUnknownTask(sdk2.Task):
    class Parameters(sdk2.Parameters):
        # common parameters
        description = "Test"
        max_restarts = 10
        kill_timeout = 3600

        # custom parameters
        overwrite_client_tags = sdk2.parameters.Bool("Overwrite client tags", default=False)
        with overwrite_client_tags.value[True]:
            client_tags = sdk2.parameters.ClientTags(
                "Client tags",
                default=ctc.Tag.GENERIC | ctc.Tag.MULTISLOT | ctc.Tag.SERVER | ctc.Tag.Group.OSX
            )

    def on_execute(self):
        attrs = {"test_attr": 42}
        file_resource_data = sdk2.ResourceData(TestUnknownResource(
            self, self.Parameters.description, "lifetime.log", **attrs
        ))

        common.fs.allocate_file(six.text_type(file_resource_data.path), 1024)
