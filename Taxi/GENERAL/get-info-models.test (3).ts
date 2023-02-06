import {beforeEach, describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';

import type {Region} from '@/src/entities/region/entity';
import type {User} from '@/src/entities/user/entity';
import type {ApiRequestContext} from 'server/routes/api/api-handler';
import {AttributeType} from 'types/attribute';

import {getInfoModelsHandler} from './get-info-models';

describe('get info models', () => {
    let user: User;
    let region: Region;
    let context: ApiRequestContext;

    beforeEach(async () => {
        user = await TestFactory.createUser();
        region = await TestFactory.createRegion();
        context = await TestFactory.createApiContext();
    });

    it('should return info models (sort by id)', async () => {
        const attr1 = await TestFactory.createAttribute({
            userId: user.id,
            attribute: {
                type: AttributeType.STRING
            }
        });

        const attr2 = await TestFactory.createAttribute({
            userId: user.id,
            attribute: {
                type: AttributeType.STRING
            }
        });

        const im1 = await TestFactory.createInfoModel({
            userId: user.id,
            regionId: region.id,
            attributes: [
                {
                    id: attr1.id
                },
                {
                    id: attr2.id,
                    isImportant: true
                }
            ]
        });

        const im2 = await TestFactory.createInfoModel({
            userId: user.id,
            regionId: region.id,
            attributes: [
                {
                    id: attr1.id
                }
            ]
        });

        const infoModels1 = await getInfoModelsHandler.handle({
            context,
            data: {
                query: {
                    limit: 1,
                    offset: 0
                }
            }
        });

        expect(infoModels1.totalCount).toBe(2);
        expect(infoModels1.list).toEqual([
            {
                code: im1.code,
                region: region.isoCode,
                name: {},
                description: {},
                attributes: [
                    {
                        code: attr1.code,
                        isImportant: false
                    },
                    {
                        code: attr2.code,
                        isImportant: true
                    }
                ]
            }
        ]);

        const infoModels2 = await getInfoModelsHandler.handle({
            context,
            data: {
                query: {
                    limit: 1,
                    offset: 1
                }
            }
        });

        expect(infoModels2.totalCount).toBe(2);
        expect(infoModels2.list).toEqual([
            {
                code: im2.code,
                region: region.isoCode,
                name: {},
                description: {},
                attributes: [
                    {
                        code: attr1.code,
                        isImportant: false
                    }
                ]
            }
        ]);
    });

    it('should return info models (sort by group and in group)', async () => {
        const attrGroup1 = await TestFactory.createAttributeGroup({
            userId: user.id,
            attributeGroup: {
                code: 'some_group_1'
            }
        });

        const attrGroup2 = await TestFactory.createAttributeGroup({
            userId: user.id,
            attributeGroup: {
                code: 'some_group_2'
            }
        });

        const attr1 = await TestFactory.createAttribute({
            userId: user.id,
            attribute: {
                type: AttributeType.STRING
            }
        });

        const attr2 = await TestFactory.createAttribute({
            userId: user.id,
            attribute: {
                type: AttributeType.STRING,
                attributeGroupId: attrGroup1.id,
                attributeGroupSortOrder: 2
            }
        });

        const attr3 = await TestFactory.createAttribute({
            userId: user.id,
            attribute: {
                type: AttributeType.STRING,
                attributeGroupId: attrGroup1.id,
                attributeGroupSortOrder: 1
            }
        });

        const attr4 = await TestFactory.createAttribute({
            userId: user.id,
            attribute: {
                type: AttributeType.STRING,
                attributeGroupId: attrGroup2.id,
                attributeGroupSortOrder: 1
            }
        });

        const im = await TestFactory.createInfoModel({
            userId: user.id,
            regionId: region.id,
            attributes: [
                {
                    id: attr4.id
                },
                {
                    id: attr3.id,
                    isImportant: true
                },
                {
                    id: attr2.id
                },
                {
                    id: attr1.id
                }
            ]
        });

        const infoModels = await getInfoModelsHandler.handle({
            context,
            data: {
                query: {
                    limit: 1,
                    offset: 0
                }
            }
        });

        expect(infoModels.totalCount).toBe(1);
        expect(infoModels.list).toEqual([
            {
                code: im.code,
                region: region.isoCode,
                name: {},
                description: {},
                attributes: [
                    {
                        code: attr3.code,
                        isImportant: true
                    },
                    {
                        code: attr2.code,
                        isImportant: false
                    },
                    {
                        code: attr4.code,
                        isImportant: false
                    },
                    {
                        code: attr1.code,
                        isImportant: false
                    }
                ]
            }
        ]);
    });
});
