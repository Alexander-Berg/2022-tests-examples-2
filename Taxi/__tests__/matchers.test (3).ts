import {expectSaga} from 'redux-saga-test-plan';

import {OPERATIONS} from '../../consts';
import {Role} from '../../types';
import {postFind, preSave} from '../matchers';

const ID = 'ID';
const NAME = 'NAME';

describe('bundles/permissions/sagas/matchers', () => {
    test('Работает postFind', () => {
        const res: Role = {
            id: ID,
            name: NAME,
            categories: [
                {
                    permissions: [
                        {
                            action: 'редактирование',
                            comment: null,
                            countries_filter: ['civ', 'rus'],
                            id: 'edit_banners',
                            mode: 'countries_filter',
                            sections: ['Найм']
                        },
                        {
                            action: 'отправка',
                            comment: null,
                            countries_filter: ['rus'],
                            id: 'deploy_banners',
                            mode: 'countries_filter',
                            sections: ['Найм']
                        }
                    ],
                    id: 'banners',
                    name: 'Баннеры'
                }
            ]
        };

        const result = postFind(res);

        expect(result).toMatchObject({
            id: ID,
            name: NAME,
            groupsWithCountry: [
                {
                    country: 'civ',
                    groups: [
                        {
                            id: 'banners',
                            permissions: ['edit_banners']
                        }
                    ]
                },
                {
                    country: 'rus',
                    groups: [
                        {
                            id: 'banners',
                            permissions: ['edit_banners', 'deploy_banners']
                        }
                    ]
                }
            ]
        });
    });

    test('Работает preSave', () => {
        const model = {
            id: ID,
            name: NAME,
            groupsWithCountry: [
                {
                    country: 'civ',
                    groups: [
                        {
                            id: 'banners',
                            permissions: ['edit_banners']
                        }
                    ]
                },
                {
                    country: 'rus',
                    groups: [
                        {
                            id: 'banners',
                            permissions: ['edit_banners', 'deploy_banners']
                        }
                    ]
                },
                {
                    country: 'all',
                    groups: [
                        {
                            id: 'banners',
                            permissions: ['deploy_banners']
                        }
                    ]
                }
            ],
            dynamic_permissions: [
                {
                    countries_filter: ['rus'],
                    id: 'taxi_scripts',
                    mode: 'countries_filter' as 'countries_filter'
                }
            ]
        };

        return expectSaga(preSave, model)
            .withState({
                asyncOperations: {
                    [OPERATIONS.LOAD_ALL_PERMISSIONS]: {
                        result: {
                            dynamic_permissions: ['taxi_scripts', 'dwh_scripts']
                        }
                    }
                }
            })
            .returns({
                id: ID,
                name: NAME,
                permissions: [
                    {
                        id: 'edit_banners',
                        mode: 'countries_filter',
                        countries_filter: ['civ', 'rus']
                    },
                    {
                        id: 'deploy_banners',
                        mode: 'unrestricted'
                    }
                ],
                dynamic_permissions: [
                    {
                        countries_filter: ['rus'],
                        id: 'taxi_scripts',
                        mode: 'countries_filter'
                    }
                ]
            })
            .run();
    });
});
