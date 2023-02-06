from sandbox import sdk2


class TestPipelineTask(sdk2.Task):

    class Requirements(sdk2.Requirements):
        ram = 4 * 1024
        cores = 1

        class Caches(sdk2.Requirements.Caches):
            pass

    def on_execute(self):
        pass
