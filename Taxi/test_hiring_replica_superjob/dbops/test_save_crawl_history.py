# pylint: disable=redefined-outer-name


async def test_get_last_resume_empty(get_last_resume):
    last_resume = await get_last_resume()
    assert last_resume == '1'


async def test_get_last_resume(get_last_resume, save_crawl_history):
    resume_revision = 123456
    await save_crawl_history(rev=resume_revision)

    last_resume = await get_last_resume()
    assert last_resume == str(resume_revision + 1)
