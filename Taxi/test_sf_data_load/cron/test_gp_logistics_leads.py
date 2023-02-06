import datetime
import logging

import pytest

from sf_data_load.generated.cron import run_cron


logger = logging.getLogger(__name__)


@pytest.mark.config(
    SF_DATA_LOAD_SF_RULES=[
        {
            'source': 'GPLogisticLeads',
            'source_field': 'region',
            'sf_api_name': 'Region__c',
            'lookup_alias': 'logistics_from_gp_to_case',
            'load_period': 1,
        },
        {
            'source': 'GPLogisticLeads',
            'source_field': 'product',
            'sf_api_name': 'Product__c',
            'lookup_alias': 'logistics_from_gp_to_case',
            'load_period': 1,
        },
        {
            'source': 'GPLogisticLeads',
            'source_field': 'record_type_id',
            'sf_api_name': 'RecordTypeId',
            'lookup_alias': 'logistics_from_gp_to_case',
            'load_period': 1,
        },
        {
            'source': 'GPLogisticLeads',
            'source_field': 'origin',
            'sf_api_name': 'Origin',
            'lookup_alias': 'logistics_from_gp_to_case',
            'load_period': 1,
        },
        {
            'source': 'GPLogisticLeads',
            'source_field': 'deal_id',
            'sf_api_name': 'pd_id__c',
            'lookup_alias': 'logistics_from_gp_to_case',
            'load_period': 1,
        },
        {
            'source': 'GPLogisticLeads',
            'source_field': 'supplied_company',
            'sf_api_name': 'SuppliedCompany',
            'lookup_alias': 'logistics_from_gp_to_case',
            'load_period': 1,
        },
        {
            'source': 'GPLogisticLeads',
            'source_field': 'deal_title',
            'sf_api_name': 'Company_Full_Name__c',
            'lookup_alias': 'logistics_from_gp_to_case',
            'load_period': 1,
        },
        {
            'source': 'GPLogisticLeads',
            'source_field': 'city',
            'sf_api_name': 'City__c',
            'lookup_alias': 'logistics_from_gp_to_case',
            'load_period': 1,
        },
        {
            'source': 'GPLogisticLeads',
            'source_field': 'phone',
            'sf_api_name': 'SuppliedPhone',
            'lookup_alias': 'logistics_from_gp_to_case',
            'load_period': 1,
        },
        {
            'source': 'GPLogisticLeads',
            'source_field': 'email',
            'sf_api_name': 'SuppliedEmail',
            'lookup_alias': 'logistics_from_gp_to_case',
            'load_period': 1,
        },
        {
            'source': 'GPLogisticLeads',
            'source_field': 'inn',
            'sf_api_name': 'INN__c',
            'lookup_alias': 'logistics_from_gp_to_case',
            'load_period': 1,
        },
        {
            'source': 'GPLogisticLeads',
            'source_field': 'website',
            'sf_api_name': 'urlcompany__c',
            'lookup_alias': 'logistics_from_gp_to_case',
            'load_period': 1,
        },
    ],
    SF_DATA_LOAD_LOOKUPS={
        'logistics_from_gp_to_case': {
            'sf_org': 'b2b',
            'sf_object': 'Case',
            'source_key': 'deal_id',
            'create': True,
            'record_load_by_bulk': 0,
        },
    },
)
async def test_load_logistics_leads(cron_context, pgsql, mocked_time):
    async with cron_context.greenplum.get_pool() as pool:
        async with pool.acquire() as gp_conn:
            await gp_conn.execute(
                """
                CREATE SCHEMA IF NOT EXISTS snb_b2b;
                CREATE TABLE  IF NOT EXISTS
                snb_b2b.niksm_b2b_leads_for_taxi(
                    deal_id integer,
                    country text,
                    city text,
                    deal_title text,
                    inn text,
                    website text,
                    person_name text,
                    phone character varying,
                    email character varying,
                    record_date date,
                    add_date date,
                    pipeline_name text,
                    stage_name text
                )
            """,
            )
            data = [
                [
                    3260333,
                    'РФ',
                    'Москва',
                    'ООО Саске вернись в коноху',
                    '9723108468',
                    'http://www.naruto1love.ru',
                    'Хатаке Какаши',
                    '+7932123321',
                    'info@sasuke.pro',
                    datetime.date(2022, 6, 20),
                    datetime.datetime.now() - datetime.timedelta(15),
                    'ЗАПУСК И РАЗВИТИЕ',
                    'РАЗГОН',
                ],
                [
                    3223855,
                    'РФ',
                    'Москва',
                    'Azog / ООО Доставка орков',
                    '7728336506',
                    'https://azor.ru/',
                    'Громаш Адский Крик',
                    '+7 969 362-42-57',
                    'info@ozonair.ru',
                    datetime.date(2022, 6, 20),
                    datetime.datetime.now() - datetime.timedelta(15),
                    'САМОСТОЯТЕЛЬНЫЕ КЛИЕНТЫ',
                    'БЕЗ МЕНЕДЖЕРА',
                ],
                [
                    3290677,
                    'РФ',
                    'Москва',
                    'АрхиСталь / ООО АрхиСталь' * 10,
                    '5021018294',
                    'https://www.arhistal.ru/',
                    'Повелитель Стале Сплавов',
                    '+7 992 655-70-81',
                    '43144321@mail.ru',
                    datetime.date(2022, 6, 20),
                    datetime.datetime.now() - datetime.timedelta(15),
                    'ПОДКЛЮЧЕНИЕ',
                    'ПЕРЕГОВОРЫ',
                ],
            ]
            await gp_conn.copy_records_to_table(
                table_name='niksm_b2b_leads_for_taxi',
                schema_name='snb_b2b',
                records=data,
                columns=[
                    'deal_id',
                    'country',
                    'city',
                    'deal_title',
                    'inn',
                    'website',
                    'person_name',
                    'phone',
                    'email',
                    'record_date',
                    'add_date',
                    'pipeline_name',
                    'stage_name',
                ],
            )

    await run_cron.main(
        ['sf_data_load.crontasks.lead.logistics_from_pg', '-t', '0'],
    )

    cursor = pgsql['sf_data_load'].cursor()
    cursor.execute(
        """
        SELECT
            source_class_name,
            source_field,
            sf_api_field_name,
            lookup_alias,
            source_key,
            data_value,
            retries_count
        FROM sf_data_load.loading_fields
        WHERE lookup_alias = 'logistics_from_gp_to_case'
        ORDER BY source_key, source_field
    """,
    )

    assert cursor.fetchall() == [
        (
            'GPLogisticLeads',
            'city',
            'City__c',
            'logistics_from_gp_to_case',
            '3223855',
            'Москва',
            0,
        ),
        (
            'GPLogisticLeads',
            'deal_id',
            'pd_id__c',
            'logistics_from_gp_to_case',
            '3223855',
            '3223855',
            0,
        ),
        (
            'GPLogisticLeads',
            'deal_title',
            'Company_Full_Name__c',
            'logistics_from_gp_to_case',
            '3223855',
            'Azog / ООО Доставка орков',
            0,
        ),
        (
            'GPLogisticLeads',
            'email',
            'SuppliedEmail',
            'logistics_from_gp_to_case',
            '3223855',
            'info@ozonair.ru',
            0,
        ),
        (
            'GPLogisticLeads',
            'inn',
            'INN__c',
            'logistics_from_gp_to_case',
            '3223855',
            '7728336506',
            0,
        ),
        (
            'GPLogisticLeads',
            'origin',
            'Origin',
            'logistics_from_gp_to_case',
            '3223855',
            'Yandex Delivery',
            0,
        ),
        (
            'GPLogisticLeads',
            'phone',
            'SuppliedPhone',
            'logistics_from_gp_to_case',
            '3223855',
            '+7 969 362-42-57',
            0,
        ),
        (
            'GPLogisticLeads',
            'product',
            'Product__c',
            'logistics_from_gp_to_case',
            '3223855',
            'Taxi',
            0,
        ),
        (
            'GPLogisticLeads',
            'record_type_id',
            'RecordTypeId',
            'logistics_from_gp_to_case',
            '3223855',
            '0123X000000Zzw2QAC',
            0,
        ),
        (
            'GPLogisticLeads',
            'region',
            'Region__c',
            'logistics_from_gp_to_case',
            '3223855',
            'RF',
            0,
        ),
        (
            'GPLogisticLeads',
            'supplied_company',
            'SuppliedCompany',
            'logistics_from_gp_to_case',
            '3223855',
            'Azog / ООО Доставка орков',
            0,
        ),
        (
            'GPLogisticLeads',
            'website',
            'urlcompany__c',
            'logistics_from_gp_to_case',
            '3223855',
            'https://azor.ru/',
            0,
        ),
        (
            'GPLogisticLeads',
            'city',
            'City__c',
            'logistics_from_gp_to_case',
            '3260333',
            'Москва',
            0,
        ),
        (
            'GPLogisticLeads',
            'deal_id',
            'pd_id__c',
            'logistics_from_gp_to_case',
            '3260333',
            '3260333',
            0,
        ),
        (
            'GPLogisticLeads',
            'deal_title',
            'Company_Full_Name__c',
            'logistics_from_gp_to_case',
            '3260333',
            'ООО Саске вернись в коноху',
            0,
        ),
        (
            'GPLogisticLeads',
            'email',
            'SuppliedEmail',
            'logistics_from_gp_to_case',
            '3260333',
            'info@sasuke.pro',
            0,
        ),
        (
            'GPLogisticLeads',
            'inn',
            'INN__c',
            'logistics_from_gp_to_case',
            '3260333',
            '9723108468',
            0,
        ),
        (
            'GPLogisticLeads',
            'origin',
            'Origin',
            'logistics_from_gp_to_case',
            '3260333',
            'Yandex Delivery',
            0,
        ),
        (
            'GPLogisticLeads',
            'phone',
            'SuppliedPhone',
            'logistics_from_gp_to_case',
            '3260333',
            '+7932123321',
            0,
        ),
        (
            'GPLogisticLeads',
            'product',
            'Product__c',
            'logistics_from_gp_to_case',
            '3260333',
            'Taxi',
            0,
        ),
        (
            'GPLogisticLeads',
            'record_type_id',
            'RecordTypeId',
            'logistics_from_gp_to_case',
            '3260333',
            '0123X000000Zzw2QAC',
            0,
        ),
        (
            'GPLogisticLeads',
            'region',
            'Region__c',
            'logistics_from_gp_to_case',
            '3260333',
            'RF',
            0,
        ),
        (
            'GPLogisticLeads',
            'supplied_company',
            'SuppliedCompany',
            'logistics_from_gp_to_case',
            '3260333',
            'ООО Саске вернись в коноху',
            0,
        ),
        (
            'GPLogisticLeads',
            'website',
            'urlcompany__c',
            'logistics_from_gp_to_case',
            '3260333',
            'http://www.naruto1love.ru',
            0,
        ),
        (
            'GPLogisticLeads',
            'city',
            'City__c',
            'logistics_from_gp_to_case',
            '3290677',
            'Москва',
            0,
        ),
        (
            'GPLogisticLeads',
            'deal_id',
            'pd_id__c',
            'logistics_from_gp_to_case',
            '3290677',
            '3290677',
            0,
        ),
        (
            'GPLogisticLeads',
            'deal_title',
            'Company_Full_Name__c',
            'logistics_from_gp_to_case',
            '3290677',
            'АрхиСталь / ООО АрхиСтальАрхиСталь / ООО АрхиСтальАрхиСталь / ООО АрхиСтальАрхиСталь / ООО АрхиСтальАрхиСталь / ООО АрхиСтальАрхиСталь / ООО АрхиСтальАрхиСталь / ООО АрхиСтальАрхиСталь / ООО АрхиСтальАрхиСталь / ООО АрхиСтальАрхиСталь / ООО АрхиСталь',  # noqa: E501
            0,
        ),
        (
            'GPLogisticLeads',
            'email',
            'SuppliedEmail',
            'logistics_from_gp_to_case',
            '3290677',
            '43144321@mail.ru',
            0,
        ),
        (
            'GPLogisticLeads',
            'inn',
            'INN__c',
            'logistics_from_gp_to_case',
            '3290677',
            '5021018294',
            0,
        ),
        (
            'GPLogisticLeads',
            'origin',
            'Origin',
            'logistics_from_gp_to_case',
            '3290677',
            'Yandex Delivery',
            0,
        ),
        (
            'GPLogisticLeads',
            'phone',
            'SuppliedPhone',
            'logistics_from_gp_to_case',
            '3290677',
            '+7 992 655-70-81',
            0,
        ),
        (
            'GPLogisticLeads',
            'product',
            'Product__c',
            'logistics_from_gp_to_case',
            '3290677',
            'Taxi',
            0,
        ),
        (
            'GPLogisticLeads',
            'record_type_id',
            'RecordTypeId',
            'logistics_from_gp_to_case',
            '3290677',
            '0123X000000Zzw2QAC',
            0,
        ),
        (
            'GPLogisticLeads',
            'region',
            'Region__c',
            'logistics_from_gp_to_case',
            '3290677',
            'RF',
            0,
        ),
        (
            'GPLogisticLeads',
            'supplied_company',
            'SuppliedCompany',
            'logistics_from_gp_to_case',
            '3290677',
            'АрхиСталь / ООО АрхиСтальАрхиСталь / ООО АрхиСтальАрхиСталь / ООО АрхиСтальАрхиС',  # noqa: E501
            0,
        ),
        (
            'GPLogisticLeads',
            'website',
            'urlcompany__c',
            'logistics_from_gp_to_case',
            '3290677',
            'https://www.arhistal.ru/',
            0,
        ),
    ]