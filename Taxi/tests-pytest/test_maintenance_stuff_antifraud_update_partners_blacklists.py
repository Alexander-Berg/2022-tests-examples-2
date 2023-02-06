import contextlib
import datetime
import pytest

from taxi.core import async
from taxi.core import db
from taxi_maintenance.stuff import antifraud_update_partners_blacklists


@pytest.mark.parametrize(
    'last_updated, mapper_name, yt_fixture, expected_yt_tmp_table', [
        (
            datetime.datetime(2021, 10, 11, 12, 0, 0),
            '_CompaniesListMapper',
            [
                {
                    'id': '0013X00002YEYDRQA5',
                    'doc': {
                        'TIN__c': '7325113987',
                        'Blacklist__c': 'Major Fraud',
                        'LongName__c': 'Full Name 1',
                        'Name': 'Name 1',
                        'Phone': '4b0020dcbc6c4cae905847c7e61dd4d0'
                    },
                    'utc_updated_dttm': '2021-10-11 12:45:00',
                },
            ],
            [
                {
                    'id': '0013X00002YEYDRQA5',
                    'in_blacklist': True,
                    'inns': [7325113987],
                    'full_names': [
                        'Full Name 1',
                    ],
                    'short_names': [
                        'Name 1',
                    ],
                    'phones': [],
                    'updated': '2021-10-11T12:45:00',
                },
            ],
        ),
        (
            datetime.datetime(2021, 10, 11, 12, 0, 0),
            '_CompaniesListMapper',
            [
                {
                    'id': '0013X00002YEtpsQAD', 'utc_updated_dttm': '2021-10-11 11:59:59',
                },
                {
                    'id': '0013X00002YGFowQAH', 'utc_updated_dttm': '2021-10-11 12:00:00',
                },
                {
                    'id': '0013X00002YlsbeQAB', 'utc_updated_dttm': '2021-10-11 11:59:59',
                },
            ],
            [
                {
                    'id': '0013X00002YGFowQAH', 'in_blacklist': False,
                    'inns': [], 'full_names': [], 'short_names': [],
                    'phones': [], 'updated': '2021-10-11T12:00:00',
                },
            ],
        ),
        (
            datetime.datetime(2021, 10, 11, 12, 0, 0),
            '_CompaniesListMapper',
            [
                {
                    'id': '0013X00002YEtpsQAD',
                    'doc': {
                        'TIN__c': '7325113987',
                    },
                    'utc_updated_dttm': '2021-10-11T12:00:01',
                },
                {
                    'id': '0013X00002YGFowQAH',
                    'doc': {
                        'TIN__c': 5249156189,
                    },
                    'utc_updated_dttm': '2021-10-11T12:00:02',
                },
                {
                    'id': '0013X00002YlsbeQAB',
                    'doc': {
                        'TIN__c': None,
                    },
                    'utc_updated_dttm': '2021-10-11T12:00:03',
                },
            ],
            [
                {
                    'id': '0013X00002YEtpsQAD', 'in_blacklist': False,
                    'inns': [7325113987], 'full_names': [], 'short_names': [],
                    'phones': [], 'updated': '2021-10-11T12:00:01',
                },
                {
                    'id': '0013X00002YGFowQAH', 'in_blacklist': False,
                    'inns': [5249156189], 'full_names': [], 'short_names': [],
                    'phones': [], 'updated': '2021-10-11T12:00:02',
                },
                {
                    'id': '0013X00002YlsbeQAB', 'in_blacklist': False,
                    'inns': [], 'full_names': [], 'short_names': [],
                    'phones': [], 'updated': '2021-10-11T12:00:03',
                },
            ],
        ),
        (
            datetime.datetime(2021, 10, 11, 12, 0, 0),
            '_CompaniesListMapper',
            [
                {
                    'id': '0013X00002YEtpsQAD',
                    'doc': {
                        'LongName__c': 'Full Name',
                    },
                    'utc_updated_dttm': '2021-10-11T12:00:01',
                },
                {
                    'id': '0013X00002YGFowQAH',
                    'doc': {
                        'Name': 5249156189,
                    },
                    'utc_updated_dttm': '2021-10-11T12:00:02',
                },
                {
                    'id': '0013X00002YlsbeQAB',
                    'doc': {
                        'LongName__c': None,
                    },
                    'utc_updated_dttm': '2021-10-11T12:00:03',
                },
                {
                    'id': '0013X00002XNbuXQAT',
                    'doc': {
                        'Name': '',
                    },
                    'utc_updated_dttm': '2021-10-11T12:00:04',
                },
            ],
            [
                {
                    'id': '0013X00002YEtpsQAD', 'in_blacklist': False,
                    'inns': [], 'full_names': ['Full Name'], 'short_names': [],
                    'phones': [], 'updated': '2021-10-11T12:00:01',
                },
                {
                    'id': '0013X00002YGFowQAH', 'in_blacklist': False,
                    'inns': [], 'full_names': [], 'short_names': ['5249156189'],
                    'phones': [], 'updated': '2021-10-11T12:00:02',
                },
                {
                    'id': '0013X00002YlsbeQAB', 'in_blacklist': False,
                    'inns': [], 'full_names': [], 'short_names': [],
                    'phones': [], 'updated': '2021-10-11T12:00:03',
                },
                {
                    'id': '0013X00002XNbuXQAT', 'in_blacklist': False,
                    'inns': [], 'full_names': [], 'short_names': [],
                    'phones': [], 'updated': '2021-10-11T12:00:04',
                },
            ],
        ),
        (
            datetime.datetime(2021, 10, 11, 12, 0, 0),
            '_CompaniesListMapper',
            [
                {
                    'id': '0013X00002YEtpsQAD',
                    'doc': {
                        'Blacklist__c': '',
                    },
                    'utc_updated_dttm': '2021-10-11T12:00:01',
                },
                {
                    'id': '0013X00002YGFowQAH',
                    'doc': {
                        'Blacklist__c': 'No Payment',
                    },
                    'utc_updated_dttm': '2021-10-11T12:00:02',
                },
                {
                    'id': '0013X00002YlsbeQAB',
                    'doc': {
                        'Blacklist__c': 'Major Fraud',
                    },
                    'utc_updated_dttm': '2021-10-11T12:00:03',
                },
                {
                    'id': '0013X00002XNbuXQAT',
                    'doc': {
                        'Blacklist__c': 'Moderate Fraud',
                    },
                    'utc_updated_dttm': '2021-10-11T12:00:04',
                },
                {
                    'id': '0013X00002XNcD6QAL',
                    'doc': {
                        'Blacklist__c': None,
                    },
                    'utc_updated_dttm': '2021-10-11T12:00:05',
                },
            ],
            [
                {
                    'id': '0013X00002YEtpsQAD', 'in_blacklist': False,
                    'inns': [], 'full_names': [], 'short_names': [],
                    'phones': [], 'updated': '2021-10-11T12:00:01',
                },
                {
                    'id': '0013X00002YGFowQAH', 'in_blacklist': False,
                    'inns': [], 'full_names': [], 'short_names': [],
                    'phones': [], 'updated': '2021-10-11T12:00:02',
                },
                {
                    'id': '0013X00002YlsbeQAB', 'in_blacklist': True,
                    'inns': [], 'full_names': [], 'short_names': [],
                    'phones': [], 'updated': '2021-10-11T12:00:03',
                },
                {
                    'id': '0013X00002XNbuXQAT', 'in_blacklist': False,
                    'inns': [], 'full_names': [], 'short_names': [],
                    'phones': [], 'updated': '2021-10-11T12:00:04',
                },
                {
                    'id': '0013X00002XNcD6QAL', 'in_blacklist': False,
                    'inns': [], 'full_names': [], 'short_names': [],
                    'phones': [], 'updated': '2021-10-11T12:00:05',
                },
            ],
        ),
        (
            datetime.datetime(2021, 10, 11, 12, 0, 0),
            '_CompaniesListMapper',
            [
                {
                    'id': '0013X00002YEtpsQAD',
                    'doc': None,
                    'utc_updated_dttm': '2021-10-11T12:00:01',
                },
                {
                    'id': '0013X00002YGFowQAH',
                    'doc': '',
                    'utc_updated_dttm': '2021-10-11T12:00:02',
                },
                {
                    'id': '0013X00002YlsbeQAB',
                    'doc': 1,
                    'utc_updated_dttm': '2021-10-11T12:00:03',
                },
                {
                    'id': '0013X00002XNbuXQAT',
                    'doc': '',
                    'utc_updated_dttm': '2021-10-11T12:00:04',
                },
                {
                    'id': '0013X00002XNcD6QAL',
                    'utc_updated_dttm': '2021-10-11T12:00:05',
                },
            ],
            [
                {
                    'id': '0013X00002YEtpsQAD', 'in_blacklist': False,
                    'inns': [], 'full_names': [], 'short_names': [],
                    'phones': [], 'updated': '2021-10-11T12:00:01',
                },
                {
                    'id': '0013X00002YGFowQAH', 'in_blacklist': False,
                    'inns': [], 'full_names': [], 'short_names': [],
                    'phones': [], 'updated': '2021-10-11T12:00:02',
                },
                {
                    'id': '0013X00002YlsbeQAB', 'in_blacklist': False,
                    'inns': [], 'full_names': [], 'short_names': [],
                    'phones': [], 'updated': '2021-10-11T12:00:03',
                },
                {
                    'id': '0013X00002XNbuXQAT', 'in_blacklist': False,
                    'inns': [], 'full_names': [], 'short_names': [],
                    'phones': [], 'updated': '2021-10-11T12:00:04',
                },
                {
                    'id': '0013X00002XNcD6QAL', 'in_blacklist': False,
                    'inns': [], 'full_names': [], 'short_names': [],
                    'phones': [], 'updated': '2021-10-11T12:00:05',
                },
            ],
        ),

        (
            datetime.datetime(2021, 10, 11, 12, 0, 0),
            '_ContactsListMapper',
            [
                {
                    'id': '0033X00002zF2AMQA0',
                    'doc': {
                        'Blacklist__c': 'Major Fraud',
                        'Email': 'contact@example.com',
                        'MobilePhone': 79161234567,
                        'OtherEmail1__c': 'contact1@example.com',
                        'OtherEmail2__c': 'contact2@example.com',
                        'OtherPhone': '+7(903) 987-65-43',
                        'Phone': '4b0020dcbc6c4cae905847c7e61dd4d0',
                    },
                    'utc_updated_dttm': '2021-10-11 12:45:00',
                },
            ],
            [
                {
                    'id': '0033X00002zF2AMQA0',
                    'in_blacklist': True,
                    'emails': [
                        'contact@example.com',
                        'contact1@example.com',
                        'contact2@example.com',
                    ],
                    'phones': [
                        79161234567,
                        79039876543,
                    ],
                    'updated': '2021-10-11T12:45:00',
                },
            ],
        ),
        (
            datetime.datetime(2021, 10, 11, 12, 0, 0),
            '_ContactsListMapper',
            [
                {
                    'id': '0013X00002YEtpsQAD', 'utc_updated_dttm': '2021-10-11 11:59:59',
                },
                {
                    'id': '0013X00002YGFowQAH', 'utc_updated_dttm': '2021-10-11 12:00:00',
                },
                {
                    'id': '0013X00002YlsbeQAB', 'utc_updated_dttm': '2021-10-11 11:59:59',
                },
            ],
            [
                {
                    'id': '0013X00002YGFowQAH', 'in_blacklist': False,
                    'emails': [], 'phones': [], 'updated': '2021-10-11T12:00:00',
                },
            ],
        ),
        (
            datetime.datetime(2021, 10, 11, 12, 0, 0),
            '_ContactsListMapper',
            [
                {
                    'id': '0013X00002YEtpsQAD',
                    'doc': {
                        'Email': 'contact@example.com',
                    },
                    'utc_updated_dttm': '2021-10-11T12:00:01',
                },
                {
                    'id': '0013X00002YGFowQAH',
                    'doc': {
                        'Email': None,
                        'OtherEmail1__c': 'another@example.com',
                    },
                    'utc_updated_dttm': '2021-10-11T12:00:02',
                },
                {
                    'id': '0013X00002YlsbeQAB',
                    'doc': {
                        'OtherEmail2__c': None,
                    },
                    'utc_updated_dttm': '2021-10-11T12:00:03',
                },
                {
                    'id': '0013X00002XNbuXQAT',
                    'doc': {
                        'Email': '',
                    },
                    'utc_updated_dttm': '2021-10-11T12:00:04',
                },
            ],
            [
                {
                    'id': '0013X00002YEtpsQAD', 'in_blacklist': False,
                    'emails': ['contact@example.com'], 'phones': [], 'updated': '2021-10-11T12:00:01',
                },
                {
                    'id': '0013X00002YGFowQAH', 'in_blacklist': False,
                    'emails': ['another@example.com'], 'phones': [], 'updated': '2021-10-11T12:00:02',
                },
                {
                    'id': '0013X00002YlsbeQAB', 'in_blacklist': False,
                    'emails': [], 'phones': [], 'updated': '2021-10-11T12:00:03',
                },
                {
                    'id': '0013X00002XNbuXQAT', 'in_blacklist': False,
                    'emails': [], 'phones': [], 'updated': '2021-10-11T12:00:04',
                },
            ],
        ),
        (
            datetime.datetime(2021, 10, 11, 12, 0, 0),
            '_ContactsListMapper',
            [
                {
                    'id': '0013X00002YEtpsQAD',
                    'doc': {
                        'Phone': '+79261234567',
                    },
                    'utc_updated_dttm': '2021-10-11T12:00:01',
                },
                {
                    'id': '0013X00002YGFowQAH',
                    'doc': {
                        'MobilePhone': '7 (909) 987-65-43',
                        'OtherPhone': None,
                        'Phone': '79261234567',
                    },
                    'utc_updated_dttm': '2021-10-11T12:00:02',
                },
                {
                    'id': '0013X00002YlsbeQAB',
                    'doc': {
                        'OtherPhone': 79164561298,
                        'Phone': '',
                    },
                    'utc_updated_dttm': '2021-10-11T12:00:03',
                },
                {
                    'id': '0013X00002XNbuXQAT',
                    'doc': {
                        'MobilePhone': None,
                        'OtherPhone': '',
                    },
                    'utc_updated_dttm': '2021-10-11T12:00:04',
                },
            ],
            [
                {
                    'id': '0013X00002YEtpsQAD', 'in_blacklist': False,
                    'emails': [], 'phones': [79261234567], 'updated': '2021-10-11T12:00:01',
                },
                {
                    'id': '0013X00002YGFowQAH', 'in_blacklist': False,
                    'emails': [], 'phones': [79099876543, 79261234567], 'updated': '2021-10-11T12:00:02',
                },
                {
                    'id': '0013X00002YlsbeQAB', 'in_blacklist': False,
                    'emails': [], 'phones': [79164561298], 'updated': '2021-10-11T12:00:03',
                },
                {
                    'id': '0013X00002XNbuXQAT', 'in_blacklist': False,
                    'emails': [], 'phones': [], 'updated': '2021-10-11T12:00:04',
                },
            ],
        ),
        (
            datetime.datetime(2021, 10, 11, 12, 0, 0),
            '_ContactsListMapper',
            [
                {
                    'id': '0013X00002YEtpsQAD',
                    'doc': {
                        'Blacklist__c': '',
                    },
                    'utc_updated_dttm': '2021-10-11T12:00:01',
                },
                {
                    'id': '0013X00002YGFowQAH',
                    'doc': {
                        'Blacklist__c': 'No Payment',
                    },
                    'utc_updated_dttm': '2021-10-11T12:00:02',
                },
                {
                    'id': '0013X00002YlsbeQAB',
                    'doc': {
                        'Blacklist__c': 'Major Fraud',
                    },
                    'utc_updated_dttm': '2021-10-11T12:00:03',
                },
                {
                    'id': '0013X00002XNbuXQAT',
                    'doc': {
                        'Blacklist__c': 'Moderate Fraud',
                    },
                    'utc_updated_dttm': '2021-10-11T12:00:04',
                },
                {
                    'id': '0013X00002XNcD6QAL',
                    'doc': {
                        'Blacklist__c': None,
                    },
                    'utc_updated_dttm': '2021-10-11T12:00:05',
                },
            ],
            [
                {
                    'id': '0013X00002YEtpsQAD', 'in_blacklist': False,
                    'emails': [], 'phones': [], 'updated': '2021-10-11T12:00:01',
                },
                {
                    'id': '0013X00002YGFowQAH', 'in_blacklist': False,
                    'emails': [], 'phones': [], 'updated': '2021-10-11T12:00:02',
                },
                {
                    'id': '0013X00002YlsbeQAB', 'in_blacklist': True,
                    'emails': [], 'phones': [], 'updated': '2021-10-11T12:00:03',
                },
                {
                    'id': '0013X00002XNbuXQAT', 'in_blacklist': False,
                    'emails': [], 'phones': [], 'updated': '2021-10-11T12:00:04',
                },
                {
                    'id': '0013X00002XNcD6QAL', 'in_blacklist': False,
                    'emails': [], 'phones': [], 'updated': '2021-10-11T12:00:05',
                },
            ],
        ),
        (
            datetime.datetime(2021, 10, 11, 12, 0, 0),
            '_ContactsListMapper',
            [
                {
                    'id': '0013X00002YEtpsQAD',
                    'doc': None,
                    'utc_updated_dttm': '2021-10-11T12:00:01',
                },
                {
                    'id': '0013X00002YGFowQAH',
                    'doc': '',
                    'utc_updated_dttm': '2021-10-11T12:00:02',
                },
                {
                    'id': '0013X00002YlsbeQAB',
                    'doc': 1,
                    'utc_updated_dttm': '2021-10-11T12:00:03',
                },
                {
                    'id': '0013X00002XNbuXQAT',
                    'doc': '',
                    'utc_updated_dttm': '2021-10-11T12:00:04',
                },
                {
                    'id': '0013X00002XNcD6QAL',
                    'utc_updated_dttm': '2021-10-11T12:00:05',
                },
            ],
            [
                {
                    'id': '0013X00002YEtpsQAD', 'in_blacklist': False,
                    'emails': [], 'phones': [], 'updated': '2021-10-11T12:00:01',
                },
                {
                    'id': '0013X00002YGFowQAH', 'in_blacklist': False,
                    'emails': [], 'phones': [], 'updated': '2021-10-11T12:00:02',
                },
                {
                    'id': '0013X00002YlsbeQAB', 'in_blacklist': False,
                    'emails': [], 'phones': [], 'updated': '2021-10-11T12:00:03',
                },
                {
                    'id': '0013X00002XNbuXQAT', 'in_blacklist': False,
                    'emails': [], 'phones': [], 'updated': '2021-10-11T12:00:04',
                },
                {
                    'id': '0013X00002XNcD6QAL', 'in_blacklist': False,
                    'emails': [], 'phones': [], 'updated': '2021-10-11T12:00:05',
                },
            ],
        ),
    ],
    ids=[
        'company_basic_record',
        'company_update_filtering',
        'company_tin_values',
        'company_name_values',
        'company_blacklist_values',
        'company_wrong_doc',

        'contact_basic_record',
        'contact_update_filtering',
        'contact_email_values',
        'contact_phone_values',
        'contact_blacklist_values',
        'contact_wrong_doc',
    ]
)
@pytest.mark.asyncenv('blocking')
def test_list_mapper(
        last_updated, mapper_name, yt_fixture, expected_yt_tmp_table):
    mapper = getattr(antifraud_update_partners_blacklists, mapper_name)(
        last_updated,
    )

    yt_tmp_table = list()
    for row in yt_fixture:
        for new_row in mapper(row):
            yt_tmp_table.append(new_row)

    assert yt_tmp_table == expected_yt_tmp_table


