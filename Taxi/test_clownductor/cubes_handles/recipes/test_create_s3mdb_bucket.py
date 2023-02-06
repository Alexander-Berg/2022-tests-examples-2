import pytest

SERVICE = 'taxidocumenttemplator'

CONFIG = {
    '__default__': {'components': [74933, 31505], 'queue': 'TAXIADMIN'},
    'mdssupport': {
        'queue': 'MDSSUPPORT',
        'comment': (
            'не клоуновский сервис. '
            'Используется для создания тикетов в очереди '
            'MDSSUPPORT'
        ),
    },
}

TANKER = {
    'creates3bucket.startrack_ticket_custom_size.summary': {
        'ru': 'Квота в S3 для {abc_service_name}',
    },
    'creates3bucket.startrack_ticket_custom_size.description': {
        'ru': (
            'Ваш ABC сервис:\n{abc_service_name}\n'
            'Суммарное количество бакетов:\n{buckets_quantity}\n'
            'Free Tier:\nНет\n'
            'Краткое описание сервиса для получения'
            ' Free Tier квоты:\nНет ответа\n'
            'Общий объём требуемого места (Gb):\n{bucket_size_gb}\n'
            'Заказ откуда брать квоту:\n{quota_service}\n'
            'Предполагаемая нагрузка на чтение в rps:\n{bucket_rps_read}\n'
            'Предполагаемая нагрузка на запись в rps:\n{bucket_rps_write}\n'
            'Я знаю о том, что роли в IDM регулярно пересматриваются,\n'
            'и буду следить за уведомлениями от IDM, чтобы роль моего\n'
            'сервиса/пользователя не отозвали по этой причине:\nДа'
        ),
    },
}

IDM_REQUESTS = {
    's3-mds': {
        'path': f'/{SERVICE}-1237-50889/service-account-role/writer/',
        'user': 1000,
    },
    's3-mds-test': {
        'path': f'/{SERVICE}-1237-50889/service-account-role/writer/',
        'user': 1001,
    },
}


@pytest.mark.config(CLOWNDUCTOR_PROJECT_QUEUES=CONFIG)
async def test_create_s3mds_default_quota(
        abc_mockserver,
        add_service,
        load_yaml,
        login_mockserver,
        run_job_common,
        staff_mockserver,
        task_processor,
):

    abc_mock = abc_mockserver()
    login_mockserver()
    staff_mockserver()

    await add_service('storagefortest', 'service-1')

    recipe = task_processor.load_recipe(
        load_yaml('recipes/S3MdsCreateBucket.yaml')['data'],
    )

    job = await recipe.start_job(
        job_vars={
            'users': [
                {'login': 'temox', 'role': 's3_owner'},
                {'login': 'werr', 'role': 's3_admin'},
                {'login': 'test_user1', 'role': 's3_admin'},
            ],
            'service_slug': 'storagefortest',
            'bucket_name': 'temox-test',
            'bucket_size_gb': 10,
            'buckets_quantity': 1,
            'bucket_objects_quantity': 1,
            'bucket_rps_read': 1,
            'bucket_rps_write': 1,
            'quota_service': 'parrentstoragefortest',
        },
        initiator='clownductor',
    )

    await run_job_common(job)

    assert abc_mock.times_called == 3
    assert abc_mock.next_call()['request'].json == {
        'service': 1237,
        'person': 'temox',
        'role': 4881,
    }
    assert abc_mock.next_call()['request'].json == {
        'service': 1237,
        'person': 'werr',
        'role': 4877,
    }
    assert abc_mock.next_call()['request'].json == {
        'service': 1237,
        'person': 'test_user1',
        'role': 4877,
    }


