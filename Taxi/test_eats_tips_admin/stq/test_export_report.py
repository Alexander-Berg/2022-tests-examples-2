from eats_tips_admin.stq import export_report


async def test_task(stq3_context):
    await export_report.task(stq3_context, 1, 'test')
