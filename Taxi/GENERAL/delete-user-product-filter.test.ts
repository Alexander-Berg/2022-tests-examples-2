/* eslint-disable @typescript-eslint/no-non-null-assertion */
import {beforeEach, describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';

import type {Region} from '@/src/entities/region/entity';
import type {User} from '@/src/entities/user/entity';
import {EntityNotFoundError} from '@/src/errors';

import {deleteUserProductFilterHandler} from './delete-user-product-filter';

describe('delete user product filter', () => {
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

    it('should delete user filter', async () => {
        const filter = await TestFactory.createUserProductFilter({
            regionId: region.id,
            userId: user.id,
            name: 'name1',
            query: 'query1'
        });

        await TestFactory.createUserProductFilter({
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

        const filtersBefore = await TestFactory.getUserProductFilters();

        expect(filtersBefore).toHaveLength(5);

        const result = await deleteUserProductFilterHandler.handle({
            context: await TestFactory.createApiContext({user, region}),
            data: {
                params: {
                    id: filter.id
                }
            }
        });

        expect(result).toEqual({});

        const filtersAfter = await TestFactory.getUserProductFilters();
        const deletedFilter = filtersAfter.find((it) => it.id === filter.id);

        expect(filtersAfter).toHaveLength(4);
        expect(deletedFilter).toBeUndefined();
    });

    it('should throw error if filter does not exist', async () => {
        const result = deleteUserProductFilterHandler.handle({
            context: await TestFactory.createApiContext({user, region}),
            data: {
                params: {
                    id: 99999
                }
            }
        });

        await expect(result).rejects.toThrow(EntityNotFoundError);
    });

    it('should throw error if filter has other user', async () => {
        const filter = await TestFactory.createUserProductFilter({
            regionId: region.id,
            userId: user.id,
            name: 'foo',
            query: 'bar'
        });

        const result = deleteUserProductFilterHandler.handle({
            context: await TestFactory.createApiContext({user: otherUser, region}),
            data: {
                params: {
                    id: filter.id
                }
            }
        });

        await expect(result).rejects.toThrow(EntityNotFoundError);
    });
});
