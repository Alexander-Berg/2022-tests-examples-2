import datetime

import pytest

from tests_effrat_employees import department


class PreprofileContextMock:
    def __init__(self):
        self._has_request_errors = False

        self.staff_groups_response = None

        self._departments = None
        self.helpdesk_response = None

        self.helpdesk_handler = None
        self.staff_departmentstaff_handler = None
        self.staff_groups_handler = None

    def build_helpdesk_response(self, mocked_time, load_json):
        response_raw = load_json('preprofile-export-helpdesk.json')
        response = []
        departments = {}
        for idx, item in enumerate(response_raw):
            domain = item.pop('_domain', None)
            item['modified_at'] = datetime.datetime.strftime(
                mocked_time.now(), '%Y-%m-%dT%H:%M:%S',
            )
            if not item.get('uid'):
                item['uid'] = str(10000000000000 + idx)
            response.append(item)
            dpt_id = item['department']
            if dpt_id not in departments:
                departments[dpt_id] = department.generate_staff_departments(
                    dpt_id, domain=domain or department.DEFAULT_DOMAIN,
                )

        self._departments = departments
        self.helpdesk_response = response

    @property
    def departments(self):
        return self._departments

    @property
    def has_request_errors(self):
        return self._has_request_errors


@pytest.fixture
def preprofile_mock(mockserver, mocked_time, load_json):
    ctx = PreprofileContextMock()
    ctx.build_helpdesk_response(mocked_time, load_json)

    @mockserver.json_handler('staff-preprofile/preprofile-api/export/helpdesk')
    def helpdesk_handler(request):
        if callable(ctx.helpdesk_response):
            return ctx.helpdesk_response(request)
        return ctx.helpdesk_response

    ctx.helpdesk_handler = helpdesk_handler

    @mockserver.json_handler('staff-for-wfm/v3/departmentstaff')
    def departmentstaff(request):
        department_url = request.query['department_group.url']
        return {
            'page': 1,
            'links': {},
            'limit': 1,
            'result': [
                {
                    'department_group': {
                        'id': dpt_id,
                        'url': dpt.department.external_id,
                        'name': dpt.department.name,
                    },
                }
                for dpt_id, dpt in ctx.departments.items()
                if department_url == dpt.department.external_id
            ],
        }

    ctx.staff_departmentstaff_handler = departmentstaff

    @mockserver.json_handler('staff-for-wfm/v3/groups')
    def groups(request):
        if ctx.staff_groups_response and callable(ctx.staff_groups_response):
            # pylint: disable=not-callable
            return ctx.staff_groups_response(request)
        return {'result': []}

    ctx.staff_groups_handler = groups

    return ctx
