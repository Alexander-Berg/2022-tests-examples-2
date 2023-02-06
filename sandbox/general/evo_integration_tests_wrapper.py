from sandbox.projects.release_machine.components.config_core.jg.cube import (
    Cube,
    CubeInput,
)


class AliceEvoIntegrationTestsWrapper(Cube):

    NAME = "alice_evo_integration_tests_wrapper"

    def __init__(self, input, evo_context):
        if evo_context:
            input = self._enrich_input_from_evo_ctx(input, evo_context)
        super(self.__class__, self).__init__(
            name=self.NAME,
            title="EvoTests",
            task="projects/alice/alice_evo_integration_tests_wrapper",
            input=input,
        )

    @staticmethod
    def _enrich_input_from_evo_ctx(input, evo_context):
        input_from_ctx = CubeInput(
            launch_type=evo_context.component_name,
            branch_number=evo_context.branch_number,
            tag_number=evo_context.tag_number,
            beta_name=evo_context.beta_name,
            release_ticket=evo_context.release_ticket,
        )
        input_from_ctx.merge(input)
        return input_from_ctx
