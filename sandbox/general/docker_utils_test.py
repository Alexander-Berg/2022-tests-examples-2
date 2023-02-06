import json
import logging
import subprocess

import sandbox.common as common
from sandbox import sdk2
from sandbox.common.types import task as ctt
from sandbox.projects.common.nanny import nanny
from sandbox.projects.common.build.YaPackage import DOCKER


class DockerTestTask(sdk2.Task, nanny.ReleaseToNannyTask2):

    def _ya_package_build_docker(
            self,
            package_files,
            revision,
            docker_image_repository="maps",
            docker_user="robot-maps-sandbox",
            docker_token_vault_name="robot-maps-sandbox-docker-oauth",
            task_owner='MAPS-CI',
            overwrite_read_only_files=False):
        with self.memoize_stage["ya_package_build_docker_{}@{}".format('&'.join(package_files), revision)]:
            self.Context.child_tasks_ids = []
            for package_file in package_files:
                self.set_info("Building docker image for {}".format(package_file))
                YaPackageClass = sdk2.Task['MAPS_DOCKER_TEST']
                task = YaPackageClass(
                    self,
                    kill_timeout=7200,
                    package_type=DOCKER,
                    docker_push_image=True,
                    docker_registry="registry.yandex.net",
                    docker_image_repository=docker_image_repository,
                    packages=package_file,
                    docker_user=docker_user,
                    docker_token_vault_name=docker_token_vault_name,
                    resource_type="YA_PACKAGE_RESOURCE",
                    checkout_arcadia_from_url="arcadia:/arc/trunk/arcadia@{revision}"
                                              .format(revision=revision),
                    checkout=False,
                    use_aapi_fuse=True,
                    use_arc_instead_of_aapi=True,
                    aapi_fallback=True,
                    ya_yt_store=True,
                    ignore_recurses=True,
                    overwrite_read_only_files=overwrite_read_only_files
                )
                task.Parameters.owner = task_owner
                task.save().enqueue()
                self.Context.child_tasks_ids.append(task.id)
            raise sdk2.WaitTask(self.Context.child_tasks_ids, ctt.Status.Group.FINISH + ctt.Status.Group.BREAK, wait_all=True)
        return [sdk2.Task.find(id=id_).first() for id_ in self.Context.child_tasks_ids]

    def _verify_subtask(self, task):
        if task.status in ctt.Status.Group.BREAK + ctt.Status.Group.SCHEDULER_FAILURE:
            raise common.errors.TaskError("Subtask failed with status " + str(task.status))

    def _release_docker_image(self, ya_package_task, nanny_status, custom_docker_image_name=None):
        with self.memoize_stage["release_{}_{}".format(nanny_status, ya_package_task.id)]:
            image_name, _, image_tag = (custom_docker_image_name or ya_package_task.Context.output_resource_version).partition(':')
            _, _, image_name = image_name.partition('/')
            release_payload = {
                'spec': {
                    'type': "DOCKER_RELEASE",
                    'docker_release': {
                        "image_name": image_name,
                        "image_tag":  image_tag,
                        "release_type": nanny_status.upper()
                    },
                    'desc': self.Parameters.description
                }
            }
            logging.info('Sending release of Docker task {} to Nanny'.format(ya_package_task.id))
            logging.info('Release payload: %s', json.dumps(release_payload, indent=4))
            result = self.nanny_client.create_release2(release_payload)
            logging.info('Release result is {}'.format(result))


def _docker_inspect_image(docker_repository, docker_cmd):
    args = list(docker_cmd) + ["inspect", "--format='{{json .RepoDigests}}'", docker_repository]
    docker_process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = docker_process.communicate()
    if docker_process.returncode != 0:
        error_descr = "'{cmd}' failed with exit code {exit_code}: {error}".format(
            cmd=" ".join(args), exit_code=docker_process.returncode, error=stderr)
        raise Exception(error_descr)
    return stdout


def get_image_hash(docker_repository, docker_cmd):
    try:
        image_desc = _docker_inspect_image(docker_repository, docker_cmd)
        image_desc = json.loads(image_desc[1:-2])
        return image_desc[0].split('@')[-1]
    except Exception as e:
        raise Exception("Failed to retrieve hash for image {}: {}".format(docker_repository, e))
