# Generated via `tvmknife unittest service -s 111 -d 111`
LOYALTY_SERVICE_TICKET = (
    '3:serv:CBAQ__________9_IgQIbxBv:Vu-cLYI6QABXmqYglsi_E'
    'nQoyEav5W8v6-SY1L6ANPnhig2fXWfmwR_HahKjuoBleAzbA6SytO'
    'xSre7KztT-sB4RkuZ5xoOHcGNYvx6aYGeifq4RkE6IEraTAyc8VAG'
    'rn1smMWCNr1HWYG2DySE2wSAwebZ1vpyvE9Vh4Wvjooc'
)


def get_auth_headers(
        park_id='db1',
        driver_profile_id='uuid1',
        user_agent: str = 'Taximeter 9.07 (1234)',
):
    app_version = ' '.join(user_agent.split(' ')[1:])
    return {
        'Accept-Language': 'ru',
        'X-YaTaxi-Park-Id': park_id,
        'X-YaTaxi-Driver-Profile-Id': driver_profile_id,
        'X-Request-Application': 'taximeter',
        'X-Request-Application-Version': app_version,
        'X-Request-Version-Type': '',
        'X-Request-Platform': 'android',
        'X-Ya-Service-Ticket': LOYALTY_SERVICE_TICKET,
        'User-Agent': user_agent,
    }


def select_account(pgsql, unique_driver_id):
    with pgsql['loyalty'].cursor() as cursor:
        cursor.execute(
            f"""SELECT unique_driver_id, next_recount, status,
            block, send_notification
            FROM loyalty.loyalty_accounts
            WHERE unique_driver_id = '{unique_driver_id}'
            """,
        )
        result = list(cursor)
        return result


def select_log(pgsql, unique_driver_id):
    with pgsql['loyalty'].cursor() as cursor:
        cursor.execute(
            f"""SELECT status, unique_driver_id, reason, points
            FROM loyalty.status_logs
            WHERE unique_driver_id = '{unique_driver_id}'
            ORDER BY created DESC
            """,
        )
        result = list(cursor)
        return result


def select_manual_status(pgsql, unique_driver_id):
    with pgsql['loyalty'].cursor() as cursor:
        cursor.execute(
            f"""SELECT unique_driver_id, new_status
            FROM loyalty.manual_statuses
            WHERE unique_driver_id = '{unique_driver_id}'
            ORDER BY event_at DESC
            """,
        )
        result = list(cursor)
        return result


def make_priority_experiment3(enabled, clauses=None):
    if clauses is None:
        clauses = []
    return dict(
        match={'predicate': {'type': str(enabled).lower()}, 'enabled': True},
        name='replace_activity_with_priority',
        consumers=['loyalty/priority-activity-override'],
        clauses=clauses,
        default_value={
            'enabled': True,
            'rewards': {
                'point_b': {
                    'block_threshold': 90,
                    'title_override': 'loyalty.reward.title_point_b_exp',
                    'text_override': 'loyalty.reward.description_point_b_exp',
                    'block_override': (
                        'loyalty.details.block_point_b_by_priority'
                    ),
                },
            },
        },
    )


def make_priority_exp3_wo_default(clauses=None):
    if clauses is None:
        clauses = [
            {
                'enabled': True,
                'extension_method': 'replace',
                'is_paired_signal': False,
                'is_signal': False,
                'is_tech_group': False,
                'predicate': {
                    'init': {
                        'arg_name': 'zones',
                        'set_elem_type': 'string',
                        'value': 'non-existent-name',
                    },
                    'type': 'contains',
                },
                'title': 'test_zones',
                'value': {
                    'enabled': True,
                    'rewards': {
                        'point_b': {
                            'block_threshold': 90,
                            'title_override': (
                                'loyalty.reward.title_point_b_exp'
                            ),
                            'text_override': (
                                'loyalty.reward.description_point_b_exp'
                            ),
                            'block_override': (
                                'loyalty.details.block_point_b_by_priority'
                            ),
                        },
                    },
                },
            },
        ]
    return dict(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='replace_activity_with_priority',
        consumers=['loyalty/priority-activity-override'],
        clauses=clauses,
    )


def get_priority_exp_zones_clause(zones_value, block_threshold):
    return {
        'enabled': True,
        'extension_method': 'replace',
        'is_paired_signal': False,
        'is_signal': False,
        'is_tech_group': False,
        'predicate': {
            'init': {
                'arg_name': 'zones',
                'set_elem_type': 'string',
                'value': zones_value,
            },
            'type': 'contains',
        },
        'title': 'test_zones',
        'value': {
            'enabled': True,
            'rewards': {
                'point_b': {
                    'block_threshold': block_threshold,
                    'title_override': 'loyalty.reward.title_point_b_exp',
                    'text_override': 'loyalty.reward.description_point_b_exp',
                    'block_override': (
                        'loyalty.details.block_point_b_by_priority'
                    ),
                },
            },
        },
    }
