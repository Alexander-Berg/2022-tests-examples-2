import argparse
import asyncio
import collections
import datetime
import pprint

import uvloop

from taxi.util import dates

from chatterbox import cron_run
from chatterbox.crontasks import calculate_stat
from chatterbox.internal import stat as stat_module
from chatterbox.internal import tasks_manager


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--day_from', required=True, help='YYYY-MM-DD')
    parser.add_argument('--day_to', required=True, help='YYYY-MM-DD')
    parser.add_argument('--sleep', default=2, type=int)
    parser.add_argument('--step_minutes', default=60, required=False, type=int)
    parser.add_argument('--dry_run', required=False, action='store_true')
    args = parser.parse_args()
    return args


async def main():
    async for app in cron_run.create_app(loop, None):
        args = parse_args()
        day_from = dates.parse_timestring(args.day_from, 'UTC')
        day_to = dates.parse_timestring(args.day_to, 'UTC')
        day = day_from
        while day <= day_to:
            day_string = calculate_stat.utc_datetime_to_moscow_day(day)
            await calculate_statistics(
                app.db, day_string, True, args.step_minutes, args.dry_run,
            )
            print('calculated statistics for day {}'.format(day_string))
            await asyncio.sleep(args.sleep)
            day += datetime.timedelta(days=1)


async def calculate_statistics(db, day, completed, step, dry):
    begin = calculate_stat.moscow_day_to_utc_datetime(day)
    end = begin + datetime.timedelta(days=1)
    base_stat = await _stat_by_line_login_action_in_addition(
        db, begin, end, datetime.timedelta(minutes=step),
    )
    for in_addition in [None, False, True]:
        statistics = await stat_calculate_statistics(
            db, begin, end, base_stat, in_addition,
        )
        if dry:
            pprint.pprint(statistics)
        else:
            await db.support_chatterbox_stat.find_and_modify(
                query={
                    'day': day,
                    'in_addition': stat_module.get_in_addition_query(
                        in_addition,
                    ),
                },
                update={
                    '$set': {
                        'completed': completed,
                        'lines_statistics': statistics['lines_statistics'],
                        'total_statistics': statistics['total_statistics'],
                    },
                },
                upsert=True,
                new=True,
            )


