import json
import logging

logger = logging.getLogger(__name__)


class TestPalmClientWrapper:
    def __init__(self, client):
        self.client = client

    def create_testrun(
            self,
            project_id,
            testsuite_id,
            testrun_title,
            assignee,
            created_by,
    ):
        try:
            result = self.client.create_testrun_from_suite(
                testsuiteid=testsuite_id,
                data={
                    'status': 'CREATED',
                    'title': testrun_title,
                    'assignee': assignee,
                    'createdBy': created_by,
                },
                project=project_id,
            )
        except Exception as e:
            logger.error(
                'Failed to create a Testrun from Testsuite in TestPalm, error: %s',
                e.message,
            )
            raise e
        if isinstance(result, list):
            if len(result) == 0:
                raise RuntimeError('Testrun data is incorrect')
            result = result[0]
        return result

    def get_testrun_info(self, project_id, testrun_id):
        logger.info('Getting testrun info by id %s' % testrun_id)
        response = self.client.get_testrun_info(
            id=testrun_id, project=project_id,
        )
        if isinstance(response, dict) and response.get('title'):
            return response
        raise RuntimeError('Testrun with id=%s not found' % testrun_id)

    def bulk_update_statuses(self, testrun_id, project_id, testcase_statuses):
        try:
            self.client.make_request(
                method='post',
                path='testrun/%s/%s/resolve/bulk' % (project_id, testrun_id),
                data=json.dumps(testcase_statuses),
            )
        except Exception as e:
            logger.error(
                'Failed to update statuses for testcases in testrun, error: %s',
                e.message,
            )
            raise e
