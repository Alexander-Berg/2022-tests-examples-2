import datetime
import logging
import time
import re

from sandbox import sdk2
from sandbox.sandboxsdk import environments


PROJECTS_DEPRECATION_THRESHOLD_DAYS = 40
DELTA = datetime.timedelta(days=PROJECTS_DEPRECATION_THRESHOLD_DAYS)
THRESHOLD_TIMESTAMP = time.time() - DELTA.total_seconds()

CLOSED_PROJECTS_DEPRECATION_THRESHOLD_DAYS = 30
CLOSED_DELTA = datetime.timedelta(days=CLOSED_PROJECTS_DEPRECATION_THRESHOLD_DAYS)
CLOSED_THRESHOLD_TIMESTAMP = time.time() - CLOSED_DELTA.total_seconds()

SKIP_LAST_OPENED_PROJECTS_COUNTER = 2


PROJECT_PREFIXES = (
    "chat\-v\d",
    "lego\-(v|islands_)?\d",
    "nerpa\-(touch_v|desktop_v)?\d",
    "turbo\-v?\d",
    "Tycoon\s(pr\d|verv)",
    "uslugi-\d",
    "ydo-erp-\d",
	"health-\d",
    "(Q|q)\s(pr|v|ver)\d",

    "fiji\-(images_v|video_v)?\d",
    "fiji-releases_",

    "granny-\d",
    "granny\-js\-(v|freeze_v)?\d",

    "serp\-js\-(v|exp\d*_v)?\d",
    "serp-js-(releases_|issue-)",

    "(C|c)ollections-\d",
    "(C|c)ollections\s(v|pr)\d",
)

class TestpalmMongodbMaintenance(sdk2.Task):
    class Requirements(sdk2.Task.Requirements):
        environments = [
            environments.PipEnvironment('pymongo'),
            environments.PipEnvironment('requests'),
        ]

    class Parameters(sdk2.Task.Parameters):
        mongodb_url = sdk2.parameters.String('MongoDB URL', description='MongoDB Connection string')

    def on_execute(self):
        mongodb_secret = sdk2.yav.Secret('sec-01dd8p69t29c78565sasadb1jg')

        mongodb_url = self.Parameters.mongodb_url.format(
            password=mongodb_secret.data()['password'],
        )

        import pymongo
        client = pymongo.MongoClient(mongodb_url)
        db = client.testpalm

        projects = []

        for prefix in PROJECT_PREFIXES:
            projectsByPrefix = [p for p in db.project.find({
                '$or': [
                    {
                        'title': {'$regex': re.compile('^' + prefix)},
                        'lastModifiedTime': {'$lte': THRESHOLD_TIMESTAMP * 1000}
                    },
                    {
                        'title': {'$regex': re.compile('^' + prefix + '.* \[Closed\]')},
                        'lastModifiedTime': {'$lte': CLOSED_THRESHOLD_TIMESTAMP * 1000}
                    },
                ]
            }).sort('lastModifiedTime', -1)]

            skippedProjects = 0
            deprecatedProjects = []

            # Remove 2 last opened projects from deprecation list
            for project in projectsByPrefix:
                if skippedProjects == SKIP_LAST_OPENED_PROJECTS_COUNTER or project['title'].endswith(' [Closed]'):
                    deprecatedProjects.append(project)
                else:
                    skippedProjects = skippedProjects + 1

            projects.extend(deprecatedProjects)

        import requests

        tms_robot_secret = sdk2.yav.Secret('sec-01dd8nk2q0ntke4r03jb0zxn0z')

        tms_robot_token = tms_robot_secret.data()['api_token']

        for project in projects:
            logging.info('Processing project %s', project['title'])
            projectId = project['_id']
            url = 'https://testpalm-api.yandex-team.ru/projects/%s?permanent=1' % projectId
            oauth = 'OAuth %s' % tms_robot_token
            requests.delete(
                url,
                headers={'Authorization': oauth},
                verify=False,
                timeout=60
            )

        logging.info('Done')
