async def test_recipe(load_yaml, task_processor):
    """
    Just test that recipe is valid
    """
    task_processor.load_recipe(load_yaml('EntryPointEnableSsl.yaml')['data'])
