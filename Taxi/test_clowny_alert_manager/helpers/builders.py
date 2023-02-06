from typing import List
from typing import Optional

from testsuite.utils import matching


def notification(logins: List[str], name: str, id_: int, for_upsert=False):
    data = {
        'logins': logins,
        'name': name,
        'repo_meta': {'config_project': '', 'file_name': ''},
        'statuses': [{'from': 'OK', 'to': 'WARN'}],
        'type': 'telegram',
    }
    if not for_upsert:
        data.update(
            id=id_,
            created_at=matching.datetime_string,
            updated_at=matching.datetime_string,
            is_deleted=False,
        )
    return data


class Event(dict):
    def __init__(
            self,
            id_: int,
            name: str,
            config_id=None,
            template_id=None,
            for_upsert=False,
            ignore_nodata: Optional[bool] = True,
    ):
        super().__init__(
            name=name,
            settings={
                'times': [
                    {
                        'crit': {'count_threshold': 0},
                        'days': ['Mon', 'Sun'],
                        'time': [0, 23],
                        'warn': {'count_threshold': 0},
                    },
                ],
            },
        )
        if config_id:
            self['config_id'] = config_id
        if template_id:
            self['template_id'] = template_id
        if ignore_nodata is not None:
            self['settings']['ignore_nodata'] = ignore_nodata
        if not for_upsert:
            self.update(
                id=id_,
                created_at=matching.datetime_string,
                updated_at=matching.datetime_string,
                is_deleted=False,
            )

    def with_notifications(self, *notifications):
        self['notification_options'] = list(notifications)
        return self


def repo_meta(
        config_project='taxi',
        file_name='pkgver.yaml',
        file_path='templates/pkgver.yaml',
):
    result = {'config_project': config_project}
    for field, value in [('file_name', file_name), ('file_path', file_path)]:
        if value is not None:
            result[field] = value
    return result


def template(name: str, *events, repo_meta_=None, for_upsert=False):
    if repo_meta_ is None:
        repo_meta_ = repo_meta()
    data = {
        'name': name,
        'namespace': 'default',
        'events': list(events),
        'repo_meta': repo_meta_,
    }
    if not for_upsert:
        data.update(
            id=1,
            created_at=matching.datetime_string,
            updated_at=matching.datetime_string,
            is_deleted=False,
        )
    return data


class LinkedTemplate(dict):
    def __init__(self, template_, **kwargs):
        super().__init__(template=template_, overrides=kwargs)

    def with_notifications(self, *notifications):
        self['notification_options'] = list(notifications)
        return self


class Config(dict):
    def __init__(self, id_=1, branch_id=1, repo_meta_=None, for_upsert=False):
        super().__init__(
            branch_id=branch_id,
            repo_meta=(
                repo_meta_
                or {
                    'config_project': 'taxi',
                    'file_name': 'b1.yaml',
                    'file_path': 'b1.yaml',
                }
            ),
            events=[],
            notification_options=[],
            templates=[],
        )
        if not for_upsert:
            self.update(
                id=id_,
                created_at=matching.datetime_string,
                updated_at=matching.datetime_string,
                is_deleted=False,
            )

    def with_events(self, *events):
        self['events'] = list(events)
        return self

    def with_templates(self, *templates):
        self['templates'] = list(templates)
        return self

    def with_notifications(self, *notifications):
        self['notification_options'] = list(notifications)
        return self


def branch(
        *configs,
        id_=1,
        service_id=1,
        clown_branch_ids=None,
        repo_meta_=None,
        names=None,
        namespace=None,
        basename=None,
        juggler_host=None,
        for_upsert=False,
):
    result = {
        'service_id': service_id,
        'names': names or ['some'],
        'clown_branch_ids': clown_branch_ids or [],
        'namespace': namespace or 'ns1',
        'repo_meta': repo_meta_ or repo_meta(
            file_name='b1.yaml', file_path='b1.yaml',
        ),
        'configs': list(configs),
    }
    result['basename'] = basename if basename else result['names'][0]
    result['juggler_host'] = (
        juggler_host if juggler_host else result['basename']
    )
    if not for_upsert:
        result.update(
            id=id_,
            created_at=matching.datetime_string,
            updated_at=matching.datetime_string,
            is_deleted=False,
        )
    return result


def service(
        *branches,
        id_=1,
        project_name='taxi',
        service_name='crons',
        clown_project_id=None,
        clown_service_id=None,
        type_='cgroup',
        repo_meta_=None,
        for_upsert=False,
):
    result = {
        'project_name': project_name,
        'service_name': service_name,
        'type': type_,
        'repo_meta': repo_meta_ or {'config_project': 'taxi'},
        'branches': list(branches),
    }
    if not for_upsert:
        result.update(
            id=id_,
            created_at=matching.datetime_string,
            updated_at=matching.datetime_string,
            is_deleted=False,
        )
    if clown_service_id:
        result['clown_service_id'] = clown_service_id
    if clown_project_id:
        result['clown_project_id'] = clown_project_id
    return result
