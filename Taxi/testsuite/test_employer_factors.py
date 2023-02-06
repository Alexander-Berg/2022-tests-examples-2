async def test_basic(
        rt_robot_execute,
        execute_pg_query,
):
    await rt_robot_execute('employer_factors_watcher')
    employer_factors_rows = execute_pg_query("select key from default_cache WHERE key LIKE '/factors/%'")
    
    assert employer_factors_rows == [
        ['/factors/default'],
        ['/factors/eats'],
        ['/factors/food_retail'],
        ['/factors/grocery'],
    ]
