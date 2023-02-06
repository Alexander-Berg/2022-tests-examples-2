import os
import shutil

from sandbox.common.errors import TaskFailure
from sandbox.common.types import task
from sandbox.projects.common.nanny import nanny
from sandbox import sdk2


class RazladkiWowPackage(sdk2.Resource):
    """
    Ya package with razladki_wow sources, solomon calculator, etc.
    """
    releasable = True


class RazladkiWowPortoLayer(sdk2.Resource):
    """
    Porto layer with razladki_wow dependencies
    """
    releasable = True


class BuildRazladkiWowPorto(nanny.ReleaseToNannyTask2, sdk2.Task):
    class Parameters(sdk2.Task.Parameters):
        package_resource_type = sdk2.parameters.String(
            'Ya package resource type',
            required=True,
            default='RAZLADKI_WOW_PACKAGE',
        )

        package_path = sdk2.parameters.String(
            'Arcadia path to package.json',
            required=True,
            default='razladki/porto/package.json',
        )

        porto_layer_resource_type = sdk2.parameters.String(
            'Porto layer resource type',
            required=True,
            default='RAZLADKI_WOW_PORTO_LAYER',
        )

        porto_layer_parent = sdk2.parameters.Resource(
            'Parent layer',
            required=True,
        )

        porto_layer_setup_script = sdk2.parameters.String(
            'Arcadia url to porto layer setup script',
            required=True,
            default='arcadia:/arc/trunk/arcadia/razladki/porto/porto_layer_setup_xenial.sh',
        )

        release_on_success = sdk2.parameters.Bool(
            'Release if the task succeeds',
            default=False,
            required=True,
        )

        with release_on_success.value[True]:
            with sdk2.parameters.String('Release status', required=True) as release_status:
                release_status.values['stable'] = 'stable'
                release_status.values['testing'] = 'testing'

    def _run_substasks(self):
        ya_package_task = sdk2.Task['YA_PACKAGE'](
            self,
            description='Razladki wow package\n'
                        'Child of #{}'.format(self.id),
            packages=self.Parameters.package_path,
            package_type='tarball',
            resource_type=self.Parameters.package_resource_type,
            owner=self.owner,
        )
        ya_package_task.Requirements.disk_space = self.Requirements.disk_space
        ya_package_task.save().enqueue()
        self.Context.ya_package_task_id = ya_package_task.id

        build_porto_layer_task = sdk2.Task['BUILD_PORTO_LAYER'](
            self,
            parent_layer=self.Parameters.porto_layer_parent.id,
            description='Razladki wow porto layer\n'
                        'Child of #{}'.format(self.id),
            layer_name='razladki_layer',
            layer_type=self.Parameters.porto_layer_resource_type,
            script=self.Parameters.porto_layer_setup_script,
        )
        build_porto_layer_task.Requirements.disk_space = self.Requirements.disk_space
        build_porto_layer_task.save().enqueue()
        self.Context.build_porto_layer_task_id = build_porto_layer_task.id

        raise sdk2.WaitTask(
            [
                ya_package_task,
                build_porto_layer_task,
            ],
            task.Status.Group.FINISH | task.Status.Group.BREAK,
            wait_all=True,
        )

    def _copy_resource_from_subtask(self, subtask, resource_type):
        # based on YtBuildYaPackage._copy_resource_from_sub_task
        src_resource = sdk2.Resource[resource_type].find(task=subtask).first()
        if src_resource is None:
            raise TaskFailure('Subtask resource not found')

        src_data = sdk2.ResourceData(src_resource)
        src_path = str(src_data.path.absolute())
        resource_name = os.path.basename(src_path)

        dst_resource = sdk2.Resource[resource_type](
            self,
            src_resource.description,
            resource_name,
            ttl=30,
        )
        dst_data = sdk2.ResourceData(dst_resource)
        dst_path = str(dst_data.path.absolute())
        if os.path.isfile(src_path):
            shutil.copy(src_path, dst_path)
        else:
            shutil.copytree(src_path, dst_path)
        dst_data.ready()

    def _check_subtasks(self):
        ya_package_task = self.find(id=self.Context.ya_package_task_id).first()
        if ya_package_task.status not in task.Status.Group.SUCCEED:
            raise TaskFailure('YA_PACKAGE subtask failed')

        build_porto_layer_task = self.find(id=self.Context.build_porto_layer_task_id).first()
        if build_porto_layer_task.status not in task.Status.Group.SUCCEED:
            raise TaskFailure('BUILD_PORTO_LAYER subtask failed')

        self._copy_resource_from_subtask(ya_package_task, self.Parameters.package_resource_type)
        self._copy_resource_from_subtask(build_porto_layer_task, self.Parameters.porto_layer_resource_type)

    def on_execute(self):
        with self.memoize_stage.subtasks:
            self._run_substasks()

        self._check_subtasks()

    def on_success(self, prev_status):
        sdk2.Task.on_success(self, prev_status)
        if self.Parameters.release_on_success:
            self.on_release(dict(
                releaser=self.author,
                release_status=self.Parameters.release_status,
                release_subject='Razladki Wow',
                email_notifications=dict(to=['svxf', 'valgushev', 'uranix'], cc=[]),
                release_comments='Razladki Wow',
            ))

    def on_release(self, additional_parameters):
        nanny.ReleaseToNannyTask2.on_release(self, additional_parameters)
        sdk2.Task.on_release(self, additional_parameters)
