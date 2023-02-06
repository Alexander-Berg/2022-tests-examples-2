import pytest


@pytest.fixture(name='unique_drivers')
def unique_drivers(mockserver):
    class Context:
        def __init__(self):
            self.calls = 0
            self.park_id = ''
            self.driver_id = ''
            self.unique_driver_id = ''

        def set_unique(self, park_id, driver_id, unique_driver_id):
            self.park_id = park_id
            self.driver_id = driver_id
            self.unique_driver_id = unique_driver_id

    context = Context()

    @mockserver.json_handler(
        '/unique-drivers/v1/driver/uniques/retrieve_by_profiles',
    )
    async def _retrieve_by_profiles(request):
        context.calls += 1
        if context.unique_driver_id:
            return {
                'uniques': [
                    {
                        'park_driver_profile_id': (
                            f'{context.park_id}_{context.driver_id}'
                        ),
                        'data': {'unique_driver_id': context.unique_driver_id},
                    },
                ],
            }
        return {'uniques': []}

    return context
