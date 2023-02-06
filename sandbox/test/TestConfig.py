import json
import yatest

from sandbox.projects.safesearch.CleanWebTestAndDeploy.config.config import Config, PROJECTS


class TestProjects:
    def test_1(self):
        for project in PROJECTS:
            for component in project.components:
                package_arcadia_path = '{}/{}/package.json'.format(Config.CLEAN_WEB_ROOT, component.path)
                package_path = yatest.common.source_path(package_arcadia_path)
                with open(package_path) as json_file:
                    try:
                        package_json = json.load(json_file)
                    except Exception as e:
                        raise Exception('Failed to load JSON file {!r}: {!r}'.format(package_path, e))

                    assert package_json['meta']['name'] == component.path.replace('clients/', '').replace('backends/', '').replace('/', '_')

                    target = '{}/{}'.format(Config.CLEAN_WEB_ROOT, component.path)
                    assert package_json['build']['targets'] == [target],\
                        'Check build targets at {}'.format(package_arcadia_path)

                    assert package_json['data'][0]['source']['path'] == target, \
                        'Check data source path at {}'.format(package_arcadia_path)