@pytest.mark.config(CLOWNDUCTOR_PROJECT_QUEUES=CONFIG)
@pytest.mark.translations(clownductor=TANKER)
async def test_create_s3mds_custom_size(
        abc_mockserver,
        add_service,
        load_yaml,
        login_mockserver,
        patch,
        run_job_common,
        staff_mockserver,
        task_processor,
):

    abc_mock = abc_mockserver()
    login_mockserver()
    staff_mockserver()

    await add_service('storagefortest', 'service-1')

    @patch('taxi.clients.startrack.StartrackAPIClient.create_ticket')
    async def _create_ticket(**kwargs):
        assert kwargs['queue'] == 'MDSSUPPORT'

        assert (
            kwargs['summary']
            == 'Квота в S3 для Виртуальная эксплуатация Такси'
        )
        assert kwargs['description'] == (
            'Ваш ABC сервис:\nВиртуальная эксплуатация Такси\n'
            'Суммарное количество бакетов:\n1\n'
            'Free Tier:\nНет\n'
            'Краткое описание сервиса для получения'
            ' Free Tier квоты:\nНет ответа\n'
            'Общий объём требуемого места (Gb):\n100\n'
            'Заказ откуда брать квоту:\nparrentstoragefortest\n'
            'Предполагаемая нагрузка на чтение в rps:\n1\n'
            'Предполагаемая нагрузка на запись в rps:\n1\n'
            'Я знаю о том, что роли в IDM регулярно пересматриваются,\n'
            'и буду следить за уведомлениями от IDM, чтобы роль моего\n'
            'сервиса/пользователя не отозвали по этой причине:\nДа'
        )
        assert kwargs['followers'] == ['temox']

        return {'key': 'MDSSUPPORT-1'}

    recipe = task_processor.load_recipe(
        load_yaml('recipes/S3MdsCreateBucket.yaml')['data'],
    )

    job = await recipe.start_job(
        job_vars={
            'users': [
                {'login': 'temox', 'role': 's3_owner'},
                {'login': 'werr', 'role': 's3_admin'},
                {'login': 'test_user1', 'role': 's3_admin'},
            ],
            'service_slug': 'storagefortest',
            'bucket_name': 'temox-test',
            'bucket_size_gb': 100,
            'buckets_quantity': 1,
            'bucket_objects_quantity': 1,
            'bucket_rps_read': 1,
            'bucket_rps_write': 1,
            'quota_service': 'parrentstoragefortest',
        },
        initiator='clownductor',
    )

    await run_job_common(job)

    assert abc_mock.times_called == 3
    assert abc_mock.next_call()['request'].json == {
        'service': 1237,
        'person': 'temox',
        'role': 4881,
    }
    assert abc_mock.next_call()['request'].json == {
        'service': 1237,
        'person': 'werr',
        'role': 4877,
    }
    assert abc_mock.next_call()['request'].json == {
        'service': 1237,
        'person': 'test_user1',
        'role': 4877,
    }
    assert len(_create_ticket.calls) == 1


@pytest.mark.features_on('permissions_cube_give_role_for_service')
async def test_service_has_two_tvms(
        mock_idm,
        mockserver,
        abc_mockserver,
        login_mockserver,
        staff_mockserver,
        load_yaml,
        task_processor,
        run_job_common,
):
    abc_mockserver()
    login_mockserver()
    staff_mockserver()

    @mock_idm('/api/v1/batch/')
    def _batch_handler(request):
        def _body(id_):
            method = requests[0]['method']
            path = requests[0]['path']
            if method == 'DELETE':
                return ''
            if method == 'POST':
                if path == '/rolenodes/':
                    return None
                return {'id': id_ + 1}
            raise RuntimeError(f'unknown method {method} for mock')

        requests = request.json
        responses = []
        for i, req in enumerate(requests):
            body = req['body']
            system = body['system']

            assert system in IDM_REQUESTS
            assert body['path'] == IDM_REQUESTS[system]['path']
            assert body['user'] == IDM_REQUESTS[system]['user']

            responses.append(
                {'id': req['id'], 'status_code': 200, 'body': _body(i)},
            )
        return mockserver.make_response(
            status=200, json={'responses': responses},
        )

    @mockserver.json_handler('/clowny-perforator/v1.0/services')
    def get_handler(request):
        if request.query['id'] == '50889':
            envs = [
                {'id': 1, 'env_type': 'production', 'tvm_id': 1000},
                {'id': 2, 'env_type': 'testing', 'tvm_id': 1001},
            ]
            response = {
                'id': 1,
                'tvm_name': 'srvice-tvm-name',
                'environments': envs,
                'clown_service': {'project_id': 50889, 'clown_id': 50889},
                'is_internal': True,
            }
            return response

        return mockserver.make_response(
            json={'code': 'code', 'message': 'message'}, status=404,
        )

    recipe = task_processor.load_recipe(
        load_yaml('recipes/S3MdsCreateBucket.yaml')['data'],
    )

    job = await recipe.start_job(
        job_vars={
            'env': 'testing',
            'users': [
                {'login': 'temox', 'role': 's3_owner'},
                {'login': 'werr', 'role': 's3_admin'},
                {'login': 'test_user1', 'role': 's3_admin'},
            ],
            'service_slug': SERVICE,
            'bucket_name': 'temox-test',
            'bucket_size_gb': 10,
            'buckets_quantity': 1,
            'bucket_objects_quantity': 1,
            'bucket_rps_read': 1,
            'bucket_rps_write': 1,
            'quota_service': 'parrentstoragefortest',
        },
        initiator='clownductor',
    )

    await run_job_common(job)

    assert get_handler.times_called == 1


