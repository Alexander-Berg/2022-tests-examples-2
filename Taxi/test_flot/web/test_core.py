import pytest


@pytest.mark.parametrize(
    'login,body,status,expected_data',
    [
        (
            '123',
            {'code': 'CoreType', 'name': 'TestTypeName'},
            400,
            {
                'code': 'Creating Error',
                'message': (
                    'Error Creating Entity CoreType, Exception class = '
                    'UniqueViolationError, Error =  duplicate key value '
                    'violates unique constraint "type_ix_code"\n'
                    'DETAIL:  Key (code)=(CoreType) already exists.'
                ),
            },
        ),
        (
            '345',
            {'code': 'TestType', 'name': 'TestTypeName'},
            201,
            {'code': 'TestType', 'name': 'TestTypeName'},
        ),
    ],
)
async def test_core_type_register(
        web_context, web_app_client, login, body, status, expected_data,
):
    async with web_context.pg.master_pool.acquire() as conn:
        await conn.execute(
            """do $$
declare
  Type_TypeUID uuid;
begin
  select uuid_generate_v4() into Type_TypeUID;
  insert into core.type(
    uid
   ,code
   ,name
  )
  select
     Type_TypeUID
    ,'CoreType'
    ,'Types'
  where not exists(select * from core.type where code = 'CoreType');
  insert into core.object(
     uid
    ,type_uid
    ,creator_id
    ,create_date
    ,updator_id
    ,update_date
  )
  select
     Type_TypeUID
    ,Type_TypeUID
    ,1120000000595835
    ,now()
    ,1120000000595835
    ,now()
    where not exists(select * from core.object as o
                     left join core.type as t on t.uid = o.type_uid
                     where t.code = 'CoreType');
end
$$;""",
        )
    response = await web_app_client.post(
        '/core/type/register', headers={'X-Yandex-UID': login}, json=body,
    )
    assert response.status == status

    content = await response.json()

    if response.status == 201:
        expected_data.update({'uid': content['uid']})
        assert content == expected_data
    else:
        assert content == expected_data
