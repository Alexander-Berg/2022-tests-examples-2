import copy

import pytest

from test_taxi_exp import helpers
from test_taxi_exp.helpers import db
from test_taxi_exp.helpers import experiment


WITH_MODSHA1 = 'with_modsha1'
WITH_HIDED_SEGMENTATION = 'with_hided_segmentation'
OLD_SALT = 'old_salt_old_salt'
NEW_SALT = 'new_salt_new_salt'
NEW_SALT_FOR_OLD_PREDICATE = 'aaaaaa'


# @pytest.mark.skip
@pytest.mark.pgsql(
    'taxi_exp', queries=[db.ADD_CONSUMER.format('test_consumer')],
)
async def test(taxi_exp_client, taxi_config):
    # 0. before all features create old experiment
    body_with_mod_sha1 = experiment.generate(
        name=WITH_MODSHA1,
        clauses=[
            experiment.make_clause(
                'title', experiment.mod_sha1_predicate(salt=OLD_SALT),
            ),
        ],
    )
    body_with_mod_sha1 = await helpers.init_exp(
        taxi_exp_client, body_with_mod_sha1,
    )
    body_with_mod_sha1 = await helpers.update_exp_by_draft(
        taxi_exp_client, body_with_mod_sha1,
    )
    # check no has salts
    assert not await db.get_salts(taxi_exp_client.app)

    # I. enable feature and update experiment with save salt
    taxi_config.set_values(
        {
            'EXP3_ADMIN_CONFIG': {
                'features': {'common': {'enable_save_salts': True}},
            },
        },
    )
    await taxi_exp_client.app.config.refresh_cache()
    body_with_mod_sha1 = await helpers.update_exp(
        taxi_exp_client, body_with_mod_sha1,
    )
    body_with_mod_sha1 = await helpers.update_exp_by_draft(
        taxi_exp_client, body_with_mod_sha1,
    )
    # check that experiment with old salt has special trait tag
    assert body_with_mod_sha1['trait_tags'] == ['by-percentage']
    # check that salt saved
    assert (
        [
            {
                'id': item['id'],
                'salt': item['salt'],
                'segmentation_method': item['segmentation_method'],
            }
            for item in await db.get_salts(taxi_exp_client.app)
        ]
        == [
            {
                'id': 1,
                'salt': OLD_SALT,
                'segmentation_method': 'mod_sha1_with_salt',
            },
        ]
    )

    # II. save segmentation for new salts
    # view on updates handle only, admin - view exp without tag
    taxi_config.set_values(
        {
            'EXP3_ADMIN_CONFIG': {
                'features': {
                    'common': {
                        'enable_save_salts': True,
                        'enable_write_segmentation_for_new_salts': True,
                    },
                },
            },
        },
    )
    await taxi_exp_client.app.config.refresh_cache()
    body_with_hided_segmentation = experiment.generate(
        name=WITH_HIDED_SEGMENTATION,
        clauses=[
            experiment.make_clause(
                'title', experiment.mod_sha1_predicate(salt=NEW_SALT),
            ),
        ],
    )
    body_with_hided_segmentation = await helpers.init_exp(
        taxi_exp_client, body_with_hided_segmentation,
    )
    body_with_hided_segmentation = await helpers.update_exp_by_draft(
        taxi_exp_client, body_with_hided_segmentation,
    )
    # check no trait_tag in admin handle
    assert (
        'use-new-segmentation-method'
        in body_with_hided_segmentation['trait_tags']
    )
    assert body_with_hided_segmentation['clauses'][0]['predicate'] == {
        'type': 'mod_sha1_with_salt',
        'init': {
            'arg_name': 'phone_id',
            'divisor': 100,
            'range_from': 0,
            'range_to': 100,
            'salt': NEW_SALT,
        },
    }
    # check found segmentation predicate in updates handle
    response = await helpers.get_updates(
        taxi_exp_client,
        newer_than=body_with_hided_segmentation['last_modified_at'] - 1,
        limit=1,
    )
    response_body = response['experiments'][0]
    assert response_body['name'] == WITH_HIDED_SEGMENTATION
    assert response_body['clauses'][0]['predicate'] == {
        'type': 'segmentation',
        'init': {
            'arg_name': 'phone_id',
            'divisor': 100,
            'range_from': 0,
            'range_to': 100,
            'salt': 'new_salt_new_salt',
        },
    }
    # check update old experiment
    body_with_mod_sha1 = await helpers.update_exp(
        taxi_exp_client, body_with_mod_sha1,
    )
    body_with_mod_sha1 = await helpers.update_exp_by_draft(
        taxi_exp_client, body_with_mod_sha1,
    )
    assert body_with_mod_sha1['trait_tags'] == ['by-percentage']
    assert (
        [
            {
                'id': item['id'],
                'salt': item['salt'],
                'segmentation_method': item['segmentation_method'],
            }
            for item in await db.get_salts(taxi_exp_client.app)
        ]
        == [
            {
                'id': 1,
                'salt': OLD_SALT,
                'segmentation_method': 'mod_sha1_with_salt',
            },
            {'id': 3, 'salt': NEW_SALT, 'segmentation_method': 'segmentation'},
        ]
    )

    # III. allow work segmetation with front
    taxi_config.set_values(
        {
            'EXP3_ADMIN_CONFIG': {
                'features': {
                    'common': {
                        'enable_save_salts': True,
                        'enable_write_segmentation_for_new_salts': True,
                        'enable_segmentation_for_front': True,
                    },
                },
            },
        },
    )
    await taxi_exp_client.app.config.refresh_cache()
    result = await helpers.get_experiment(
        taxi_exp_client, WITH_HIDED_SEGMENTATION,
    )
    assert result['clauses'][0]['predicate'] == {
        'type': 'segmentation',
        'init': {
            'arg_name': 'phone_id',
            'divisor': 100,
            'range_from': 0,
            'range_to': 100,
            'salt': 'new_salt_new_salt',
        },
    }

    # allow send segmentation for admin
    body_with_segmentation = copy.copy(body_with_hided_segmentation)
    body_with_segmentation['clauses'][0]['predicate']['type'] = 'segmentation'
    response = await helpers.update_exp(
        taxi_exp_client, body_with_segmentation, raw_answer=True,
    )
    assert response.status == 200
    response = await helpers.update_exp_by_draft(
        taxi_exp_client, body_with_segmentation, raw_answer=True,
    )
    assert response.status == 200