@pytest.mark.parametrize(
    'yt_fixture, expected_mongo', [
        (
            {
                'companies_table': [
                    {
                        'id': '1',
                        'in_blacklist': True,
                        'inns': [100500111],
                        'full_names': ['Full Name 1.2'],
                        'short_names': [],
                        'phones': [],
                        'updated': '2018-07-09T12:30:00',
                    },
                    {
                        'id': '2',
                        'in_blacklist': False,
                        'inns': [100500112],
                        'full_names': ['Full Name 2'],
                        'short_names': [],
                        'phones': [],
                        'updated': '2018-07-09T12:35:00',
                    },
                ],
                'contacts_table': [],
            },
            {
                'companies': [
                    {
                        '_id': '1',
                        'inns': [100500111],
                        'full_names': ['Full Name 1.2'],
                        'short_names': [],
                        'phones': [],
                    },
                ],
                'contacts': [],
                'metainfo': {
                    'companies': {
                        '_id': 'companies',
                        'last_updated':
                            datetime.datetime(2018, 7, 9, 12, 35, 0),
                    },
                    'contacts': {
                        '_id': 'contacts',
                        'last_updated':
                            datetime.datetime(2018, 7, 9, 12, 0, 0),
                    },
                },
            },
        ),
        (
            {
                'companies_table': [
                    {
                        'id': '3',
                        'in_blacklist': True,
                        'inns': [100500113],
                        'full_names': ['Full Name 3'],
                        'short_names': [],
                        'phones': [],
                        'updated': '2018-07-09T12:00:00',
                    },
                ],
                'contacts_table': [],
            },
            {
                'companies': [
                    {
                        '_id': '1', 'inns': [100500111],
                        'full_names': ['Full Name 1'], 'short_names': [],
                        'phones': [],
                    },
                    {
                        '_id': '2', 'inns': [100500112],
                        'full_names': ['Full Name 2'], 'short_names': [],
                        'phones': [],
                    },
                    {
                        '_id': '3', 'inns': [100500113],
                        'full_names': ['Full Name 3'], 'short_names': [],
                        'phones': [],
                    },
                ],
                'contacts': [],
                'metainfo': {
                    'companies': {
                        '_id': 'companies',
                        'last_updated':
                            datetime.datetime(2018, 7, 9, 12, 0, 0),
                    },
                    'contacts': {
                        '_id': 'contacts',
                        'last_updated':
                            datetime.datetime(2018, 7, 9, 12, 0, 0),
                    },
                },
            },
        ),
        (
            {
                'companies_table': [],
                'contacts_table': [
                    {
                        'id': '1',
                        'in_blacklist': True,
                        'emails': ['azaza@mailserver.ru'],
                        'phones': [79261234567],
                        'updated': '2018-07-09T11:00:00',
                    },
                ],
            },
            {
                'companies': [
                    {
                        '_id': '1', 'inns': [100500111],
                        'full_names': ['Full Name 1'], 'short_names': [],
                        'phones': [],
                    },
                    {
                        '_id': '2', 'inns': [100500112],
                        'full_names': ['Full Name 2'], 'short_names': [],
                        'phones': [],
                    },
                ],
                'contacts': [
                    {
                        '_id': '1', 'emails': ['azaza@mailserver.ru'],
                        'phones': [79261234567],
                    },
                ],
                'metainfo': {
                    'contacts': {
                        '_id': 'contacts',
                        'last_updated':
                            datetime.datetime(2018, 7, 9, 12, 0, 0),
                    },
                },
            },
        ),
        (
            {
                'companies_table': [
                    {
                        'id': '1',
                        'in_blacklist': True,
                        'inns': [100500111],
                        'full_names': [],
                        'short_names': ['Short Name 1', 'Short Name 2'],
                        'phones': [79261234567, 79261234568, 79261234569],
                        'updated': '2018-07-09T11:00:00',
                    },
                ],
                'contacts_table': [],
            },
            {
                'companies': [
                    {
                        '_id': '1',
                        'inns': [100500111],
                        'full_names': [],
                        'short_names': ['Short Name 1', 'Short Name 2'],
                        'phones': [79261234567, 79261234568, 79261234569],
                    },
                    {
                        '_id': '2',
                        'inns': [100500112],
                        'full_names': ['Full Name 2'],
                        'short_names': [],
                        'phones': [],
                    },
                ],
                'contacts': [],
                'metainfo': {
                    'companies': {
                        '_id': 'companies',
                        'last_updated':
                            datetime.datetime(2018, 7, 9, 11, 0, 0),
                    },
                    'contacts': {
                        '_id': 'contacts',
                        'last_updated':
                            datetime.datetime(2018, 7, 9, 12, 0, 0),
                    },
                },
            },
        ),
        (
            {
                'companies_table': [
                    {
                        'id': '1', 'in_blacklist': False,
                    },
                    {
                        'id': '2', 'in_blacklist': False,
                    },
                ],
                'contacts_table': [],
            },
            {
                'companies': [],
                'contacts': [],
                'metainfo': {
                    'contacts': {
                        '_id': 'contacts',
                        'last_updated':
                            datetime.datetime(2018, 7, 9, 12, 0, 0),
                    },
                },
            },
        ),
        (
            {
                'companies_table': [],
                'contacts_table': [
                    {
                        'id': '1', 'in_blacklist': False,
                        'updated': '2018-07-09T13:00:00',
                    },
                ],
            },
            {
                'companies': [
                    {
                        '_id': '1', 'inns': [100500111],
                        'full_names': ['Full Name 1'], 'short_names': [],
                        'phones': [],
                    },
                    {
                        '_id': '2', 'inns': [100500112],
                        'full_names': ['Full Name 2'], 'short_names': [],
                        'phones': [],
                    },
                ],
                'contacts': [],
                'metainfo': {
                    'contacts': {
                        '_id': 'contacts',
                        'last_updated':
                            datetime.datetime(2018, 7, 9, 13, 0, 0),
                    },
                },
            },
        ),
    ]
)
@pytest.mark.filldb()
@pytest.mark.now('2018-07-09 13:00:00')
@pytest.mark.config(AFS_UPDATE_PARTNERS_BLACKLISTS=True)
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_update_partners_blacklists(
        yt_fixture, expected_mongo, monkeypatch):
    monkeypatch.setattr(
        'taxi.external.yt_wrapper.hahn_dwh_env',
        DummyYtClient(yt_fixture),
    )

    yield antifraud_update_partners_blacklists.do_stuff(
        cron_start_time=datetime.datetime.utcnow(),
    )

    yield _check_mongo(expected_mongo)


