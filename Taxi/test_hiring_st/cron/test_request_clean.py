# pylint: disable=redefined-outer-name
import uuid

from hiring_st.generated.cron import run_cron


async def test_clean(web_app_client, load_json, create_workflow):
    data = load_json('workflow.json')
    data['request_id'] = uuid.uuid4().hex
    await create_workflow(data)
    await create_workflow(data)

    await run_cron.main(['hiring_st.crontasks.request_clean', '-t', '0'])
