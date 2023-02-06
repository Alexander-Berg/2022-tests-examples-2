import random

from sandbox import sdk2


class TestEnvironmentDummyResource(sdk2.Resource):
    idd = sdk2.parameters.Integer(
        "Dummy idd",
        default=0
    )


class TestEnvironmentDummyResourceGenerator(sdk2.Task):

    def on_execute(self):
        resource = TestEnvironmentDummyResource(self, "Output file", "output_dir")
        resource.idd = random.randint(1, 1000000)
        data = sdk2.ResourceData(resource)
        data.path.mkdir(0o755, parents=True, exist_ok=True)
        data.path.joinpath("filename.txt").write_bytes(
            "Dummy data"
        )
        data.ready()