class DummyYtClient(object):
    def __init__(self, yt_fixture):
        self._yt_fixture = yt_fixture
        self._yt_tables = ['companies_table', 'contacts_table']
        self._curr_table = 0

    @contextlib.contextmanager
    def TempTable(self):
        yield None

    def get_attribute(self, *args):
        return 0

    @contextlib.contextmanager
    def Transaction(self):
        yield None

    def run_map(self, *args, **kwargs):
        pass

    def TablePath(self, *args, **kwargs):
        return None

    def read_table(self, *args, **kwargs):
        table = self._yt_fixture[self._yt_tables[self._curr_table]]
        self._curr_table += 1
        return table


@async.inline_callbacks
def _check_mongo(expected):
    yield _check_mongo_data(
        db.antifraud_blacklists_companies, 'companies', expected,
    )
    yield _check_mongo_data(
        db.antifraud_blacklists_contacts, 'contacts', expected,
    )


@async.inline_callbacks
def _check_mongo_data(blacklist_db_collection, list_name, expected):
    expected_list = expected[list_name]

    for expected_list_item in expected_list:
        list_items = yield blacklist_db_collection.find(
            {'_id': expected_list_item['_id']}
        ).run()
        assert list_items
        for list_item in list_items:
            assert _without_dttm_fields(list_item) == expected_list_item

    count = yield blacklist_db_collection.count()
    assert count == len(expected_list)

    if list_name in expected['metainfo']:
        expected_metainfo = expected['metainfo'][list_name]

        metainfo = yield db.antifraud_blacklists_metainfo.find_one(
            {'_id': list_name},
        )
        assert _without_dttm_fields(metainfo) == expected_metainfo


def _without_dttm_fields(item):
    return {
        key: item[key] for key in item
        if key not in ('created', 'updated')
    }
