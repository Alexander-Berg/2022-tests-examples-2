import shutil
import os.path

from sandbox import sdk2
from sandbox.projects import resource_types


class UserdataTestDataExtractor(sdk2.Task):
    class Parameters(sdk2.Parameters):
        build_output = sdk2.parameters.Resource(
            'Build output with test results',
            required=True,
            resource_type=resource_types.BUILD_OUTPUT
        )
        target = sdk2.parameters.String(
            'Target name to find resources',
            required=True
        )
        index_fragment = sdk2.parameters.String(
            'When provided, create index fragment resource from with path suffix',
            required=False
        )

    def get_test_output(self):
        src_data = sdk2.ResourceData(self.Parameters.build_output)
        return os.path.join(str(src_data.path), self.Parameters.target, "test-results", "pytest", "testing_out_stuff")

    def create_tables_archive(self):
        resource = resource_types.USERDATA_TABLES_ARCHIVE(self, "Tables archive with test data", "tables")
        resource.tables_prefix = "sandbox/"
        dst_data = sdk2.ResourceData(resource)
        shutil.copytree(os.path.join(self.get_test_output(), "tables_dump"), str(dst_data.path))
        dst_data.ready()

    def create_index_fragment(self):
        resource = resource_types.USERDATA_INDEX_FRAGMENT(self, "Index fragment with test data", "index_fragment")
        dst_data = sdk2.ResourceData(resource)

        def ignore_func(src, names):
            return [n for n in names if n in ["bin", "scripts"]]

        shutil.copytree(os.path.join(self.get_test_output(), str(self.Parameters.index_fragment)), str(dst_data.path), ignore=ignore_func)

        dst_data.ready()

    def on_execute(self):
        self.create_tables_archive()
        if self.Parameters.index_fragment:
            self.create_index_fragment()
