import copy
import functools

import pytest

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from persey_labs_plugins import *  # noqa: F403 F401


def pgify_arg(arg):
    if isinstance(arg, list):
        return arg
    if arg is None:
        return 'NULL'
    if arg is True:
        return 'TRUE'
    if arg is False:
        return 'FALSE'
    return repr(arg)


def pgify_args(start_with=1):
    def decorator(func):
        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            args_untouched = args[:start_with]
            args_pgified = map(pgify_arg, args[start_with:])
            kwargs_pgified = {name: pgify_arg(kwargs[name]) for name in kwargs}
            return func(*args_untouched, *args_pgified, **kwargs_pgified)

        return wrapped

    return decorator


class DbController:
    def __init__(self, pgsql, load_json):
        self.db = pgsql['persey_labs']
        self.load_json = load_json
        self.cursor = self.db.cursor()

        self.prefill()

    def exec_fetchall(self, query):
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return rows

    def exec_fetchid(self, query):
        return self.exec_fetchall(query)[0][0]

    def execute(self, query):
        self.cursor.execute(query)

    def add_contact(self, phone, email, web_site=None):
        web_site = f'\'{web_site}\'' if web_site is not None else 'NULL'
        query = f"""
        INSERT INTO persey_labs.contacts
            (phone, email, web_site)
        VALUES
            ('{phone}', '{email}', {web_site})
        RETURNING id;
    """
        return self.exec_fetchid(query)

    def add_billing_info(self):
        query = """
        INSERT INTO persey_labs.billing_infos
            (legal_name_short, legal_name_full, OGRN,
            legal_address, postal_address, web_license_resource,
            BIK, settlement_account, contract_start_dt, partner_uid,
            partner_commission, contract_id)
        VALUES
            ('my_entity_lab', 'my_awesome_entity_lab',
            'ogrn', 'there', 'right there', 'www.license.com',
            'bik', 'what is that', 'date', 'uid', '2.73', '321')
        RETURNING id;
    """
        return self.exec_fetchid(query)

    @pgify_args()
    def add_lab_entity(
            self,
            entity_id,
            contact_id,
            billing_info_id,
            employee_tests_threshold='NULL',
            test_kind='NULL',
            test_kinds='NULL',
            is_active='TRUE',
            custom_employee_address='FALSE',
            taxi_corp_id='\'123456\'',
    ):
        query = f"""
        INSERT INTO persey_labs.lab_entities
            (id, taxi_corp_id, contacts, communication_name, contact_id,
             billing_info_id, employee_tests_threshold, test_kind, is_active,
             custom_employee_address)
        VALUES
            ({entity_id}, {taxi_corp_id}, 'some contacts', 'comname',
             {contact_id}, {billing_info_id},
             {employee_tests_threshold}, {test_kind}, {is_active},
             {custom_employee_address})
        RETURNING id;
    """
        entity_id = self.exec_fetchid(query)
        if test_kinds != 'NULL':
            for test in test_kinds:
                query = f"""
            INSERT INTO persey_labs.lab_entity_tests
                (lab_entity_id, test_id)
            VALUES
                ('{entity_id}', '{test}');
        """
                self.execute(query)

        return entity_id

    @pgify_args()
    def add_address(
            self,
            lon,
            lat,
            locality_id,
            text='\'Somewhere\'',
            title='\'some\'',
            subtitle='\'where\'',
            comment='NULL',
    ):
        query = f"""
        INSERT INTO persey_labs.addresses
            (lon, lat, locality_id, full_text, title, subtitle, comment)
        VALUES
            ({lon}, {lat}, {locality_id}, {text}, {title}, {subtitle},
             {comment})
        RETURNING id;
    """
        return self.exec_fetchid(query)

    def add_lab_contacts(self, name, contact_id):
        query = f"""
        INSERT INTO persey_labs.lab_contact_persons
            ("name", contact_id)
        VALUES
            ('{name}', {contact_id})
        RETURNING id;
    """
        return self.exec_fetchid(query)

    @pgify_args()
    def add_lab(
            self,
            lab_id,
            entity_id,
            name,
            tests_per_day,
            contact_id,
            address_id,
            contact_person_id,
    ):
        query = f"""
        INSERT INTO persey_labs.labs
                (id, lab_entity_id, is_active, "name", description,
                tests_per_day,
                contacts, contact_id, address_id, contact_person_id)
        VALUES
            ({lab_id}, {entity_id}, 'TRUE', {name},
            'some description', {tests_per_day},
            'some contacts', {contact_id}, {address_id}, {contact_person_id});
    """
        self.execute(query)

    def load_address(self, address):
        address['lon'], address['lat'] = address['position']
        del address['position']
        return self.add_address(**address)

    def load_labs(self, entity_id, labs):
        for lab in labs:
            lab_id = lab['id']
            name = lab['name']
            address = lab['address']
            tests_per_day = lab['tests_per_day']
            address_id = self.load_address(address)
            self.add_lab(
                lab_id,
                entity_id,
                name,
                tests_per_day,
                self.contacts_id,
                address_id,
                self.c_p_id,
            )

    def load_lab_entities(self, lab_entites):
        for entity_id, entity_data in lab_entites.items():
            assert 'entity_id' not in entity_data
            entity_data['entity_id'] = entity_id
            branches = entity_data['branches']
            del entity_data['branches']
            entity_data['contact_id'] = self.l_e_contacts_id
            entity_data['billing_info_id'] = self.l_e_billing_id
            self.add_lab_entity(**entity_data)
            self.load_labs(entity_id, branches)

    def prefill(self):
        self.l_e_contacts_id = self.add_contact(
            '+77778887766',
            'entity_lab@yandex.ru',
            'www.my_main_lab@yandex.ru',
        )
        self.l_e_billing_id = self.add_billing_info()
        self.c_p_contacts_id = self.add_contact(
            '+79998887766', 'mail@yandex.ru',
        )
        self.c_p_id = self.add_lab_contacts(
            'Ivanov Ivan', self.c_p_contacts_id,
        )
        self.contacts_id = self.add_contact(
            '+78888887766', 'mail@yandex.ru', 'wwww.my_lab.ru',
        )

    @pgify_args()
    def add_person_info(self, firstname, surname, middlename='NULL'):
        return self.exec_fetchid(
            f"""
            INSERT INTO persey_labs.person_infos
                (firstname, surname, middlename)
            VALUES
                ({firstname}, {surname}, {middlename})
            RETURNING id
        """,
        )

    @pgify_args()
    def add_employee(
            self,
            lab_id,
            yandex_login,
            address_id='1',
            is_active='TRUE',
            person_info_id='NULL',
            contact_id='NULL',
    ):
        return self.exec_fetchid(
            f"""
            INSERT INTO persey_labs.lab_employees
                (lab_id, yandex_login, is_active, address_id, person_info_id,
                contact_id)
            VALUES
                ({lab_id}, {yandex_login}, {is_active}, {address_id},
                 {person_info_id}, {contact_id})
            RETURNING id
        """,
        )

    @pgify_args()
    def add_shift(
            self,
            employee_id,
            start_time,
            finish_time,
            taxi_order_state='\'planned\'',
            taxi_order_id='NULL',
            selected_tests='NULL',
    ):
        shift_id = self.exec_fetchid(
            f"""
                INSERT INTO persey_labs.lab_employee_shifts
                    (lab_employee_id, start_time, finish_time, taxi_order_id,
                     taxi_order_state)
                VALUES
                    ({employee_id}, {start_time}, {finish_time},
                     {taxi_order_id}, {taxi_order_state})
                RETURNING id
            """,
        )
        if selected_tests != 'NULL':
            for test in selected_tests:
                query = f"""
            INSERT INTO persey_labs.shift_tests
                (shift_id, test_id)
            VALUES
                ('{shift_id}', '{test}');
        """
                self.execute(query)

        return shift_id

    def load_shifts(self, employee_id, shifts):
        for shift in shifts:
            self.add_shift(employee_id, **shift)

    def load_employees(self, lab_id, employees):
        if isinstance(lab_id, list):
            for lab in lab_id:
                self.load_employees(lab, copy.deepcopy(employees))
            return

        for employee in employees:
            address = employee['address']
            del employee['address']
            employee['address_id'] = self.load_address(address)

            if 'person_info' in employee:
                person_info = employee['person_info']
                del employee['person_info']
                employee['person_info_id'] = self.add_person_info(
                    **person_info,
                )

            if 'contacts' in employee:
                contacts = employee['contacts']
                del employee['contacts']
                employee['contact_id'] = self.add_contact(**contacts)

            employee['yandex_login'] = employee['yandex_login'].format(
                lab_id=lab_id,
            )

            if 'address' in employee:
                address = employee['address']
                del employee['address']
                employee['address_id'] = self.add_address(**address)

            shifts = []
            if 'shifts' in employee:
                shifts = employee['shifts']
                del employee['shifts']

            employee_id = self.add_employee(lab_id, **employee)

            self.load_shifts(employee_id, shifts)


@pytest.fixture
async def fill_labs(pgsql, load_json):
    ctl = DbController(pgsql, load_json)
    return ctl
