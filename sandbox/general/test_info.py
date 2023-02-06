# coding=utf-8
from __future__ import unicode_literals

from sandbox.projects.metrika.admins.metrika_admin_package import MetrikaAdminPackage
from sandbox.projects.metrika.admins.run_binary import RunBinary
from sandbox.projects.metrika.core.metrika_core_development import MetrikaCoreDevelopment
from sandbox.projects.metrika.core.metrika_core_release import MetrikaCoreRelease
from sandbox.projects.metrika.java.metrika_java_development import MetrikaJavaDevelopment
from sandbox.projects.metrika.java.metrika_java_release import MetrikaJavaRelease

ARCADIA_URL = 'arcadia-arc:/#trunk'
TRACKER_ISSUE = 'TEST-60441'

TESTS = {
    MetrikaJavaDevelopment.name: {
        MetrikaJavaDevelopment.Parameters.arcadia_url: ARCADIA_URL,
        MetrikaJavaDevelopment.Parameters.daemon_list: ['audienceapid'],
        MetrikaJavaDevelopment.Parameters.send_notifications: False,
        MetrikaJavaDevelopment.Parameters.tracker_issue: TRACKER_ISSUE
    },
    MetrikaJavaRelease.name: {
        MetrikaJavaRelease.Parameters.daemon_list: ['providerd'],
    },
    MetrikaCoreDevelopment.name: {
        MetrikaCoreDevelopment.Parameters.arcadia_url: ARCADIA_URL,
        MetrikaCoreDevelopment.Parameters.daemon_list: ['logprocessd'],
        MetrikaCoreDevelopment.Parameters.send_notifications: False,
        MetrikaCoreDevelopment.Parameters.tracker_issue: TRACKER_ISSUE
    },
    MetrikaCoreRelease.name: {
        MetrikaCoreRelease.Parameters.arcadia_url: ARCADIA_URL,
        MetrikaCoreRelease.Parameters.daemon_list: ['logprocessd'],
        MetrikaCoreRelease.Parameters.tracker_issue: TRACKER_ISSUE
    },
    MetrikaAdminPackage.name: {
        MetrikaAdminPackage.Parameters.arcadia_url: ARCADIA_URL,
        MetrikaAdminPackage.Parameters.name: 'clickhouse-server-metrika'
    },
    'METRIKA_BUILD_BINARY_TASK': {
        'arcadia_url': 'arcadia:/arc/trunk/arcadia',
        'task_type': RunBinary.name,
        'release_branch': 'testing'
    }
}
