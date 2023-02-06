from tests_eats_billing_processor.tlog_info import helper


async def test_happy_path(tlog_info_fixtures):
    await (
        helper.TLogInfoTest()
        .request('123456-654321')
        .response(
            table_format=[
                helper.column_format(
                    column_name='Сумма без НДС',
                    column_number=3,
                    title=['amount', 'amount_with_vat'],
                ),
                helper.column_format(
                    column_name='Идентификатор клиента в балансе',
                    column_number=2,
                    title=['client_id'],
                ),
                helper.column_format(
                    column_name='Идентификатор фирмы',
                    column_number=1,
                    title=['firm_id'],
                ),
            ],
            docs=[
                helper.make_doc(
                    doc_id=123456,
                    transaction={'mvp': 'MSKc', 'firm_id': '32'},
                ),
                helper.make_doc(
                    doc_id=654321,
                    transaction={'mvp': 'MSKc123', 'firm_id': '322'},
                ),
            ],
        )
        .run(tlog_info_fixtures)
    )


async def test_fail(tlog_info_fixtures):
    await (
        helper.TLogInfoTest()
        .request('123456-654321')
        .async_fail()
        .run(tlog_info_fixtures)
    )
