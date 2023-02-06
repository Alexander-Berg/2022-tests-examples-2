#!/usr/bin/env python3
import collections
import sys

import get_services
import teamcity_utils

RTC_SUBST = '/production:'
RTC_PREFIX = 'registry.yandex.net/taxi/'


def main() -> None:
    services = get_services.load_services(
        sys.argv[1:] or ('docker-compose.yml', 'eats/docker-compose.yml'),
    )
    rtc_dict = collections.defaultdict(list)

    for service_name, params in services.items():
        extended_service = params.get('extends', {}).get('service', '')
        extended_service = extended_service.split('taxi-')[-1]

        image = params.get('image', '')
        bare_name = image.split(RTC_PREFIX)[-1].split('/')[0]
        if not bare_name.startswith('taxi'):
            service_name = service_name.split('taxi-')[-1]
        if RTC_SUBST in image and image.startswith(RTC_PREFIX):
            rtc_dict[extended_service].append(service_name)

    for repo, services_list in rtc_dict.items():
        env_name = repo.upper().replace('-', '_') + '_RTC_IMAGES'
        teamcity_utils.set_parameter(env_name, ' '.join(services_list))


if __name__ == '__main__':
    main()
