def ods_order_rows(cases):
    for case in cases:
        for order in case['given']['orders']:
            yield order


def ods_forms_inspection_rows(cases):
    for case in cases:
        for form in case['given']['forms']:
            form['inspection_id'] = case['id'] + '#' + form['inspection_id']
            yield form


def ods_toloka_rows(cases):
    for case in cases:
        for assessment in case['given']['toloka']:
            yield assessment


def expected_inspections(case):
    return case['expected']


def actual_inspections(case, actual_all_checks_all_cases):
    return [inspection
            for inspection in actual_all_checks_all_cases
            if inspection['inspection_id'].startswith(case['id'])]
