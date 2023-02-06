# coding: utf-8

from sandbox.projects.partner.tasks.e2e_tests.e2e_all_tests.build_manager import \
    BuildManager

from sandbox.projects.adfox.adfox_ui.deploy import AdfoxUiDeploy, Stage, AdfoxUiBuild


class StandsManager(BuildManager):
    """
    Test stands manager: update stands
    """

    @property
    def adfox_stand_update_task_name(self):
        return 'adfox_stand_update_task'

    @property
    def pi_stad_update_task_name_for_adfox(self):
        return 'pi_stand_update_task_for_adfox'

    class Context(BuildManager.Context):
        pass

    class Parameters(BuildManager.Parameters):
        pass

    def build_adfox_stand(self):
        # Сборка тестового стенда Adfox
        task = AdfoxUiBuild(
            self,
            git_branch=self.Parameters.adfox_branch,
            stage=Stage.AUTO_TEST
        )
        task.enqueue()
        return task

    def update_adfox_stands(self, stands):

        def get_stage_id(type):
            for stand in stands:
                if stand['type'] == type:
                    return stand['adfox_stage_id']
            return '0'

        need_stand_types = set()
        for stand in stands:
            need_stand_types.add(stand['type'])

        tasks = []
        for need_stand_type in need_stand_types:
            # Обновление тестового стенда Adfox
            task = AdfoxUiDeploy(
                self,
                git_branch=self.Parameters.adfox_branch,
                stage=Stage.AUTO_TEST,
                autotest_stand_type=need_stand_type,
                stage_id=get_stage_id(need_stand_type)
            )
            task.enqueue()
            tasks.append(task)
        return tasks
