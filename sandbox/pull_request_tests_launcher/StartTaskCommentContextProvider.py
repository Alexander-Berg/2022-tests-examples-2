import json
from urllib import quote_plus

from sandbox.common.utils import get_task_link


def get_start_task_comment_context(author, branch, commit, tasks, extension_config):
    config = json.loads(extension_config)
    context = {
        "author": _link_obj(author, _staff_link(author)),
        "branch": _link_obj(branch, _arcanum_link(branch)) if branch else None,
        "commit": _link_obj(commit, _arcanum_link(commit)) if commit else None,
        "platforms": [_link_obj(name, get_task_link(id)) for (id, name) in tasks.items()],
        "androidVersions": config.get("android_apis", []),
        "iosVersions": config.get("ios_versions", []),
        "gradleProperties": _text_from_lines(config.get("gradle_properties", [])),
        "testsTemplate": _text_from_lines(config.get("tests_template", [])),
    }
    return context


def _link_obj(name, link):
    return dict(name=name, link=link)


def _staff_link(id):
    return "https://staff.yandex-team.ru/{}".format(quote_plus(id))


def _arcanum_link(rev):
    "https://a.yandex-team.ru/arcadia/?rev={}".format(quote_plus(rev)),


def _text_from_lines(lines):
    return "\n".join(list(map(lambda e: _fix_string(e), lines)))


def _fix_string(s):
    return s.replace('*', '\\*').replace('>', '\\>')