async def stat_calculate_statistics(
        db, begin, end, base_stat, in_addition=None,
):
    def default_line():
        return {'count': 0, 'first_answers': [], 'full_resolves': []}

    lines = collections.defaultdict(default_line)

    match = {'created': {'$gte': begin, '$lte': end}}
    if in_addition:
        match['history.in_addition'] = True
    if in_addition is False:
        match['history.in_addition'] = {'$ne': True}
    cursor = db.secondary.support_chatterbox.aggregate(
        [
            {'$match': match},
            {'$group': {'_id': '$line', 'count': {'$sum': 1}}},
        ],
    )
    async for line in cursor:
        lines[line['_id']]['count'] += line['count']

    stat_statuses = tasks_manager.STATUSES_EXTERNAL
    stat_statuses += [tasks_manager.STATUS_READY_TO_ARCHIVE]
    query = {
        'updated': {'$gte': begin, '$lte': end},
        'status': {'$in': stat_statuses},
        'full_resolve': {'$exists': True},
    }
    if in_addition:
        query['history.in_addition'] = True
    if in_addition is False:
        query['history.in_addition'] = {'$ne': True}
    cursor = db.secondary.support_chatterbox.find(
        query, {'line': True, 'full_resolve': True, 'first_answer': True},
    )
    async for task in cursor:
        lines[task['line']]['full_resolves'].append(task['full_resolve'])
        lines[task['line']]['first_answers'].append(task['first_answer'])

    total = default_line()
    for line in lines.values():
        total['first_answers'].extend(line['first_answers'])
        total['full_resolves'].extend(line['full_resolves'])
        total['count'] += line['count']
    for line in list(lines.values()) + [total]:
        if line['first_answers']:
            line['first_answers'].sort()
            line['first_answer_median'] = int(
                line['first_answers'][len(line['first_answers']) // 2],
            )
        if line['full_resolves']:
            line['full_resolves'].sort()
            line['full_resolve_median'] = int(
                line['full_resolves'][len(line['full_resolves']) // 2],
            )
        line.pop('first_answers')
        line.pop('full_resolves')
    lines_statistics = []
    actions_by_lines = await _actions_by_lines(
        base_stat, in_addition=in_addition,
    )
    actions_by_supporter_by_lines = await _actions_by_supporter_by_lines(
        base_stat, in_addition=in_addition,
    )
    for line_name, line_stat in lines.items():
        line_stat['line'] = line_name
        line_stat['actions'] = stat_module._get_line_actions(
            actions_by_lines, line_name,
        )
        line_stat['actions_by_supporter'] = stat_module._get_line_actions(
            actions_by_supporter_by_lines, line_name,
        )
        lines_statistics.append(line_stat)
    total['actions'] = await _total_actions(base_stat, in_addition=in_addition)
    total['actions_by_supporter'] = await _total_actions_by_supporter(
        base_stat, in_addition=in_addition,
    )
    return {'lines_statistics': lines_statistics, 'total_statistics': total}


async def _actions_by_supporter_by_lines(stat, in_addition=None):
    result = []
    for line, line_stat in stat.items():
        line_stat_result = []
        for login, login_stat in line_stat.items():
            actions = [
                {
                    'action_id': action,
                    'count': action_stat[in_addition]['count'],
                    'average_latency': (
                        action_stat[in_addition]['total_latency']
                        / action_stat[in_addition]['count']
                    ),
                    'min_latency': action_stat[in_addition]['min_latency'],
                    'max_latency': action_stat[in_addition]['max_latency'],
                }
                for action, action_stat in login_stat.items()
                if in_addition in action_stat
            ]
            if actions:
                line_stat_result.append({'login': login, 'actions': actions})
        if line_stat_result:
            result.append({'_id': line, 'line_stat': line_stat_result})

    return result


async def _actions_by_lines(stat, in_addition=None):
    result = []
    for line, line_stat in stat.items():
        stat_by_action = {}
        for _, login_stat in line_stat.items():
            for action, action_stat in login_stat.items():
                if in_addition not in action_stat:
                    continue

                line_action_stat = stat_by_action.setdefault(
                    action,
                    {
                        'count': 0,
                        'total_latency': 0,
                        'min_latency': action_stat[in_addition]['min_latency'],
                        'max_latency': action_stat[in_addition]['max_latency'],
                    },
                )

                line_action_stat['count'] += action_stat[in_addition]['count']
                line_action_stat['total_latency'] += action_stat[in_addition][
                    'total_latency'
                ]
                line_action_stat['max_latency'] = max(
                    line_action_stat['max_latency'],
                    action_stat[in_addition]['max_latency'],
                )
                line_action_stat['min_latency'] = min(
                    line_action_stat['min_latency'],
                    action_stat[in_addition]['min_latency'],
                )

        result.append(
            {
                '_id': line,
                'line_stat': [
                    {
                        'action_id': action,
                        'count': line_action_stat['count'],
                        'average_latency': (
                            line_action_stat['total_latency']
                            / line_action_stat['count']
                        ),
                        'min_latency': line_action_stat['min_latency'],
                        'max_latency': line_action_stat['max_latency'],
                    }
                    for action, line_action_stat in stat_by_action.items()
                ],
            },
        )

    return result


async def _total_actions(stat, in_addition=None):
    total_stat = {}
    result = []
    for _, line_stat in stat.items():
        for _, login_stat in line_stat.items():
            for action, action_stat in login_stat.items():
                if in_addition not in action_stat:
                    continue

                total_action_stat = total_stat.setdefault(
                    action,
                    {
                        'count': 0,
                        'total_latency': 0,
                        'min_latency': action_stat[in_addition]['min_latency'],
                        'max_latency': action_stat[in_addition]['max_latency'],
                    },
                )

                total_action_stat['count'] += action_stat[in_addition]['count']
                total_action_stat['total_latency'] += action_stat[in_addition][
                    'total_latency'
                ]
                total_action_stat['max_latency'] = max(
                    total_action_stat['max_latency'],
                    action_stat[in_addition]['max_latency'],
                )
                total_action_stat['min_latency'] = min(
                    total_action_stat['min_latency'],
                    action_stat[in_addition]['min_latency'],
                )

    sorted_stat = sorted(total_stat.items(), key=lambda item: item[0])
    for action, total_action_stat in sorted_stat:
        result.append(
            {
                'action_id': action,
                'count': total_action_stat['count'],
                'average_latency': (
                    total_action_stat['total_latency']
                    / total_action_stat['count']
                ),
                'min_latency': total_action_stat['min_latency'],
                'max_latency': total_action_stat['max_latency'],
            },
        )

    return result


async def _total_actions_by_supporter(stat, in_addition=None):
    total_stat_by_supporter = {}
    result = []
    for _, line_stat in stat.items():
        for login, login_stat in line_stat.items():
            for action, action_stat in login_stat.items():
                if in_addition not in action_stat:
                    continue

                supporter_stat = (
                    total_stat_by_supporter.setdefault(login, {}).setdefault(
                        action,
                        {
                            'count': 0,
                            'total_latency': 0,
                            'min_latency': action_stat[in_addition][
                                'min_latency'
                            ],
                            'max_latency': action_stat[in_addition][
                                'max_latency'
                            ],
                        },
                    )
                )

                supporter_stat['count'] += action_stat[in_addition]['count']
                supporter_stat['total_latency'] += action_stat[in_addition][
                    'total_latency'
                ]
                supporter_stat['max_latency'] = max(
                    supporter_stat['max_latency'],
                    action_stat[in_addition]['max_latency'],
                )
                supporter_stat['min_latency'] = min(
                    supporter_stat['min_latency'],
                    action_stat[in_addition]['min_latency'],
                )

    sorted_stat_by_login = sorted(
        total_stat_by_supporter.items(), key=lambda item: item[0],
    )
    for login, login_stat in sorted_stat_by_login:
        sorted_stat_by_action = sorted(
            login_stat.items(), key=lambda item: item[0],
        )
        actions = []
        for action, total_action_stat in sorted_stat_by_action:
            actions.append(
                {
                    'action_id': action,
                    'count': total_action_stat['count'],
                    'average_latency': (
                        total_action_stat['total_latency']
                        / total_action_stat['count']
                    ),
                    'min_latency': total_action_stat['min_latency'],
                    'max_latency': total_action_stat['max_latency'],
                },
            )
        if actions:
            result.append({'login': login, 'actions': actions})

    return result


async def _stat_by_line_login_action_in_addition(
        db, date_from, date_to, chunk_delta,
):
    stat = {}
    chunk_date_from = date_from
    while chunk_date_from <= date_to:
        conditions = {
            'history': {
                '$elemMatch': {
                    'login': {'$ne': tasks_manager.LOGIN_SUPERUSER},
                    'created': {'$gte': chunk_date_from},
                },
            },
        }
        chunk_date_to = chunk_date_from + chunk_delta
        if chunk_date_to > date_to:
            conditions['history']['$elemMatch']['created']['$lte'] = date_to
        else:
            conditions['history']['$elemMatch']['created'][
                '$lt'
            ] = chunk_date_to

        cursor = db.secondary.support_chatterbox.find(
            conditions, {'_id': False, 'history': True},
        )
        async for task in cursor:
            for action in task['history']:
                if action['login'] == tasks_manager.LOGIN_SUPERUSER:
                    continue
                if 'latency' not in action:
                    continue
                if action['created'] < chunk_date_from:
                    continue
                if action['created'] >= chunk_date_to:
                    continue
                if action['created'] > date_to:
                    continue

                action_stat = (
                    stat.setdefault(action['line'], {})
                    .setdefault(action['login'], {})
                    .setdefault(action['action'], {})
                )

                for in_addition in (None, True, False):
                    if (
                            in_addition is not None
                            and in_addition != action.get('in_addition', False)
                    ):
                        continue

                    in_addition_stat = action_stat.setdefault(in_addition, {})
                    in_addition_stat.setdefault('count', 0)
                    in_addition_stat.setdefault('total_latency', 0)
                    in_addition_stat.setdefault(
                        'min_latency', action['latency'],
                    )
                    in_addition_stat.setdefault(
                        'max_latency', action['latency'],
                    )

                    in_addition_stat['count'] += 1
                    in_addition_stat['total_latency'] += action['latency']
                    in_addition_stat['min_latency'] = min(
                        in_addition_stat['min_latency'], action['latency'],
                    )
                    in_addition_stat['max_latency'] = max(
                        in_addition_stat['max_latency'], action['latency'],
                    )

        print(
            'calculated statistics for {} - {}'.format(
                chunk_date_from, min(chunk_date_to, date_to),
            ),
        )
        chunk_date_from = chunk_date_to

    return stat


if __name__ == '__main__':
    loop = uvloop.new_event_loop()
    loop.run_until_complete(main())
