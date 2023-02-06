import os
import yaml

from sandbox import common
from sandbox.projects.browser.autotests_qa_tools.configs import testing_groups


MAX_ASSESSOR_RUN = 60
# see https://st.yandex-team.ru/BYIN-11877#5fb3af38f589b30523ee0b09
DEFAULT_TESTCASE_ESTIMATE = 3 * 60 * 1000
MAX_TESTCASE_STAT_ESTIMATE = 20 * 60 * 1000
REPORT_OVERHEAD = 1.3  # We suppose testers spend 30% of testrun time on paperwork: tickets creation etc

INFRA_SUPPORT_CHAT = 'https://t.me/joinchat/EdxsYxG7mSf7Q9LDnZ6e3g'

REGRESSION_MAILLIST = 'browser-regression'
TSP_HOURS = 2

DEFAULT_TESTPALM_PROJECT = 'brocase'


class TestingGroup(object):
    def __init__(self, name, telegram, components, participants,
                 manual_ticket_queue=None, assessors_ticket_queue=None,
                 asessors_priority=1, testpalm_projects=None, activity=None,
                 manual_ticket_tags=None, manual_ticket_components=None,
                 asessors_ticket_tags=None, asessors_ticket_components=None,
                 hardcore_assignee=False):
        self.name = name
        self.telegram = telegram
        self.components = components
        self.participants = participants
        self.manual_ticket_queue = manual_ticket_queue
        self.assessors_ticket_queue = assessors_ticket_queue
        self.asessors_priority = asessors_priority
        self.testpalm_projects = testpalm_projects or []
        self.activity = activity or []
        self.manual_ticket_tags = manual_ticket_tags or []
        self.manual_ticket_components = manual_ticket_components or []
        self.asessors_ticket_tags = asessors_ticket_tags or []
        self.asessors_ticket_components = asessors_ticket_components or []
        self.hardcore_assignee = hardcore_assignee

    @property
    def head(self):
        return self.participants[0]

    @property
    def summary(self):
        return {
            "name": self.name,
            "telegram": self.telegram,
            "components": self.components,
            "participants": self.participants,
            "manual_ticket_queue": self.manual_ticket_queue,
            "assessors_ticket_queue": self.assessors_ticket_queue,
            "asessors_priority": self.asessors_priority,
            "testpalm_projects": self.testpalm_projects,
            "activity": self.activity,
            "manual_ticket_tags": self.manual_ticket_tags,
            "manual_ticket_components": self.manual_ticket_components,
            "asessors_ticket_tags": self.asessors_ticket_tags,
            "asessors_ticket_components": self.asessors_ticket_components,
            "hardcore_assignee": self.hardcore_assignee
        }


@common.utils.singleton
def get_group_conf():
    GROUPS_CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(testing_groups.__file__)), 'testing_groups.yaml')
    with open(GROUPS_CONFIG_PATH, 'r') as stream:
        return yaml.load(stream)


def get_groups_conf_by_activities(activities):
    return {
        name: data for name, data in get_group_conf().iteritems() if any(_x in activities for _x in data['activity'])
    }


@common.utils.singleton
def get_componets_conf():
    COMPONENTS_CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(testing_groups.__file__)), 'components.yaml')
    with open(COMPONENTS_CONFIG_PATH, 'r') as stream:
        return yaml.load(stream)


@common.utils.singleton
def load_groups():
    res = []
    for group, info in get_group_conf().iteritems():
        res.append(TestingGroup(name=group, **info))
    return res


@common.utils.singleton
def get_group_priority(group_name, default=1):
    return get_group_conf().get(group_name, {}).get("asessors_priority", default)


@common.utils.singleton
def get_group(component, default_group=None):
    groups = load_groups()
    for group in groups:
        if component in group.components:
            return group
    return default_group


@common.utils.singleton
def identify_group_by_component(component):
    config = get_group_conf()
    for group, info in config.iteritems():
        if component in info['components']:
            return group
    return 'Unknown'


@common.utils.singleton
def group_head(group):
    config = get_group_conf()
    return config[group]['participants'][0]


@common.utils.singleton
def telegram_chat(group):
    config = get_group_conf()
    return config[group]['telegram']


@common.utils.singleton
def get_project_by_component(component):
    config = get_componets_conf()
    for project, components in config.iteritems():
        for c in components:
            if c == component:
                return project
    return DEFAULT_TESTPALM_PROJECT
