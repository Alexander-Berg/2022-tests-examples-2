import logging
import os
import shutil
from contextlib import contextmanager

import yaml
from sandbox import sdk2

RESOURCE_PREFIX = 'sandbox/projects/tank/griddic/docker_compose_test/'


class TankIntegrationTestsArtifacts(sdk2.Resource):
    tank_image_tag = sdk2.resource.Attributes.String("tank image tag")
    tests_resource_id = sdk2.resource.Attributes.String("ресурс с тестами")


class ResourcesMixin:
    def _download_resource_files(self):
        template = self._download_docker_compose_template()
        self._create_docker_compose_file_from_template(template)

        self._download_tests()
        self._download_resources_for_tests()

    def _download_docker_compose_template(self):
        from library.python import resource
        resource_key = RESOURCE_PREFIX + 'template.docker-compose.yaml'
        content = resource.resfs_read(resource_key)
        if not content:
            raise Exception('template.docker-compose.yaml resource not found')
        return content.decode()

    def _create_docker_compose_file_from_template(self, template_content):
        config = template_content.format(tag=self.Parameters.tank_image_tag)
        logging.info(config)
        with open('docker-compose.yaml', 'w') as out:
            out.write(config)

    def _download_tests(self):
        self._download_resource(self.Parameters.tests_resource_id, 'data')

    def _download_resources_for_tests(self):
        for test_dir, _ in self._tests_dirs():
            test_resources_description_file = os.path.join(test_dir, 'resources.yaml')
            if not os.path.exists(test_resources_description_file):
                continue
            with open(test_resources_description_file) as stream:
                resources_descriptions = yaml.load(stream)
            for resource_description in resources_descriptions:
                self._download_resource(resource_description['id'],
                                        os.path.join(test_dir, resource_description['path']))

    @staticmethod
    def _download_resource(resource_id, path_to_store):
        logging.debug('going to download resource %s to %s', resource_id, path_to_store)
        resource = sdk2.Resource[resource_id]
        data = sdk2.ResourceData(resource)
        path = data.path  # See https://docs.python.org/dev/library/pathlib.html
        logging.info("Resource %d downloaded to %s", resource_id, path)
        if os.path.isdir(path):
            shutil.copytree(path, path_to_store, dirs_exist_ok=True)
        else:
            os.makedirs(os.path.dirname(path_to_store), exist_ok=True)
            shutil.copyfile(path, path_to_store)

    def _store_tests_with_logs_as_resource(self):
        resource = TankIntegrationTestsArtifacts(self, 'Tests with logs', 'data')
        resource.tank_image_tag = self.Parameters.tank_image_tag
        resource.tests_resource_id = self.Parameters.tests_resource_id
        data = sdk2.ResourceData(resource)
        data.ready()
