def sort_tariff_requirements(tariff_requirements: list) -> None:
    tariff_requirements.sort(
        key=lambda tariff_requirement: tariff_requirement['class'],
    )


def sort_requests_for_comparison(*requests):
    for request in requests:
        if 'tariff_requirements' in request:
            sort_tariff_requirements(request['tariff_requirements'])
