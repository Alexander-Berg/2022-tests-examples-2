import pytest

# TODO(yudind): make it better
@pytest.fixture(name='tagger')
def _tagger(mockserver):
    class Context:
        def __init__(self):
            self.driver_to_tags = {}

        def get_tags(self):
            return self.driver_to_tags

    context = Context()

    @mockserver.json_handler('/tags/v1/assign')
    def _handler(request):
        for entity in request.json['entities']:
            [driver_id, tags] = [entity['name'], entity['tags']]
            context.driver_to_tags[driver_id] = list(tags.keys())
        return {}

    return context


# driver_6 - not in park (i.e. unknown)
# driver_66 - courier + express


@pytest.mark.config(
    DRIVER_CATEGORIES_API_TAG_MAKER_SETTINGS={
        'auto_courier': ['courier', 'express'],
    },
)
@pytest.mark.config(
    DRIVER_CATEGORIES_API_TAG_MAKER2_SETTINGS={
        'enable': True,
        'tag_name': 'auto_courier',
    },
)
@pytest.mark.pgsql('driver-categories-api', files=['categories.sql'])
@pytest.mark.parametrize(
    'stq_type, driver_id, expected',
    [
        pytest.param(
            'driver_category',
            'driver_6',
            {'park_66_driver_6': []},
            id='dummy driver',
        ),
        pytest.param(
            'car_category',
            'driver_6',
            {
                # 'park_66_driver_66': ['auto_courier'],
                # 'park_66_driver_666': ['auto_courier'],
                # 'park_66_driver_6666': ['auto_courier'],
                'park_66_driver_6666x': [],
            },
        ),
        pytest.param(
            'driver_category',
            'driver_66',
            {
                # 'park_66_driver_66': ['auto_courier']
            },
        ),
        pytest.param(
            'car_category',
            'driver_66',
            {
                # 'park_66_driver_66': ['auto_courier'],
                # 'park_66_driver_666': ['auto_courier'],
                # 'park_66_driver_6666': ['auto_courier'],
                'park_66_driver_6666x': [],
            },
        ),
    ],
)
async def test_driver_categories_tag_maker(
        mockserver,
        stq_runner,
        contractor_transport,
        fleet_parks,
        driver_tags,
        driver_profiles,
        taximeter_xservice,
        driver_trackstory,
        driver_diagnostics,
        tagger,
        stq_type,
        driver_id,
        expected,
):
    park_id = 'park_66'
    car_id = 'car_66'

    @mockserver.json_handler(
        '/driver-profiles/v1/vehicle_bindings/drivers/'
        'retrieve_by_park_id_car_id',
    )
    def _handler(request):
        assert request.json['projection'] == ['data.uuid']
        assert request.json['park_id_car_id_in_set'] == [
            park_id + '_' + car_id,
        ]

        profiles = []
        for driver_id in [
                'driver_66',
                'driver_666',
                'driver_6666',
                'driver_6666x',
        ]:
            profiles.append(
                {
                    'data': {'park_id': park_id, 'uuid': driver_id},
                    'park_driver_profile_id': park_id + '_' + driver_id,
                },
            )
        result = {
            'profiles_by_park_id_car_id': [
                {
                    'park_id_car_id': park_id + '_' + car_id,
                    'profiles': profiles,
                },
            ],
        }
        return result

    contractor_transport.set_contractor_id(park_id, driver_id)

    kwargs = {'type': stq_type, 'park_id': park_id}
    if stq_type == 'driver_category':
        task_id = park_id + '_' + driver_id
        kwargs['driver_id'] = driver_id
    else:
        task_id = park_id + '_' + car_id
        kwargs['car_id'] = car_id
    await stq_runner.driver_categories_tag_maker.call(
        task_id=task_id, kwargs=kwargs,
    )

    actual = tagger.get_tags()
    #    print(actual)
    assert actual == expected
