/* eslint-disable @typescript-eslint/no-non-null-assertion */
import {beforeEach, describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';

import type {Region} from '@/src/entities/region/entity';
import type {User} from '@/src/entities/user/entity';
import {delayMs} from 'service/helper/delay';

import {getUserProductFiltersHandler} from './get-user-product-filters';

describe('get user product filters', () => {
    let user: User;
    let otherUser: User;
    let region: Region;
    let otherRegion: Region;

    beforeEach(async () => {
        user = await TestFactory.createUser();
        otherUser = await TestFactory.createUser();
        region = await TestFactory.createRegion({code: 'RU'});
        otherRegion = await TestFactory.createRegion({code: 'FR'});
    });

    it('should return filters for user in specified region', async () => {
        const filter1 = await TestFactory.createUserProductFilter({
            regionId: region.id,
            userId: user.id,
            name: 'name1',
            query: 'query1'
        });

        // Для 100% гарантии сортировки по created_at
        await delayMs(500);

        const filter2 = await TestFactory.createUserProductFilter({
            regionId: region.id,
            userId: user.id,
            name: 'name2',
            query: 'quer2'
        });

        await TestFactory.createUserProductFilter({
            regionId: region.id,
            userId: otherUser.id,
            name: 'name3',
            query: 'query3'
        });

        await TestFactory.createUserProductFilter({
            regionId: otherRegion.id,
            userId: user.id,
            name: 'name4',
            query: 'query4'
        });

        await TestFactory.createUserProductFilter({
            regionId: otherRegion.id,
            userId: otherUser.id,
            name: 'name5',
            query: 'query5'
        });

        const result = await getUserProductFiltersHandler.handle({
            context: await TestFactory.createApiContext({user, region}),
            data: {}
        });

        expect(result).toEqual({
            list: [
                {
                    id: filter1.id,
                    name: filter1.name,
                    query: filter1.query
                },
                {
                    id: filter2.id,
                    name: filter2.name,
                    query: filter2.query
                }
            ],
            totalCount: 2
        });
    });
});
