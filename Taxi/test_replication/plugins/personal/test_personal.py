# pylint: disable=redefined-outer-name
import pytest

from replication import core_context
from replication.plugins.personal import client
from replication.plugins.personal import transform
from . import conftest


@pytest.mark.parametrize(
    'personal_type, personal_values, expected_error',
    [
        (client.PersonalType.phones, ['+79996668888', '+71113334444'], None),
        ('fail', [], client.PersonalValidationError),
    ],
)
@pytest.mark.nofilldb
async def test_personal_client(
        mock_personal,
        replication_app: core_context.AdminCoreData,
        personal_type,
        personal_values,
        expected_error,
):
    personal_client = client.PersonalClient(
        replication_app.shared_deps.client_personal,
    )
    if expected_error is None:
        response = await personal_client.bulk_store(
            personal_type, personal_values,
        )
        assert response == {
            personal_value: client.PersonalItem(
                conftest.personalize_item(personal_value),
            )
            for personal_value in personal_values
        }
    else:
        with pytest.raises(expected_error):
            await personal_client.bulk_store(personal_type, personal_values)


@pytest.mark.parametrize(
    'pd_rules, docs, expected_docs, expected_errors',
    [
        (
            [{'json_path': 'foo.bar', 'personal_type': 'phones'}],
            [{'foo': {'bar': '+79991112222'}}],
            [{'foo': {'bar': '22221119997+'}}],
            [],
        ),
        (
            [
                {
                    'json_path': 'foo.bar',
                    'personal_type': 'phones',
                    'normalize': 'phone_add_plus',
                },
            ],
            [
                {'foo': {'bar': '79991112222  '}},
                {'foo': {'bar': ' 79991112222'}},
                {'foo': {'bar': ' +79991112222 '}},
            ],
            [
                {'foo': {'bar': '22221119997+'}},
                {'foo': {'bar': '22221119997+'}},
                {'foo': {'bar': '22221119997+'}},
            ],
            [],
        ),
        (
            [
                {'json_path': 'foo.bar', 'personal_type': 'phones'},
                {'json_path': 'foo2', 'personal_type': 'driver_licenses'},
            ],
            [
                {'foo': {'bar': '+79991112222'}},
                {'foo': {}},
                {'foo': {'bar': '+73333333333'}, 'foo2': 'abc'},
            ],
            [
                {'foo': {'bar': '22221119997+'}},
                {'foo': {}},
                {'foo': {'bar': '33333333337+'}, 'foo2': 'cba'},
            ],
            [],
        ),
        (
            [{'json_path': 'foo', 'personal_type': 'phones'}],
            [{'foo': 'error'}],
            [{'foo': None}],
            [
                transform.TransformError(
                    key='foo',
                    doc_id='0',
                    original_value='error',
                    personal_value='error',
                    error_text='unexpected error',
                ),
            ],
        ),
    ],
)
@pytest.mark.nofilldb
async def test_personal_transform(
        mock_personal,
        replication_app: core_context.AdminCoreData,
        pd_rules,
        docs,
        expected_docs,
        expected_errors,
):
    personal_client = client.PersonalClient(
        replication_app.shared_deps.client_personal,
    )
    pd_rules = [transform.PDRule(**pd_rule) for pd_rule in pd_rules]
    transformer = transform.Transformer(
        personal_client=personal_client,
        pd_rules=pd_rules,
        executor_pool=replication_app.mapping_pool,
    )

    def _make_dict(_docs):
        return {str(num): doc for num, doc in enumerate(_docs)}

    docs = _make_dict(docs)
    expected_docs = _make_dict(expected_docs)
    transformed, errors = await transformer.transform_pd(docs=docs)
    assert transformed == expected_docs
    assert errors == expected_errors
