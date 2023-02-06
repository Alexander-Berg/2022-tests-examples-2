import json
import os
from datetime import datetime, timedelta


DATASET_DIR = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    'dataset'
)


def run_tests(grouper_cls, verbosity=1):
    total_points = 0.0
    max_points = 0.0

    with open(os.path.join(DATASET_DIR, '_tags_data.json')) as f:
        tags_data = json.load(f)

    grouper = grouper_cls(tags_data, id_field='_human_id')

    for path_entry in os.scandir(DATASET_DIR):
        if not path_entry.is_file() or path_entry.name.startswith('_'):
            continue

        if verbosity > 0:
            print('\n')
            print('File: {}'.format(path_entry.name))

        with open(path_entry.path) as f:
            data = json.load(f)

        events = data['events']
        now = (
            datetime.fromtimestamp(events[0]['clock']) +
            timedelta(seconds=data['ago_seconds'])
        )
        expected_matrix = grouper.make_matrix_from_groups(
            data['groups'],
            data['ungrouped'],
        )
        candidate_matrix = grouper.get_matrix(events, now)
        total_points += get_points(
            candidate_matrix,
            expected_matrix,
            events,
            grouper,
            now,
            verbosity,
        )
        max_points += 1

    if not max_points:
        raise RuntimeError('No data was found in ./dataset dir')

    return total_points / max_points


def get_points(candidate_matrix, expected_matrix, events, grouper, now,
               verbosity):
    assert candidate_matrix
    assert set(candidate_matrix.keys()) == set(expected_matrix.keys())

    events_dict = {e['_human_id']: e for e in events}
    matches = 0
    missed = 0
    false_groupings = 0
    for key in candidate_matrix.keys():
        if candidate_matrix[key] == expected_matrix[key]:
            matches += 1
            if verbosity > 1:
                print('{} and {} - ok'.format(*key))
        else:
            if verbosity > 0:
                if expected_matrix[key]:
                    missed += 1
                    error_message = 'group expected'
                else:
                    false_groupings += 1
                    error_message = 'should not be grouped'
                print('{} and {} - fail: {} {}'.format(
                    key[0],
                    key[1],
                    error_message,
                    grouper.get_score(
                        events_dict[key[0]],
                        events_dict[key[1]],
                        now,
                    )
                ))
            if verbosity > 1:
                print(events_dict[key[0]])
                print(events_dict[key[1]])
                print('Score: {}'.format(grouper.get_score(
                    events_dict[key[0]],
                    events_dict[key[1]],
                    now,
                )))

    result = matches / len(candidate_matrix)
    if verbosity >= 1:
        tmpl = ('Total score: {} ({}/{}). Groupping missed: {}. '
                'False groupings: {}')
        print(tmpl.format(
            result,
            matches,
            len(candidate_matrix),
            missed,
            false_groupings,
        ))
    return result

Trade secrets of Yandex LLC. 16, Lev Tolstoy Str., Moscow, Russia, 119021
