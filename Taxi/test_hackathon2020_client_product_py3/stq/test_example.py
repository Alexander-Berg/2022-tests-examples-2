from hackathon2020_client_product_py3.stq import example


async def test_task(stq3_context):
    await example.task(stq3_context, 1, 'test')
