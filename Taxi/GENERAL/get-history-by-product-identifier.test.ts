/* eslint-disable @typescript-eslint/no-non-null-assertion */
import {uuid} from 'casual';
import {orderBy, times} from 'lodash';
import pMap from 'p-map';
import {beforeEach, describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';

import {FrontCategoryProduct} from '@/src/entities/front-category-product/entity';
import {ImageCache} from '@/src/entities/image-cache/entity';
import type {Lang} from '@/src/entities/lang/entity';
import {Product} from '@/src/entities/product/entity';
import {ProductAttributeValue} from '@/src/entities/product-attribute-value/entity';
import type {Region} from '@/src/entities/region/entity';
import type {User} from '@/src/entities/user/entity';
import {EntityNotFoundError} from '@/src/errors';
import {executeInTransaction, HistorySource} from '@/src/service/db';
import {AttributeType} from '@/src/types/attribute';
import type {ApiRequestContext} from 'server/routes/api/api-handler';
import type {DbAttributeValue} from 'types/attribute-value';
import {ProductStatus} from 'types/product';

import {getProductHistory} from './get-history-by-product-identifier';

describe('get history by product identifier', () => {
    let user: User;
    let lang: Lang;
    let region: Region;
    let context: ApiRequestContext;

    beforeEach(async () => {
        user = await TestFactory.createUser();
        lang = await TestFactory.createLang();
        region = await TestFactory.createRegion();
        context = await TestFactory.createApiContext({region, user});
    });

    async function createMasterCategory(regionId: number) {
        const attributes = await Promise.all([
            TestFactory.createAttribute({
                userId: user.id,
                attribute: {type: AttributeType.NUMBER, isValueRequired: true, isValueLocalizable: false}
            }),
            TestFactory.createAttribute({
                userId: user.id,
                attribute: {type: AttributeType.STRING, isValueRequired: false, isValueLocalizable: true}
            })
        ]);
        const infoModel = await TestFactory.createInfoModel({
            regionId,
            userId: user.id,
            attributes: [
                {id: attributes[0].id, isImportant: true},
                {id: attributes[1].id, isImportant: false}
            ]
        });

        return TestFactory.createMasterCategory({
            infoModelId: infoModel.id,
            regionId,
            userId: user.id
        });
    }

    it('should change FC', async () => {
        const product = await TestFactory.createProduct({
            masterCategoryId: (await createMasterCategory(region.id)).id,
            userId: user.id,
            regionId: region.id
        });

        const fcs = await pMap(
            times(3),
            async () =>
                TestFactory.createFrontCategory({
                    userId: user.id,
                    regionId: region.id
                }),
            {concurrency: 1}
        );

        // Transaction #3. State: [0, 1]
        const fcp = await executeInTransaction({authorId: user.id, source: 'ui', stamp: uuid}, async (manager) => {
            return manager.save(FrontCategoryProduct, [
                {productId: product.id, frontCategoryId: fcs[0].id},
                {productId: product.id, frontCategoryId: fcs[1].id}
            ]);
        });
        fcp.sort((a, b) => a.id - b.id);

        // Transaction #2. State: [1, 2]
        await executeInTransaction({authorId: user.id, source: 'ui', stamp: uuid}, async (manager) => {
            await manager.delete(FrontCategoryProduct, {id: fcp[0].id});
            return manager.save(FrontCategoryProduct, {productId: product.id, frontCategoryId: fcs[2].id});
        });

        // Transaction #1. State: [1, 2, 0]
        await executeInTransaction({authorId: user.id, source: 'ui', stamp: uuid}, async (manager) => {
            return manager.save(FrontCategoryProduct, {productId: product.id, frontCategoryId: fcs[0].id});
        });

        const {list: historyResult} = await getProductHistory.handle({
            context,
            data: {params: {identifier: product.identifier}}
        });

        // Fix flapping tests
        for (const hr of historyResult) {
            hr.mutation.frontCategories?.new.sort((a, b) => a.id - b.id);
            hr.mutation.frontCategories?.old.sort((a, b) => a.id - b.id);
        }

        expect(historyResult).toMatchObject([
            {
                mutation: {
                    frontCategories: {
                        old: [{id: fcs[1].id}, {id: fcs[2].id}],
                        new: [{id: fcs[0].id}, {id: fcs[1].id}, {id: fcs[2].id}]
                    }
                }
            },
            {
                mutation: {
                    frontCategories: {old: [{id: fcs[0].id}, {id: fcs[1].id}], new: [{id: fcs[1].id}, {id: fcs[2].id}]}
                }
            },
            {mutation: {frontCategories: {old: [], new: [{id: fcs[0].id}, {id: fcs[1].id}]}}},
            {mutation: {}}
        ]);
    });

    it('should change something between two FC changes', async () => {
        const product = await TestFactory.createProduct({
            masterCategoryId: (await createMasterCategory(region.id)).id,
            userId: user.id,
            regionId: region.id,
            status: ProductStatus.DISABLED
        });

        const fcs = await Promise.all(
            times(2).map(() =>
                TestFactory.createFrontCategory({
                    userId: user.id,
                    regionId: region.id
                })
            )
        );

        // Transaction #3. State: [0]
        await executeInTransaction({authorId: user.id, source: 'ui', stamp: uuid}, async (manager) =>
            manager.save(FrontCategoryProduct, {productId: product.id, frontCategoryId: fcs[0].id})
        );

        // Transaction #2. A change between two FC changes
        await executeInTransaction({authorId: user.id, source: 'ui', stamp: uuid}, async (manager) => {
            product.status = ProductStatus.ACTIVE;
            return manager.save(Product, product);
        });

        // Transaction #1. State: [0, 1]
        await executeInTransaction({authorId: user.id, source: 'ui', stamp: uuid}, async (manager) => {
            return manager.save(FrontCategoryProduct, {productId: product.id, frontCategoryId: fcs[1].id});
        });

        const {list: historyResult} = await getProductHistory.handle({
            context,
            data: {params: {identifier: product.identifier}}
        });

        expect(historyResult).toMatchObject([
            {
                mutation: {frontCategories: {old: [{id: fcs[0].id}], new: [{id: fcs[0].id}, {id: fcs[1].id}]}}
            },
            {
                mutation: {
                    status: {old: ProductStatus.DISABLED, new: ProductStatus.ACTIVE}
                }
            },
            {mutation: {frontCategories: {old: [], new: [{id: fcs[0].id}]}}},
            {mutation: {}}
        ]);
        expect(historyResult[1].mutation).not.toHaveProperty('frontCategories');
    });

    it('should change MC with info-model', async () => {
        const attributes = await Promise.all([
            TestFactory.createAttribute({
                userId: user.id,
                attribute: {type: AttributeType.NUMBER, isValueRequired: true, isValueLocalizable: false}
            }),
            TestFactory.createAttribute({
                userId: user.id,
                attribute: {type: AttributeType.STRING, isValueRequired: false, isValueLocalizable: true}
            })
        ]);

        const infoModels = await Promise.all(
            times(2).map(() =>
                TestFactory.createInfoModel({
                    regionId: region.id,
                    userId: user.id,
                    attributes: [
                        {id: attributes[0].id, isImportant: true},
                        {id: attributes[1].id, isImportant: false}
                    ]
                })
            )
        );

        const mcParent = await TestFactory.createMasterCategory({
            infoModelId: infoModels[0].id,
            regionId: region.id,
            userId: user.id
        });

        const mcChildren = await Promise.all(
            infoModels.map(({id}) =>
                TestFactory.createMasterCategory({
                    infoModelId: id,
                    regionId: region.id,
                    parentId: mcParent.id,
                    userId: user.id
                })
            )
        );

        const product = await TestFactory.createProduct({
            masterCategoryId: mcChildren[0].id,
            userId: user.id,
            regionId: region.id
        });

        await executeInTransaction({authorId: user.id, source: 'ui', stamp: uuid}, async (manager) => {
            product.masterCategoryId = mcChildren[1].id;
            product.status = ProductStatus.ACTIVE;
            await manager.save(Product, product);
        });

        const {list: historyResult} = await getProductHistory.handle({
            context,
            data: {params: {identifier: product.identifier}}
        });

        expect(historyResult).toMatchObject([
            {
                author: {login: user.login},
                mutation: {
                    masterCategory: {
                        old: {id: mcChildren[0].id, infoModel: {id: infoModels[0].id}},
                        new: {id: mcChildren[1].id, infoModel: {id: infoModels[1].id}}
                    }
                }
            },
            {
                mutation: {
                    masterCategory: {
                        old: null,
                        new: {id: mcChildren[0].id, infoModel: {id: infoModels[0].id}}
                    }
                }
            }
        ]);
    });

    it('should change MC without info-model', async () => {
        const attributes = await Promise.all([
            TestFactory.createAttribute({
                userId: user.id,
                attribute: {type: AttributeType.NUMBER, isValueRequired: true, isValueLocalizable: false}
            }),
            TestFactory.createAttribute({
                userId: user.id,
                attribute: {type: AttributeType.STRING, isValueRequired: false, isValueLocalizable: true}
            })
        ]);
        attributes.sort((a, b) => a.id - b.id);

        const infoModel = await TestFactory.createInfoModel({
            regionId: region.id,
            userId: user.id,
            attributes: [
                {id: attributes[0].id, isImportant: true},
                {id: attributes[1].id, isImportant: false}
            ]
        });

        const mcParent = await TestFactory.createMasterCategory({
            infoModelId: infoModel.id,
            regionId: region.id,
            userId: user.id
        });

        const mcChildren = await Promise.all(
            [0, 1].map((sortOrder) =>
                TestFactory.createMasterCategory({
                    infoModelId: infoModel.id,
                    regionId: region.id,
                    parentId: mcParent.id,
                    sortOrder,
                    userId: user.id
                })
            )
        );

        // Transaction #2
        const product = await TestFactory.createProduct({
            masterCategoryId: mcChildren[0].id,
            userId: user.id,
            regionId: region.id
        });

        const SOURCE = 'ui';
        // Transaction #1
        await executeInTransaction({authorId: user.id, source: SOURCE, stamp: uuid}, async (manager) => {
            product.masterCategoryId = mcChildren[1].id;
            product.status = ProductStatus.ACTIVE;
            await manager.save(Product, product);
        });

        const {list: historyResult} = await getProductHistory.handle({
            context,
            data: {params: {identifier: product.identifier}}
        });
        historyResult[1].mutation?.frontCategories?.new.sort((a, b) => a.id - b.id);

        expect(historyResult).toMatchObject([
            {
                author: {login: user.login},
                source: SOURCE,
                mutation: {
                    masterCategory: {
                        old: {id: mcChildren[0].id, infoModel: {id: infoModel.id}},
                        new: {id: mcChildren[1].id, infoModel: {id: infoModel.id}}
                    },
                    status: {old: ProductStatus.DISABLED, new: ProductStatus.ACTIVE}
                }
            },
            {
                author: {login: user.login},
                mutation: {
                    masterCategory: {old: null, new: {id: mcChildren[0].id, infoModel: {id: infoModel.id}}},
                    status: {old: null, new: ProductStatus.DISABLED}
                }
            }
        ]);
    });

    it('should change product status', async () => {
        // Transaction #3
        const product = await TestFactory.createProduct({
            masterCategoryId: (await createMasterCategory(region.id)).id,
            userId: user.id,
            regionId: region.id
        });

        const SOURCE = 'ui';
        // Transaction #2
        await executeInTransaction({authorId: user.id, source: SOURCE, stamp: uuid}, async (manager) => {
            product.status = ProductStatus.ACTIVE;
            await manager.save(Product, product);
        });

        // Transaction #1
        await executeInTransaction({authorId: user.id, source: SOURCE, stamp: uuid}, async (manager) => {
            product.status = ProductStatus.DISABLED;
            await manager.save(Product, product);
        });

        const {list: historyResult} = await getProductHistory.handle({
            context,
            data: {params: {identifier: product.identifier}}
        });

        expect(historyResult).toMatchObject([
            {
                author: {login: user.login},
                source: SOURCE,
                mutation: {
                    status: {old: ProductStatus.ACTIVE, new: ProductStatus.DISABLED}
                }
            },
            {
                author: {login: user.login},
                source: SOURCE,
                mutation: {
                    status: {old: ProductStatus.DISABLED, new: ProductStatus.ACTIVE}
                }
            },
            {
                author: {login: user.login},
                mutation: {
                    status: {old: null, new: ProductStatus.DISABLED}
                }
            }
        ]);
    });

    it('should save correct source', async () => {
        const sources: HistorySource[] = ['ui', 'import', 'manual'];
        for (const source of sources as HistorySource[]) {
            const {id: regionId} = await TestFactory.createRegion();
            // Transaction #3
            const product = await TestFactory.createProduct({
                masterCategoryId: (await createMasterCategory(regionId)).id,
                userId: user.id,
                regionId,
                source
            });

            // Transaction #2
            await executeInTransaction({authorId: user.id, source, stamp: uuid}, async (manager) => {
                product.status = ProductStatus.ACTIVE;
                await manager.save(Product, product);
            });

            // Transaction #1
            await executeInTransaction({authorId: user.id, source, stamp: uuid}, async (manager) => {
                product.status = ProductStatus.DISABLED;
                await manager.save(Product, product);
            });

            const {list: historyResult} = await getProductHistory.handle({
                context,
                data: {params: {identifier: product.identifier}}
            });

            expect(historyResult).toMatchObject([
                {
                    author: {login: user.login},
                    source,
                    mutation: {
                        status: {old: ProductStatus.ACTIVE, new: ProductStatus.DISABLED}
                    }
                },
                {
                    author: {login: user.login},
                    source,
                    mutation: {
                        status: {old: ProductStatus.DISABLED, new: ProductStatus.ACTIVE}
                    }
                },
                {
                    author: {login: user.login},
                    mutation: {
                        status: {old: null, new: ProductStatus.DISABLED}
                    }
                }
            ]);
        }
    });

    it('should save product attribute values in history', async () => {
        const attributes = await Promise.all([
            TestFactory.createAttribute({
                userId: user.id,
                attribute: {type: AttributeType.NUMBER, isValueRequired: true, isValueLocalizable: false}
            }),
            TestFactory.createAttribute({
                userId: user.id,
                attribute: {type: AttributeType.STRING, isValueRequired: false, isValueLocalizable: true}
            })
        ]);

        const infoModel = await TestFactory.createInfoModel({
            regionId: region.id,
            userId: user.id,
            attributes: [
                {id: attributes[0].id, isImportant: true},
                {id: attributes[1].id, isImportant: false}
            ]
        });

        const mc = await TestFactory.createMasterCategory({
            infoModelId: infoModel.id,
            regionId: region.id,
            userId: user.id
        });

        // Transaction #3
        const product = await TestFactory.createProduct({
            masterCategoryId: mc.id,
            userId: user.id,
            regionId: region.id
        });

        // Transaction #2
        const SOURCE = 'ui';
        const pav = await executeInTransaction({authorId: user.id, source: SOURCE, stamp: uuid}, async (manager) =>
            manager.save(ProductAttributeValue, [
                {productId: product.id, value: 123, attributeId: attributes[0].id},
                {productId: product.id, value: 'first value', attributeId: attributes[1].id, langId: lang.id}
            ])
        );

        pav[1].valueText = undefined;
        pav[1].value = 'second value';
        // Transaction #1
        await executeInTransaction({authorId: user.id, source: SOURCE, stamp: uuid}, async (manager) =>
            manager.save(ProductAttributeValue, pav[1])
        );

        const {list: historyResult} = await getProductHistory.handle({
            context,
            data: {params: {identifier: product.identifier}}
        });

        expect(historyResult).toMatchObject([
            {
                author: {login: user.login},
                mutation: {
                    productAttributeValues: [
                        {
                            attribute: {id: attributes[1].id, code: attributes[1].code},
                            value: {old: {[lang.isoCode]: 'first value'}, new: {[lang.isoCode]: 'second value'}}
                        }
                    ]
                }
            },
            {
                author: {login: user.login},
                mutation: {
                    productAttributeValues: orderBy(
                        [
                            {
                                attribute: {id: attributes[0].id, code: attributes[0].code, type: attributes[0].type},
                                value: {old: null, new: 123}
                            },
                            {
                                attribute: {id: attributes[1].id, code: attributes[1].code, type: attributes[1].type},
                                value: {old: {[lang.isoCode]: null}, new: {[lang.isoCode]: 'first value'}}
                            }
                        ],
                        (a) => a.attribute.type // "number" < "string"
                    )
                }
            },
            {} // ignore creating product with master category, already tested above
        ]);
    });

    it('should contain all authors', async () => {
        const anotherUser = await TestFactory.createUser({
            staffData: {
                images: {avatar: 'https://example.com/image.jpg'},
                name: {
                    first: {ru: 'Иван', en: 'Ivan'},
                    last: {ru: 'Иванов', en: 'Ivanov'},
                    middle: '',
                    hidden_middle: false,
                    has_namesake: true
                }
            }
        });
        const product = await TestFactory.createProduct({
            masterCategoryId: (await createMasterCategory(region.id)).id,
            userId: user.id,
            regionId: region.id,
            status: ProductStatus.ACTIVE
        });

        await executeInTransaction({authorId: anotherUser.id, source: 'ui', stamp: uuid}, async (manager) => {
            product.status = ProductStatus.DISABLED;
            await manager.save(Product, product);
        });

        const {list: historyResult} = await getProductHistory.handle({
            context,
            data: {params: {identifier: product.identifier}}
        });

        expect(historyResult).toMatchObject([
            {
                author: {
                    login: anotherUser.login,
                    firstName: anotherUser.staffData.name.first,
                    lastName: anotherUser.staffData.name.last,
                    avatar: anotherUser.staffData.images?.avatar
                }
            },
            {
                author: {
                    login: user.login,
                    firstName: user.staffData.name.first,
                    lastName: user.staffData.name.last,
                    avatar: user.staffData.images?.avatar
                }
            }
        ]);
    });

    it('should save and change attribute_option', async () => {
        const attributes = await Promise.all([
            TestFactory.createAttribute({
                userId: user.id,
                attribute: {type: AttributeType.SELECT, isValueRequired: true, isValueLocalizable: false}
            }),
            TestFactory.createAttribute({
                userId: user.id,
                attribute: {type: AttributeType.MULTISELECT, isValueRequired: false, isValueLocalizable: false}
            })
        ]);

        const infoModel = await TestFactory.createInfoModel({
            regionId: region.id,
            userId: user.id,
            attributes: [
                {id: attributes[0].id, isImportant: true},
                {id: attributes[1].id, isImportant: false}
            ]
        });

        const mc = await TestFactory.createMasterCategory({
            infoModelId: infoModel.id,
            regionId: region.id,
            userId: user.id
        });

        const product = await TestFactory.createProduct({
            masterCategoryId: mc.id,
            userId: user.id,
            regionId: region.id
        });

        const pav = await executeInTransaction({authorId: user.id, source: 'ui', stamp: uuid}, async (manager) =>
            manager.save(ProductAttributeValue, [
                {productId: product.id, value: 'foo', attributeId: attributes[0].id},
                {productId: product.id, value: ['one', 'two'], attributeId: attributes[1].id}
            ])
        );

        await executeInTransaction({authorId: user.id, source: 'ui', stamp: uuid}, async (manager) => {
            return manager.save(ProductAttributeValue, [
                {id: pav[0].id, productId: product.id, value: 'bar', attributeId: attributes[0].id},
                {id: pav[1].id, productId: product.id, value: ['one', 'two', 'three'], attributeId: attributes[1].id}
            ]);
        });

        const {list: historyResult} = await getProductHistory.handle({
            context,
            data: {params: {identifier: product.identifier}}
        });

        historyResult.forEach((h) =>
            h.mutation.productAttributeValues?.sort((a, b) => a.attribute.id - b.attribute.id)
        );
        expect(historyResult).toMatchObject([
            {
                mutation: {
                    productAttributeValues: [
                        {attribute: {id: attributes[0].id, code: attributes[0].code}, value: {old: 'foo', new: 'bar'}},
                        {
                            attribute: {id: attributes[1].id, code: attributes[1].code},
                            value: {old: ['one', 'two'], new: ['one', 'two', 'three']}
                        }
                    ].sort((a, b) => a.attribute.id - b.attribute.id)
                }
            },
            {
                mutation: {
                    productAttributeValues: [
                        {attribute: {id: attributes[0].id, code: attributes[0].code}, value: {old: null, new: 'foo'}},
                        {
                            attribute: {id: attributes[1].id, code: attributes[1].code},
                            value: {old: null, new: ['one', 'two']}
                        }
                    ].sort((a, b) => a.attribute.id - b.attribute.id)
                }
            },
            {}
        ]);
    });

    it('should save then change simple attributes', async () => {
        const values = [
            [AttributeType.NUMBER, 1, 2],
            [AttributeType.STRING, 'initial string', 'final string'],
            [AttributeType.BOOLEAN, false, true],
            [AttributeType.BOOLEAN, true, false],
            [AttributeType.TEXT, 'large initial text', 'large final text']
        ] as [AttributeType, DbAttributeValue, DbAttributeValue][];

        for (const [attributeType, initValue, changedValue] of values) {
            const {id: regionId} = await TestFactory.createRegion();
            const attribute = await TestFactory.createAttribute({
                userId: user.id,
                attribute: {type: attributeType, isValueRequired: true, isArray: true}
            });
            const infoModel = await TestFactory.createInfoModel({
                regionId,
                userId: user.id,
                attributes: [{id: attribute.id, isImportant: true}]
            });

            const mc = await TestFactory.createMasterCategory({
                infoModelId: infoModel.id,
                regionId,
                userId: user.id
            });
            const product = await TestFactory.createProduct({
                masterCategoryId: mc.id,
                userId: user.id,
                regionId
            });

            const pav = await executeInTransaction({authorId: user.id, source: 'ui', stamp: uuid}, async (manager) =>
                manager.save(ProductAttributeValue, {
                    productId: product.id,
                    value: initValue,
                    attributeId: attribute.id
                })
            );

            pav.valueText = undefined;
            pav.valueNumber = undefined;
            pav.valueBoolean = undefined;
            pav.value = changedValue;

            await executeInTransaction({authorId: user.id, source: 'ui', stamp: uuid}, async (manager) =>
                manager.save(ProductAttributeValue, pav)
            );

            const {list: historyResult} = await getProductHistory.handle({
                context,
                data: {params: {identifier: product.identifier}}
            });

            expect(historyResult.map((hr) => hr.mutation?.productAttributeValues)).toMatchObject([
                [{attribute: {id: attribute.id, type: attributeType}, value: {old: initValue, new: changedValue}}],
                [{attribute: {id: attribute.id}, value: {old: null, new: initValue}}],
                undefined
            ]);
        }
    });

    it('should save then change image attributes', async () => {
        const initValue = 'https://example.com/image1.jpg';
        const changedValue = 'https://example.com/image2.jpg';

        const {id: regionId} = region;
        const attribute = await TestFactory.createAttribute({
            userId: user.id,
            attribute: {type: AttributeType.IMAGE, isValueRequired: true, isArray: true}
        });
        const infoModel = await TestFactory.createInfoModel({
            regionId,
            userId: user.id,
            attributes: [{id: attribute.id, isImportant: true}]
        });

        const mc = await TestFactory.createMasterCategory({
            infoModelId: infoModel.id,
            regionId,
            userId: user.id
        });
        const product = await TestFactory.createProduct({
            masterCategoryId: mc.id,
            userId: user.id,
            regionId
        });

        const {initCache, pav} = await executeInTransaction(
            {authorId: user.id, source: 'ui', stamp: uuid},
            async (manager) => {
                const initCache = await manager.save(ImageCache, {url: initValue as string, md5: uuid, meta: {}});
                const pav = await manager.save(ProductAttributeValue, {
                    productId: product.id,
                    value: initValue,
                    attributeId: attribute.id
                });
                return {initCache, pav};
            }
        );

        pav.valueText = undefined;
        pav.valueNumber = undefined;
        pav.valueBoolean = undefined;
        pav.value = changedValue;

        const changedCache = await executeInTransaction(
            {authorId: user.id, source: 'ui', stamp: uuid},
            async (manager) => {
                await manager.save(ProductAttributeValue, pav);
                return manager.save(ImageCache, {url: changedValue as string, md5: uuid, meta: {}});
            }
        );

        const {list: historyResult} = await getProductHistory.handle({
            context,
            data: {params: {identifier: product.identifier}}
        });
        initCache.id = Number(initCache.id);
        changedCache.id = Number(changedCache.id);

        expect(historyResult.map((hr) => hr.mutation?.productAttributeValues)).toMatchObject([
            [
                {
                    attribute: {id: attribute.id, type: AttributeType.IMAGE},
                    value: {old: initCache, new: changedCache}
                }
            ],
            [{attribute: {id: attribute.id}, value: {old: null, new: initCache}}],
            undefined
        ]);
    });

    it('should save then change array attributes', async () => {
        const values = [
            [AttributeType.NUMBER, [1, 15], [1, 20]],
            [AttributeType.STRING, ['first', 'second'], ['third', 'fourth', 'fifth']],
            [AttributeType.BOOLEAN, [true, false, true], [false]],
            [AttributeType.TEXT, ['t1', 't2'], ['t3']]
        ] as [AttributeType, DbAttributeValue, DbAttributeValue][];

        for (const [attributeType, initValue, changedValue] of values) {
            const {id: regionId} = await TestFactory.createRegion();
            const attribute = await TestFactory.createAttribute({
                userId: user.id,
                attribute: {type: attributeType, isValueRequired: true, isArray: true}
            });
            const infoModel = await TestFactory.createInfoModel({
                regionId,
                userId: user.id,
                attributes: [{id: attribute.id, isImportant: true}]
            });

            const mc = await TestFactory.createMasterCategory({
                infoModelId: infoModel.id,
                regionId,
                userId: user.id
            });
            const product = await TestFactory.createProduct({
                masterCategoryId: mc.id,
                userId: user.id,
                regionId
            });

            const pav = await executeInTransaction({authorId: user.id, source: 'ui', stamp: uuid}, async (manager) =>
                manager.save(ProductAttributeValue, {
                    productId: product.id,
                    value: initValue,
                    attributeId: attribute.id
                })
            );

            pav.valueText = undefined;
            pav.valueNumber = undefined;
            pav.valueBoolean = undefined;
            pav.value = changedValue;

            await executeInTransaction({authorId: user.id, source: 'ui', stamp: uuid}, async (manager) =>
                manager.save(ProductAttributeValue, pav)
            );

            const {list: historyResult} = await getProductHistory.handle({
                context,
                data: {params: {identifier: product.identifier}}
            });

            expect(historyResult.map((hr) => hr.mutation?.productAttributeValues)).toMatchObject([
                [{attribute: {id: attribute.id, type: attributeType}, value: {old: initValue, new: changedValue}}],
                [{attribute: {id: attribute.id}, value: {old: null, new: initValue}}],
                undefined
            ]);
        }
    });

    it('should save then change image array attributes with ImageCache', async () => {
        const initValue = ['https://example.com/image1.jpg', 'https://example.com/image2.jpg'];
        const changedValue = ['https://example.com/image2.jpg', 'https://example.com/image3.jpg'];
        const {id: regionId} = region;
        const attribute = await TestFactory.createAttribute({
            userId: user.id,
            attribute: {type: AttributeType.IMAGE, isValueRequired: true, isArray: true}
        });
        const infoModel = await TestFactory.createInfoModel({
            regionId,
            userId: user.id,
            attributes: [{id: attribute.id, isImportant: true}]
        });

        const mc = await TestFactory.createMasterCategory({
            infoModelId: infoModel.id,
            regionId,
            userId: user.id
        });
        const product = await TestFactory.createProduct({
            masterCategoryId: mc.id,
            userId: user.id,
            regionId
        });

        const {initCaches, pav} = await executeInTransaction(
            {authorId: user.id, source: 'ui', stamp: uuid},
            async (manager) => {
                const initCaches = await manager.save(ImageCache, [
                    {url: initValue[0], md5: uuid, meta: {}},
                    {url: initValue[1], md5: uuid, meta: {}}
                ]);
                const pav = await manager.save(ProductAttributeValue, {
                    productId: product.id,
                    value: initValue,
                    attributeId: attribute.id
                });
                return {initCaches, pav};
            }
        );

        pav.valueText = undefined;
        pav.valueNumber = undefined;
        pav.valueBoolean = undefined;
        pav.value = changedValue;

        const changedCaches = await executeInTransaction(
            {authorId: user.id, source: 'ui', stamp: uuid},
            async (manager) => {
                await manager.save(ProductAttributeValue, pav);
                const cache = await manager.save(ImageCache, {url: changedValue[1], md5: uuid, meta: {}});
                return [initCaches[1], cache];
            }
        );

        const {list: historyResult} = await getProductHistory.handle({
            context,
            data: {params: {identifier: product.identifier}}
        });
        initCaches[0].id = Number(initCaches[0].id);
        initCaches[1].id = Number(initCaches[1].id);
        changedCaches[0].id = Number(changedCaches[0].id);
        changedCaches[1].id = Number(changedCaches[1].id);

        expect(historyResult.map((hr) => hr.mutation?.productAttributeValues)).toMatchObject([
            [
                {
                    attribute: {id: attribute.id, type: AttributeType.IMAGE},
                    value: {old: initCaches, new: changedCaches}
                }
            ],
            [{attribute: {id: attribute.id}, value: {old: null, new: initCaches}}],
            undefined
        ]);
    });

    it('should save then change image array attributes without ImageCache', async () => {
        const initValue = ['https://example.com/image1.jpg', 'https://example.com/image2.jpg'];
        const changedValue = ['https://example.com/image2.jpg', 'https://example.com/image3.jpg'];
        const {id: regionId} = region;
        const attribute = await TestFactory.createAttribute({
            userId: user.id,
            attribute: {type: AttributeType.IMAGE, isValueRequired: true, isArray: true}
        });
        const infoModel = await TestFactory.createInfoModel({
            regionId,
            userId: user.id,
            attributes: [{id: attribute.id, isImportant: true}]
        });

        const mc = await TestFactory.createMasterCategory({
            infoModelId: infoModel.id,
            regionId,
            userId: user.id
        });
        const product = await TestFactory.createProduct({
            masterCategoryId: mc.id,
            userId: user.id,
            regionId
        });

        const pav = await executeInTransaction({authorId: user.id, source: 'ui', stamp: uuid}, async (manager) =>
            manager.save(ProductAttributeValue, {
                productId: product.id,
                value: initValue,
                attributeId: attribute.id
            })
        );

        pav.valueText = undefined;
        pav.valueNumber = undefined;
        pav.valueBoolean = undefined;
        pav.value = changedValue;

        await executeInTransaction({authorId: user.id, source: 'ui', stamp: uuid}, async (manager) =>
            manager.save(ProductAttributeValue, pav)
        );

        const {list: historyResult} = await getProductHistory.handle({
            context,
            data: {params: {identifier: product.identifier}}
        });

        expect(historyResult.map((hr) => hr.mutation?.productAttributeValues)).toMatchObject([
            [
                {
                    attribute: {id: attribute.id, type: AttributeType.IMAGE},
                    value: {
                        old: initValue.map((url) => ({url})),
                        new: changedValue.map((url) => ({url}))
                    }
                }
            ],
            [{attribute: {id: attribute.id}, value: {old: null, new: initValue.map((url) => ({url}))}}],
            undefined
        ]);
    });

    it('should return merged localized product attribute values', async () => {
        const {id: regionId} = region;
        const [lang2, lang3] = await Promise.all([TestFactory.createLang(), TestFactory.createLang()]);
        const [locAttribute, locAttributeReadOnly, simpleAttribute] = await Promise.all([
            TestFactory.createAttribute({
                userId: user.id,
                attribute: {type: AttributeType.STRING, isValueRequired: true, isValueLocalizable: true}
            }),
            TestFactory.createAttribute({
                userId: user.id,
                attribute: {type: AttributeType.STRING, isValueRequired: true, isValueLocalizable: true}
            }),
            TestFactory.createAttribute({
                userId: user.id,
                attribute: {type: AttributeType.STRING, isValueRequired: true}
            })
        ]);
        const infoModel = await TestFactory.createInfoModel({
            regionId,
            userId: user.id,
            attributes: [locAttribute, locAttributeReadOnly, simpleAttribute].map(({id}) => ({id, isImportant: true}))
        });

        const mc = await TestFactory.createMasterCategory({
            infoModelId: infoModel.id,
            regionId,
            userId: user.id
        });
        const product = await TestFactory.createProduct({
            masterCategoryId: mc.id,
            userId: user.id,
            regionId
        });

        const locPav = await TestFactory.createLocalizedProductAttributeValue({
            productId: product.id,
            attributeId: locAttribute.id,
            userId: user.id,
            values: [
                {langId: lang.id, value: 'one'},
                {langId: lang2.id, value: 'two'},
                {langId: lang3.id, value: 'three'}
            ]
        });
        await TestFactory.createLocalizedProductAttributeValue({
            productId: product.id,
            attributeId: locAttributeReadOnly.id,
            userId: user.id,
            values: [
                {langId: lang.id, value: 'one RO'},
                {langId: lang2.id, value: 'two RO'},
                {langId: lang3.id, value: 'three RO'}
            ]
        });
        const simplePav = await TestFactory.createProductAttributeValue({
            productId: product.id,
            attributeId: simpleAttribute.id,
            userId: user.id,
            value: 'simple value'
        });

        await executeInTransaction({authorId: user.id, source: 'ui', stamp: uuid}, async (manager) => {
            locPav[0].valueText = undefined;
            locPav[0].value = 'one+';
            locPav[1].valueText = undefined;
            locPav[1].value = 'two+';
            simplePav.valueText = undefined;
            simplePav.value = 'another value';
            return manager.save(ProductAttributeValue, [locPav[0], locPav[1], simplePav]);
        });

        await executeInTransaction({authorId: user.id, source: 'ui', stamp: uuid}, async (manager) => {
            locPav[1].valueText = undefined;
            locPav[1].value = 'two++';
            return manager.save(ProductAttributeValue, locPav[1]);
        });

        const {list: historyResult} = await getProductHistory.handle({
            context,
            data: {params: {identifier: product.identifier}}
        });

        expect(historyResult.map((hr) => hr.mutation?.productAttributeValues)).toMatchObject([
            [
                {
                    attribute: {id: locAttribute.id, type: locAttribute.type},
                    value: {
                        old: {[lang.isoCode]: 'one+', [lang2.isoCode]: 'two+', [lang3.isoCode]: 'three'},
                        new: {[lang.isoCode]: 'one+', [lang2.isoCode]: 'two++', [lang3.isoCode]: 'three'}
                    }
                }
            ],
            [
                {
                    attribute: {id: locAttribute.id, type: locAttribute.type},
                    value: {
                        old: {[lang.isoCode]: 'one', [lang2.isoCode]: 'two', [lang3.isoCode]: 'three'},
                        new: {[lang.isoCode]: 'one+', [lang2.isoCode]: 'two+', [lang3.isoCode]: 'three'}
                    }
                },
                {
                    attribute: {id: simpleAttribute.id, type: simpleAttribute.type},
                    value: {old: 'simple value', new: 'another value'}
                }
            ],
            [
                {
                    attribute: {id: locAttribute.id, type: locAttribute.type},
                    value: {
                        old: {[lang.isoCode]: null, [lang2.isoCode]: null, [lang3.isoCode]: null},
                        new: {[lang.isoCode]: 'one', [lang2.isoCode]: 'two', [lang3.isoCode]: 'three'}
                    }
                },
                {
                    attribute: {id: locAttributeReadOnly.id, type: locAttributeReadOnly.type},
                    value: {
                        old: {[lang.isoCode]: null, [lang2.isoCode]: null, [lang3.isoCode]: null},
                        new: {[lang.isoCode]: 'one RO', [lang2.isoCode]: 'two RO', [lang3.isoCode]: 'three RO'}
                    }
                },
                {
                    attribute: {id: simpleAttribute.id, type: simpleAttribute.type},
                    value: {old: null, new: 'simple value'}
                }
            ]
        ]);
    });

    it('should throw error if product does not exist', async () => {
        let error = null;
        const unknownId = Number.MAX_SAFE_INTEGER;

        try {
            await getProductHistory.handle({
                context,
                data: {params: {identifier: unknownId}}
            });
        } catch (err) {
            error = err;
        }

        expect(error).toBeInstanceOf(EntityNotFoundError);
        expect(error.parameters).toMatchObject({entity: 'Product'});
    });
});