@pytest.mark.features_on('permissions_cube_give_role_for_service')
async def test_service_existed_role(
        mock_idm,
        mockserver,
        abc_mockserver,
        login_mockserver,
        staff_mockserver,
        load_yaml,
        task_processor,
        run_job_common,
):
    abc_mockserver()
    login_mockserver()
    staff_mockserver()

    @mock_idm('/api/v1/batch/')
    def _batch_handler(request):
        def _body(id_):
            method = requests[0]['method']
            path = requests[0]['path']
            if method == 'DELETE':
                return ''
            if method == 'POST':
                if path == '/rolenodes/':
                    return None
                return {'id': id_ + 1}
            raise RuntimeError(f'unknown method {method} for mock')

        requests = request.json
        responses = []
        for req in requests:
            responses.append(
                {
                    'id': req['id'],
                    'status_code': 409,
                    'body': {
                        'error_code': 'CONFLICT',
                        'message': (
                            'У пользователя "srvice-tvm-name" уже есть '
                            'такая роль (Service: '
                            'taxi/document-templator (TAXIADMIN-12135), '
                            'Request type: Service account role, Role: Admin) '
                            'в системе "S3-MDS (Testing)" в состоянии "Выдана"'
                        ),
                    },
                },
            )

        return mockserver.make_response(
            status=400, json={'responses': responses},
        )

    @mockserver.json_handler('/clowny-perforator/v1.0/services')
    def get_handler(request):
        if request.query['id'] == '50889':
            envs = [
                {'id': 1, 'env_type': 'production', 'tvm_id': 1000},
                {'id': 2, 'env_type': 'testing', 'tvm_id': 1001},
            ]
            response = {
                'id': 1,
                'tvm_name': 'srvice-tvm-name',
                'environments': envs,
                'clown_service': {'project_id': 50889, 'clown_id': 50889},
                'is_internal': True,
            }
            return response

        return mockserver.make_response(
            json={'code': 'code', 'message': 'message'}, status=404,
        )

    recipe = task_processor.load_recipe(
        load_yaml('recipes/S3MdsCreateBucket.yaml')['data'],
    )

    job = await recipe.start_job(
        job_vars={
            'env': 'testing',
            'users': [
                {'login': 'temox', 'role': 's3_owner'},
                {'login': 'werr', 'role': 's3_admin'},
                {'login': 'test_user1', 'role': 's3_admin'},
            ],
            'service_slug': SERVICE,
            'bucket_name': 'temox-test',
            'bucket_size_gb': 10,
            'buckets_quantity': 1,
            'bucket_objects_quantity': 1,
            'bucket_rps_read': 1,
            'bucket_rps_write': 1,
            'quota_service': 'parrentstoragefortest',
        },
        initiator='clownductor',
    )

    await run_job_common(job)

    assert get_handler.times_called == 1
