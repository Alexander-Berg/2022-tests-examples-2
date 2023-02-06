import type {Staff} from '@lavka-js-toolbox/staff-provider';
import {describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';
import {CityGeoId} from 'tests/unit/types';

import type {RegionEntity} from '@/src/entities/region/entity';
import type {UserEntity} from '@/src/entities/user/entity';
import type {UserApiRequestContext} from 'server/routes/api/api-context';
import type {Employee} from 'types/user';

import {crmSuggestPerformersHandler} from './crm-suggest-performers';

describe('crmSuggestPerformersHandler()', () => {
    let user: UserEntity;
    let region: RegionEntity;
    let context: UserApiRequestContext;

    beforeEach(async () => {
        user = await TestFactory.createUser({
            staffData: {
                name: {
                    first: {
                        en: 'Vassily'
                    },
                    last: {
                        en: 'Poupkine'
                    }
                },
                images: {
                    avatar: 'https://yandex.ru/image.png'
                }
            } as Staff.Person
        });
        region = await TestFactory.createRegion();
        context = await TestFactory.createUserApiContext({region, user});
    });

    it('should return current user only', async () => {
        const cityGeoId = CityGeoId.MOSCOW;

        const {items} = await crmSuggestPerformersHandler({
            data: {query: {query: 'foo', cityGeoId}},
            context
        });

        expect(items).toHaveLength(1);
        expect(items[0]).toMatchObject<Employee>({
            uid: user.uid,
            login: user.login,
            name: 'Vassily Poupkine',
            avatarUrl: 'https://yandex.ru/image.png'
        });
    });
});
