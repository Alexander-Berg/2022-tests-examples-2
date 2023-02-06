from sandbox import sdk2
import sandbox.common.types.client as ctc


class TestRunInPorto(sdk2.Task):

    class Requirements(sdk2.Task.Requirements):
        disk_space = 5 * 1024
        client_tags = ctc.Tag.PORTOD
        cores = 1

    class Parameters(sdk2.Task.Parameters):
        with sdk2.parameters.Group("Porto layer"):
            porto_layers = sdk2.parameters.Resource(
                "Parent layer resource",
                default=None,
                multiple=True,
                resource_type=sdk2.Resource,
            )

    def on_save(self):
        if self.Parameters.porto_layers:
            self.Requirements.porto_layers = [
                layer.id for layer in self.Parameters.porto_layers
            ]
        super(TestRunInPorto, self).on_save()

    def on_execute(self):
        import subprocess
        try:
            subprocess.check_call('find -name ros', shell=True)
            self.set_info('OK')
        except:
            self.set_info('Fail!')
            raise
