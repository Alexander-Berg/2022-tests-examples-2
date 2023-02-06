async def activate_task(taxi_effrat_employees, task_name, response_code=200):
    response = await taxi_effrat_employees.post(
        'service/cron', {'task_name': task_name},
    )
    assert response.status_code == response_code
