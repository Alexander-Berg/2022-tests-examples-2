TEMPLATES_CONFIG = {'max_templates_count': 5, 'max_answer_size': 256}


def make_response(templates):
    return {
        'meta': {
            'max_count': TEMPLATES_CONFIG['max_templates_count'],
            'max_size': TEMPLATES_CONFIG['max_answer_size'],
        },
        'templates': templates,
    }


def get_db_templates(pgsql, partner_id):
    cursor = pgsql['eats_place_rating'].cursor()
    cursor.execute(
        'SELECT template_id, template '
        'FROM eats_place_rating.feedback_answer_templates '
        'WHERE partner_id = %s::BIGINT '
        'ORDER BY template_id;',
        (partner_id,),
    )
    return [{'id': str(r[0]), 'text': r[1]} for r in cursor.fetchall()]
