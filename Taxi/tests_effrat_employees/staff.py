import datetime
import re
from typing import List


class StaffDepartmentsQuery:
    def __init__(self, query: str):
        clauses = re.split('[()]', query)
        self.departments = list(
            map(
                lambda x: x.split('==')[1][1:-1],
                filter(self._is_department_clause, clauses),
            ),
        )
        self.modified_at = datetime.datetime.fromisoformat(
            next(filter(self._is_modified_at_clause, clauses)).split('>')[1][
                1:-1
            ],
        )

    department_urls: List[str]
    modified_at: datetime.datetime
    limit: str

    @staticmethod
    def _is_department_clause(clause: str) -> bool:
        return (
            'department_group.department.url' in clause
            or 'department_group.ancestors.department.url' in clause
        )

    @staticmethod
    def _is_modified_at_clause(clause: str) -> bool:
        return '_meta.modified_at' in clause


class StaffLoginsQuery:
    def __init__(self, query: str):
        clauses = re.split('[()]', query)
        self.logins = list(
            map(
                lambda x: x.split('==')[1][1:-1],
                filter(self._is_login_clause, clauses),
            ),
        )

    logins: List[str]

    @staticmethod
    def _is_login_clause(clause: str) -> bool:
        return 'login' in clause


class StaffGroupsQuery:
    SUBDEPARTMENTS_QUERY_FIELDS = [
        'department.id',
        'department.level',
        'department.name',
        'department.url',
        'id',
        'level',
        'name',
        'parent.department.id',
        'parent.department.name',
        'parent.department.url',
        'parent.id',
        'parent.name',
        'parent.url',
        'url',
    ]

    DEPARTMENT_HEADS_QUERY_FIELDS = [
        'department.heads.person.uid',
        'department.id',
        'department.level',
        'department.name',
        'department.url',
        'id',
        'name',
        'url',
    ]

    _LOOP_VERIFIED = False

    def __init__(self, load_json):
        self._load_json = load_json

    @staticmethod
    def _detect_a_loop_or_crossing(groups_tree):
        if StaffGroupsQuery._LOOP_VERIFIED:
            return
        verified = set([])
        for url, _ in groups_tree.items():
            if url in verified:
                continue
            visited = set([url])
            unvisited = groups_tree[url]['_children']
            while unvisited:
                cur = unvisited.pop(0)
                assert cur not in visited, (
                    'Loop or intersection detected in '
                    + f' staff_v3_groups_tree.json within "{cur}"'
                )
                visited.add(cur)
                verified.add(cur)
                unvisited += groups_tree[url]['_children']
        StaffGroupsQuery._LOOP_VERIFIED = True

    @staticmethod
    def _build_subdepartment_part(dep, url):
        return {
            'is_deleted': False,
            'id': dep['id'] * 10,
            'name': dep['name'],
            'url': url,
            'department': {
                'is_deleted': False,
                'id': dep['id'],
                'name': {
                    'full': {'ru': dep['name'], 'en': 'En-' + dep['name']},
                },
                'url': url,
            },
        }

    @staticmethod
    def _build_subdepartment(child, root, url):
        dep = StaffGroupsQuery._build_subdepartment_part(child, child['url'])
        dep['parent'] = StaffGroupsQuery._build_subdepartment_part(root, url)
        return dep

    def subdepartments_response(self, query_args):
        query = query_args['_query']

        # simple statement like `(a=="")or(b == "")...` expected
        groups_tree = self._load_json('staff_v3_groups_tree.json')
        StaffGroupsQuery._detect_a_loop_or_crossing(groups_tree)

        result = {'result': [], 'limit': query_args.get('_limit', 1)}

        pattern = re.compile(r'\(parent.url=="([^"]+)"\)')
        visited = set()
        found_all: List[str] = pattern.findall(query)
        for url in found_all:
            assert url in groups_tree
            root = groups_tree[url]
            for child_url in root['_children']:
                if child_url in visited:
                    continue
                visited.add(child_url)
                child = groups_tree[child_url]
                result['result'].append(
                    StaffGroupsQuery._build_subdepartment(child, root, url),
                )
        return result

    @staticmethod
    def _build_department_heads(root):
        return {
            'id': root['id'] * 10,
            'name': root['name'],
            'url': root['url'],
            'department': {
                'id': root['id'],
                'name': {
                    'full': {'ru': root['name'], 'en': 'En-' + root['name']},
                },
                'url': root['url'],
                'heads': [{'person': head} for head in root['heads']],
            },
        }

    def deparment_heads_response(self, query_args):
        query = query_args['_query']

        # simple statement like `(a=="")or(b == "")...` expected
        groups_tree = self._load_json('staff_v3_groups_tree.json')
        StaffGroupsQuery._detect_a_loop_or_crossing(groups_tree)

        result = {'result': [], 'limit': query_args.get('_limit', 1)}

        pattern = re.compile(r'\(department.heads.person.uid=="([^"]+)"\)')
        found_all: List[str] = pattern.findall(query)
        visited = set()
        for head in found_all:
            for _, group in groups_tree.items():
                if group['id'] in visited:
                    continue
                assert 'heads' in group
                if head not in [check['uid'] for check in group['heads']]:
                    continue
                visited.add(group['id'])
                result['result'].append(
                    StaffGroupsQuery._build_department_heads(group),
                )
        return result

    def response(self, request):
        # XXX: this check of content-type is important to parse a url-encoded
        # arguments of the request, TAXICOMMON-4988
        headers = request.headers
        assert (
            'Content-Type' in headers
        ), f'Missed Content-Type header, received headers: {request.headers}'
        assert (
            headers['Content-Type'] == 'application/x-www-form-urlencoded'
        ), (
            'Expected application/x-www-form-urlencoded as value of header '
            + f'Content-Type, but got {request.headers["Content-Type"]}'
        )
        # dummy check the request contains not a json body
        request_data = request.get_data()
        assert (
            request_data.decode('utf-8')[0] != '{'
        ), f'Expected data as url-encoded form, but got {request_data}'

        query_args = request.form
        assert (
            query_args
        ), f'Unexpected /v3/groups request with data="{request.get_data()}"'
        fields = query_args['_fields'].split(',')
        fields.sort()
        assert fields in (
            self.SUBDEPARTMENTS_QUERY_FIELDS,
            self.DEPARTMENT_HEADS_QUERY_FIELDS,
        )

        if fields == self.SUBDEPARTMENTS_QUERY_FIELDS:
            return self.subdepartments_response(query_args)
        return self.deparment_heads_response(query_args)
