class Application:
    def __init__(self):
        self.application_id = None
        self.user_id_type = None
        self.user_id = None
        self.type = None
        self.multiple_success_status_allowed = None
        self.additional_params = None
        self.initiator = None


def select_application(pgsql, application_id):
    cursor = pgsql['bank_applications'].cursor()
    cursor.execute(
        (
            f'SELECT application_id, user_id_type, user_id, type, '
            f'multiple_success_status_allowed, additional_params, initiator '
            f'FROM bank_applications.applications '
            f'WHERE application_id = \'{application_id}\'::UUID'
        ),
    )

    applications = list(cursor)
    assert len(applications) == 1
    application = applications[0]

    res = Application()

    res.application_id = application[0]
    res.user_id_type = application[1]
    res.user_id = application[2]
    res.type = application[3]
    res.multiple_success_status_allowed = application[4]
    res.additional_params = application[5]
    res.initiator = application[6]

    return res
