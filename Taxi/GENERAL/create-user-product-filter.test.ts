/* eslint-disable @typescript-eslint/no-non-null-assertion */
import {beforeEach, describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';

import type {Region} from '@/src/entities/region/entity';
import type {User} from '@/src/entities/user/entity';
import {NotUniqueProductFilterName, NotUniqueProductFilterQuery} from '@/src/errors';

import {createUserProductFilterHandler} from './create-user-product-filter';

describe('create user product filter', () => {
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

    it('should create product filter', async () => {
        const filters = await TestFactory.getUserProductFilters();

        expect(filters).toHaveLength(0);

        const result = await createUserProductFilterHandler.handle({
            context: await TestFactory.createApiContext({user, region}),
            data: {
                body: {
                    name: 'foo',
                    query: 'bar'
                }
            }
        });

        expect(result).toEqual({
            id: expect.any(Number),
            name: 'foo',
            query: 'bar'
        });

        const [filter] = await TestFactory.getUserProductFilters();

        expect(filter).toMatchObject({
            userId: user.id,
            regionId: region.id,
            name: 'foo',
            query: 'bar'
        });
    });

    it('should throw error if name is not uniq in same region for same user', async () => {
        const name = 'foo';

        await TestFactory.createUserProductFilter({
            regionId: region.id,
            userId: user.id,
            name,
            query: 'bar1'
        });

        const result = createUserProductFilterHandler.handle({
            context: await TestFactory.createApiContext({user, region}),
            data: {
                body: {
                    name,
                    query: 'bar2'
                }
            }
        });

        await expect(result).rejects.toThrow(NotUniqueProductFilterName);
    });

    it('should throw error if query is not uniq in same region for same user', async () => {
        const query = 'bar';

        await TestFactory.createUserProductFilter({
            regionId: region.id,
            userId: user.id,
            name: 'foo1',
            query
        });

        const result = createUserProductFilterHandler.handle({
            context: await TestFactory.createApiContext({user, region}),
            data: {
                body: {
                    name: 'foo2',
                    query
                }
            }
        });

        await expect(result).rejects.toThrow(NotUniqueProductFilterQuery);
    });

    it('should create product with same name in defferent region', async () => {
        const name = 'foo';

        await TestFactory.createUserProductFilter({
            regionId: region.id,
            userId: user.id,
            name,
            query: 'bar1'
        });

        const result = await createUserProductFilterHandler.handle({
            context: await TestFactory.createApiContext({user, region: otherRegion}),
            data: {
                body: {
                    name,
                    query: 'bar2'
                }
            }
        });

        expect(result).toEqual({
            id: expect.any(Number),
            name,
            query: 'bar2'
        });

        const filters = await TestFactory.getUserProductFilters();
        const filter = filters.find((it) => it.query === 'bar2');

        expect(filter).toMatchObject({
            userId: user.id,
            regionId: otherRegion.id,
            name
        });
    });

    it('should create product with same query in defferent region', async () => {
        const query = 'bar';

        await TestFactory.createUserProductFilter({
            regionId: region.id,
            userId: user.id,
            name: 'foo1',
            query
        });

        const result = await createUserProductFilterHandler.handle({
            context: await TestFactory.createApiContext({user, region: otherRegion}),
            data: {
                body: {
                    name: 'foo2',
                    query
                }
            }
        });

        expect(result).toEqual({
            id: expect.any(Number),
            name: 'foo2',
            query
        });

        const filters = await TestFactory.getUserProductFilters();
        const filter = filters.find((it) => it.name === 'foo2');

        expect(filter).toMatchObject({
            userId: user.id,
            regionId: otherRegion.id,
            query
        });
    });

    it('should create product with same name of different user', async () => {
        const name = 'foo';

        await TestFactory.createUserProductFilter({
            regionId: region.id,
            userId: user.id,
            name,
            query: 'bar1'
        });

        const result = await createUserProductFilterHandler.handle({
            context: await TestFactory.createApiContext({user: otherUser, region}),
            data: {
                body: {
                    name,
                    query: 'bar2'
                }
            }
        });

        expect(result).toEqual({
            id: expect.any(Number),
            name,
            query: 'bar2'
        });

        const filters = await TestFactory.getUserProductFilters();
        const filter = filters.find((it) => it.query === 'bar2');

        expect(filter).toMatchObject({
            userId: otherUser.id,
            regionId: region.id,
            name
        });
    });

    it('should create product with same query of different user', async () => {
        const query = 'bar';

        await TestFactory.createUserProductFilter({
            regionId: region.id,
            userId: user.id,
            name: 'foo1',
            query
        });

        const result = await createUserProductFilterHandler.handle({
            context: await TestFactory.createApiContext({user: otherUser, region}),
            data: {
                body: {
                    name: 'foo2',
                    query
                }
            }
        });

        expect(result).toEqual({
            id: expect.any(Number),
            name: 'foo2',
            query
        });

        const filters = await TestFactory.getUserProductFilters();
        const filter = filters.find((it) => it.name === 'foo2');

        expect(filter).toMatchObject({
            userId: otherUser.id,
            regionId: region.id,
            query
        });
    });
});
