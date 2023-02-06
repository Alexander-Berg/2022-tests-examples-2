/* eslint-disable @typescript-eslint/no-non-null-assertion */
import {beforeEach, describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';

import type {Region} from '@/src/entities/region/entity';
import type {User} from '@/src/entities/user/entity';
import {EntityNotFoundError, NotUniqueProductFilterName} from '@/src/errors';

import {updateUserProductFilterHandler} from './update-user-product-filter';

describe('update user product filter', () => {
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

    it('should update product filter', async () => {
        const filter = await TestFactory.createUserProductFilter({
            regionId: region.id,
            userId: user.id,
            name: 'old',
            query: 'bar'
        });

        const result = await updateUserProductFilterHandler.handle({
            context: await TestFactory.createApiContext({user, region}),
            data: {
                params: {
                    id: filter.id
                },
                body: {
                    name: 'new'
                }
            }
        });

        expect(result).toEqual({
            id: filter.id,
            name: 'new',
            query: 'bar'
        });

        const [updatedFilter] = await TestFactory.getUserProductFilters();

        expect(updatedFilter).toMatchObject({
            id: filter.id,
            userId: user.id,
            regionId: region.id,
            name: 'new',
            query: 'bar'
        });
    });

    it('should throw error if filter does not exist', async () => {
        const result = updateUserProductFilterHandler.handle({
            context: await TestFactory.createApiContext({user, region}),
            data: {
                params: {
                    id: 99999
                },
                body: {
                    name: 'foo'
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

        const result = updateUserProductFilterHandler.handle({
            context: await TestFactory.createApiContext({user: otherUser, region}),
            data: {
                params: {
                    id: filter.id
                },
                body: {
                    name: 'foo'
                }
            }
        });

        await expect(result).rejects.toThrow(EntityNotFoundError);
    });

    it('should throw error if name is not uniq in same region for same user', async () => {
        const filter = await TestFactory.createUserProductFilter({
            regionId: region.id,
            userId: user.id,
            name: 'foo1',
            query: 'bar1'
        });

        await TestFactory.createUserProductFilter({
            regionId: region.id,
            userId: user.id,
            name: 'foo2',
            query: 'bar2'
        });

        const result = updateUserProductFilterHandler.handle({
            context: await TestFactory.createApiContext({user, region}),
            data: {
                params: {
                    id: filter.id
                },
                body: {
                    name: 'foo2'
                }
            }
        });

        await expect(result).rejects.toThrow(NotUniqueProductFilterName);
    });

    it('should update product with same name in defferent region', async () => {
        const name = 'foo2';

        const filter = await TestFactory.createUserProductFilter({
            regionId: region.id,
            userId: user.id,
            name: 'foo1',
            query: 'bar1'
        });

        await TestFactory.createUserProductFilter({
            regionId: otherRegion.id,
            userId: user.id,
            name,
            query: 'bar2'
        });

        const result = await updateUserProductFilterHandler.handle({
            context: await TestFactory.createApiContext({user, region}),
            data: {
                params: {
                    id: filter.id
                },
                body: {
                    name
                }
            }
        });

        expect(result).toEqual({
            id: filter.id,
            name,
            query: 'bar1'
        });

        const filters = await TestFactory.getUserProductFilters();
        const updatedFilter = filters.find((it) => it.query === 'bar1');

        expect(updatedFilter).toMatchObject({
            userId: user.id,
            regionId: region.id,
            name
        });
    });

    it('should update product with same name of defferent user', async () => {
        const name = 'foo2';

        const filter = await TestFactory.createUserProductFilter({
            regionId: region.id,
            userId: user.id,
            name: 'foo1',
            query: 'bar1'
        });

        await TestFactory.createUserProductFilter({
            regionId: region.id,
            userId: otherUser.id,
            name,
            query: 'bar2'
        });

        const result = await updateUserProductFilterHandler.handle({
            context: await TestFactory.createApiContext({user, region}),
            data: {
                params: {
                    id: filter.id
                },
                body: {
                    name
                }
            }
        });

        expect(result).toEqual({
            id: filter.id,
            name,
            query: 'bar1'
        });

        const filters = await TestFactory.getUserProductFilters();
        const updatedFilter = filters.find((it) => it.query === 'bar1');

        expect(updatedFilter).toMatchObject({
            userId: user.id,
            regionId: region.id,
            name
        });
    });
});
