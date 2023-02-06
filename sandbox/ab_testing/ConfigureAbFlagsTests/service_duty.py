import logging
import collections

from sandbox.projects.release_machine.components.config_core import responsibility
from sandbox.projects.release_machine.helpers import responsibility_helper


SERVICES = {
    "web": [
        responsibility.Abc(  # https://abc.yandex-team.ru/services/serpsearch/duty/?role=2522
            component_id=1021,
            schedule_slug="web4-QArelease",
        ),
        responsibility.Abc(  # https://abc.yandex-team.ru/services/serpsearch/duty/?role=688
            component_id=1021,
            schedule_slug="web4-release",
        ),
        responsibility.Abc(  # https://abc.yandex-team.ru/services/ups/duty/
            component_id=33085,
        ),
    ],
    "images": [
        responsibility.Abc(  # https://abc.yandex-team.ru/services/images-report-templates/duty/?role=3292
            component_id=2290,
            schedule_slug="img-templates-testing-duty",
        ),
        responsibility.Abc(  # https://abc.yandex-team.ru/services/ups/duty/
            component_id=33085,
        ),
    ],
    "video": [
        responsibility.Abc(  # https://abc.yandex-team.ru/services/video-report-templates/duty/?role=2023
            component_id=2269,
            schedule_slug="video-templates-qa-duty",
        ),
        responsibility.Abc(  # https://abc.yandex-team.ru/services/ups/duty/
            component_id=33085,
        ),
    ],
}


def get_service_duty(**kwargs):
    """
    Get a list of people on duty for the given services

    Example:
        `get_service_duty(web=True, images=True)` - get duties for web and images

    :param kwargs: required services flags
    :return: a list of duty employees
    """

    logging.info("Getting service duty")

    result = []
    service_params = collections.defaultdict(bool)
    service_params.update(kwargs)

    for service, responsible_abc_list in SERVICES.items():

        if not service_params[service]:
            logging.info("Skipping %s (not required)", service)
            continue

        for responsible_abc in responsible_abc_list:

            user = responsibility_helper.get_responsible_user_login_from_abc_object(responsible_abc)

            if not user:
                logging.info("Responsible for %s cannot be determined", service)
                continue

            result.append(user)

    return result
