/* eslint-disable @typescript-eslint/no-explicit-any */
import {times} from 'lodash';
import {beforeEach, describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';

import type {Attribute} from '@/src/entities/attribute/entity';
import type {Region} from '@/src/entities/region/entity';
import type {User} from '@/src/entities/user/entity';
import type {ApiRequestContext} from 'server/routes/api/api-handler';
import {AttributeType} from 'types/attribute';

import {getProductsHandler} from './get-products';

const BASE_BODY = {
    limit: 10,
    offset: 0
};

async function createBase(region: Region, user: User, mcParentId?: number) {
    const im = await TestFactory.createInfoModel({
        regionId: region.id,
        userId: user.id
    });

    const mc = await TestFactory.createMasterCategory({
        userId: user.id,
        regionId: region.id,
        infoModelId: im.id,
        ...(mcParentId ? {parentId: mcParentId} : {})
    });

    return {im, mc};
}

async function linkImportantAttribute(user: User, infoModelId: number, attributeId: number) {
    await TestFactory.linkAttributesToInfoModel({
        userId: user.id,
        infoModelId,
        attributes: [
            {
                id: attributeId,
                isImportant: true
            }
        ]
    });
}

async function linkNotImportantAttribute(user: User, infoModelId: number, attributeId: number) {
    await TestFactory.linkAttributesToInfoModel({
        userId: user.id,
        infoModelId,
        attributes: [
            {
                id: attributeId,
                isImportant: false
            }
        ]
    });
}

describe('get products by attributes filters', () => {
    let user: User;
    let region: Region;
    let context: ApiRequestContext;

    beforeEach(async () => {
        user = await TestFactory.createUser();
        region = await TestFactory.createRegion();
        context = await TestFactory.createApiContext({region, user});
    });

    async function createAttributeAndLink(params: DeepPartial<Attribute>, infoModelId?: number | null) {
        const attr = await TestFactory.createAttribute({
            userId: user.id,
            attribute: params
        });

        if (infoModelId) {
            await TestFactory.linkAttributesToInfoModel({
                userId: user.id,
                attributes: [attr],
                infoModelId
            });
        }

        return attr;
    }

    it('should return products by boolean', async () => {
        const {mc} = await createBase(region, user);

        const attr = await createAttributeAndLink({type: AttributeType.BOOLEAN}, mc.infoModelId);

        const products = await Promise.all([
            TestFactory.createProduct({
                userId: user.id,
                masterCategoryId: mc.id,
                regionId: region.id
            }),
            TestFactory.createProduct({
                userId: user.id,
                masterCategoryId: mc.id,
                regionId: region.id
            })
        ]);

        await Promise.all([
            TestFactory.createProductAttributeValue({
                userId: user.id,
                productId: products[0].id,
                attributeId: attr.id,
                value: true
            }),
            TestFactory.createProductAttributeValue({
                userId: user.id,
                productId: products[1].id,
                attributeId: attr.id,
                value: false
            })
        ]);

        const suites = [
            {
                value: true,
                expectedIds: [products[0].identifier]
            },
            {
                value: false,
                expectedIds: [products[1].identifier]
            }
        ];

        for (const suite of suites) {
            const res = await getProductsHandler.handle({
                context,
                data: {
                    body: {
                        ...BASE_BODY,
                        filters: {
                            attributes: {
                                [attr.code]: suite.value
                            }
                        }
                    }
                }
            });

            expect(res.totalCount).toBe(suite.expectedIds.length);
            expect(res.list.map((it: any) => it.identifier)).toEqual(suite.expectedIds);
        }
    });

    it('should return products by select', async () => {
        const {mc} = await createBase(region, user);

        const attr = await createAttributeAndLink({type: AttributeType.SELECT}, mc.infoModelId);

        const products = await Promise.all([
            TestFactory.createProduct({
                userId: user.id,
                masterCategoryId: mc.id,
                regionId: region.id
            }),
            TestFactory.createProduct({
                userId: user.id,
                masterCategoryId: mc.id,
                regionId: region.id
            }),
            TestFactory.createProduct({
                userId: user.id,
                masterCategoryId: mc.id,
                regionId: region.id
            })
        ]);

        await Promise.all([
            TestFactory.createProductAttributeValue({
                userId: user.id,
                productId: products[0].id,
                attributeId: attr.id,
                value: 'foo'
            }),
            TestFactory.createProductAttributeValue({
                userId: user.id,
                productId: products[1].id,
                attributeId: attr.id,
                value: 'bar'
            }),
            TestFactory.createProductAttributeValue({
                userId: user.id,
                productId: products[2].id,
                attributeId: attr.id,
                value: 'zxc'
            })
        ]);

        const suites = [
            {
                value: ['foo', 'bar'],
                expectedIds: [products[0].identifier, products[1].identifier]
            },
            {
                value: ['zxc', 'undefined'],
                expectedIds: [products[2].identifier]
            }
        ];

        for (const suite of suites) {
            const res = await getProductsHandler.handle({
                context,
                data: {
                    body: {
                        ...BASE_BODY,
                        filters: {
                            attributes: {
                                [attr.code]: suite.value
                            }
                        }
                    }
                }
            });

            expect(res.totalCount).toBe(suite.expectedIds.length);
            expect(res.list.map((it: any) => it.identifier).sort()).toEqual(suite.expectedIds.sort());
        }
    });

    it('should return products by multiselect', async () => {
        const {mc} = await createBase(region, user);
        const attr = await createAttributeAndLink({type: AttributeType.MULTISELECT}, mc.infoModelId);

        const products = await Promise.all([
            TestFactory.createProduct({
                userId: user.id,
                masterCategoryId: mc.id,
                regionId: region.id
            }),
            TestFactory.createProduct({
                userId: user.id,
                masterCategoryId: mc.id,
                regionId: region.id
            }),
            TestFactory.createProduct({
                userId: user.id,
                masterCategoryId: mc.id,
                regionId: region.id
            })
        ]);

        await Promise.all([
            TestFactory.createProductAttributeValue({
                userId: user.id,
                productId: products[0].id,
                attributeId: attr.id,
                value: ['foo', 'bar']
            }),
            TestFactory.createProductAttributeValue({
                userId: user.id,
                productId: products[1].id,
                attributeId: attr.id,
                value: ['zxc', 'poo']
            }),
            TestFactory.createProductAttributeValue({
                userId: user.id,
                productId: products[2].id,
                attributeId: attr.id,
                value: ['boo', 'qwe']
            })
        ]);

        const suites = [
            {
                value: ['bar', 'zxc'],
                expectedIds: [products[0].identifier, products[1].identifier]
            },
            {
                value: ['boo', 'undefined'],
                expectedIds: [products[2].identifier]
            }
        ];

        for (const suite of suites) {
            const res = await getProductsHandler.handle({
                context,
                data: {
                    body: {
                        ...BASE_BODY,
                        filters: {
                            attributes: {
                                [attr.code]: suite.value
                            }
                        }
                    }
                }
            });

            expect(res.totalCount).toBe(suite.expectedIds.length);
            expect(res.list.map((it: any) => it.identifier).sort()).toEqual(suite.expectedIds.sort());
        }
    });

    it('should return products by string contain', async () => {
        const {mc} = await createBase(region, user);

        const attr = await createAttributeAndLink({type: AttributeType.STRING, isArray: true}, mc.infoModelId);

        const products = await Promise.all([
            TestFactory.createProduct({
                userId: user.id,
                masterCategoryId: mc.id,
                regionId: region.id
            }),
            TestFactory.createProduct({
                userId: user.id,
                masterCategoryId: mc.id,
                regionId: region.id
            }),
            TestFactory.createProduct({
                userId: user.id,
                masterCategoryId: mc.id,
                regionId: region.id
            })
        ]);

        await Promise.all([
            TestFactory.createProductAttributeValue({
                userId: user.id,
                productId: products[0].id,
                attributeId: attr.id,
                value: ['qweASDzxc', 'tyuASDzxc']
            }),
            TestFactory.createProductAttributeValue({
                userId: user.id,
                productId: products[1].id,
                attributeId: attr.id,
                value: ['qweFOO', 'tyuooo']
            }),
            TestFactory.createProductAttributeValue({
                userId: user.id,
                productId: products[2].id,
                attributeId: attr.id,
                value: ['qweZXCzxc', 'mnbhjkuio']
            })
        ]);

        const suites = [
            {
                value: ['asd', 'zxc'],
                expectedIds: [products[0].identifier, products[2].identifier]
            },
            {
                value: ['foo', 'undefined'],
                expectedIds: [products[1].identifier]
            }
        ];

        for (const suite of suites) {
            const res = await getProductsHandler.handle({
                context,
                data: {
                    body: {
                        ...BASE_BODY,
                        filters: {
                            attributes: {
                                [attr.code]: {
                                    action: 'contain',
                                    values: suite.value
                                }
                            }
                        }
                    }
                }
            });

            expect(res.totalCount).toBe(suite.expectedIds.length);
            expect(res.list.map((it: any) => it.identifier).sort()).toEqual(suite.expectedIds.sort());
        }
    });

    it('should return products by string not-contain', async () => {
        const {mc} = await createBase(region, user);

        const attr = await createAttributeAndLink({type: AttributeType.STRING, isArray: true}, mc.infoModelId);

        const products = await Promise.all(
            times(4).map(() =>
                TestFactory.createProduct({
                    userId: user.id,
                    masterCategoryId: mc.id,
                    regionId: region.id
                })
            )
        );

        await Promise.all([
            TestFactory.createProductAttributeValue({
                userId: user.id,
                productId: products[0].id,
                attributeId: attr.id,
                value: ['qweASDzxc', 'tyuASDzxc']
            }),
            TestFactory.createProductAttributeValue({
                userId: user.id,
                productId: products[1].id,
                attributeId: attr.id,
                value: ['qweFOO', 'tyuooo']
            }),
            TestFactory.createProductAttributeValue({
                userId: user.id,
                productId: products[2].id,
                attributeId: attr.id,
                value: ['qweZXCzxc', 'mnbhjkuio']
            }),
            TestFactory.createProductAttributeValue({
                userId: user.id,
                productId: products[3].id,
                attributeId: attr.id,
                value: ['some aSd value']
            })
        ]);

        const suites = [
            {
                value: ['asd', 'zxc'],
                expectedIds: [products[1].identifier]
            },
            {
                value: ['foo', 'undefined'],
                expectedIds: [products[0].identifier, products[2].identifier, products[3].identifier]
            },
            {
                value: ['asd'],
                expectedIds: [products[1].identifier, products[2].identifier]
            }
        ];

        for (const suite of suites) {
            const res = await getProductsHandler.handle({
                context,
                data: {
                    body: {
                        ...BASE_BODY,
                        filters: {
                            attributes: {
                                [attr.code]: {
                                    action: 'not-contain',
                                    values: suite.value
                                }
                            }
                        }
                    }
                }
            });

            expect(res.totalCount).toBe(suite.expectedIds.length);
            expect(res.list.map((it: any) => it.identifier).sort()).toEqual(suite.expectedIds.sort());
        }
    });

    it('should return products by string equal', async () => {
        const {mc} = await createBase(region, user);

        const attr = await createAttributeAndLink({type: AttributeType.STRING, isArray: true}, mc.infoModelId);

        const products = await Promise.all([
            TestFactory.createProduct({
                userId: user.id,
                masterCategoryId: mc.id,
                regionId: region.id
            }),
            TestFactory.createProduct({
                userId: user.id,
                masterCategoryId: mc.id,
                regionId: region.id
            }),
            TestFactory.createProduct({
                userId: user.id,
                masterCategoryId: mc.id,
                regionId: region.id
            })
        ]);

        await Promise.all([
            TestFactory.createProductAttributeValue({
                userId: user.id,
                productId: products[0].id,
                attributeId: attr.id,
                value: ['asd', 'zxc']
            }),
            TestFactory.createProductAttributeValue({
                userId: user.id,
                productId: products[1].id,
                attributeId: attr.id,
                value: ['rty', 'qwe']
            }),
            TestFactory.createProductAttributeValue({
                userId: user.id,
                productId: products[2].id,
                attributeId: attr.id,
                value: ['uio', 'ghj']
            })
        ]);

        const suites = [
            {
                value: ['asd', 'qwe'],
                expectedIds: [products[0].identifier, products[1].identifier]
            },
            {
                value: ['uio', 'undefined'],
                expectedIds: [products[2].identifier]
            }
        ];

        for (const suite of suites) {
            const res = await getProductsHandler.handle({
                context,
                data: {
                    body: {
                        ...BASE_BODY,
                        filters: {
                            attributes: {
                                [attr.code]: {
                                    action: 'equal',
                                    values: suite.value
                                }
                            }
                        }
                    }
                }
            });

            expect(res.totalCount).toBe(suite.expectedIds.length);
            expect(res.list.map((it: any) => it.identifier).sort()).toEqual(suite.expectedIds.sort());
        }
    });

    it('should return products by string not equal', async () => {
        const {mc} = await createBase(region, user);

        const attr = await createAttributeAndLink({type: AttributeType.STRING, isArray: true}, mc.infoModelId);

        const products = await Promise.all([
            TestFactory.createProduct({
                userId: user.id,
                masterCategoryId: mc.id,
                regionId: region.id
            }),
            TestFactory.createProduct({
                userId: user.id,
                masterCategoryId: mc.id,
                regionId: region.id
            }),
            TestFactory.createProduct({
                userId: user.id,
                masterCategoryId: mc.id,
                regionId: region.id
            })
        ]);

        await Promise.all([
            TestFactory.createProductAttributeValue({
                userId: user.id,
                productId: products[0].id,
                attributeId: attr.id,
                value: ['asd', 'zxc']
            }),
            TestFactory.createProductAttributeValue({
                userId: user.id,
                productId: products[1].id,
                attributeId: attr.id,
                value: ['rty', 'qwe']
            }),
            TestFactory.createProductAttributeValue({
                userId: user.id,
                productId: products[2].id,
                attributeId: attr.id,
                value: ['uio', 'ghj']
            })
        ]);

        const suites = [
            {
                value: ['asd', 'qwe'],
                expectedIds: [products[2].identifier]
            },
            {
                value: ['uio'],
                expectedIds: [products[0].identifier, products[1].identifier]
            }
        ];

        for (const suite of suites) {
            const res = await getProductsHandler.handle({
                context,
                data: {
                    body: {
                        ...BASE_BODY,
                        filters: {
                            attributes: {
                                [attr.code]: {
                                    action: 'not-equal',
                                    values: suite.value
                                }
                            }
                        }
                    }
                }
            });

            expect(res.totalCount).toBe(suite.expectedIds.length);
            expect(res.list.map((it: any) => it.identifier).sort()).toEqual(suite.expectedIds.sort());
        }
    });

    it('should return products by string array-length', async () => {
        const {mc} = await createBase(region, user);

        const attr = await createAttributeAndLink({type: AttributeType.STRING, isArray: true}, mc.infoModelId);

        const products = await Promise.all(
            times(5).map(() =>
                TestFactory.createProduct({
                    userId: user.id,
                    masterCategoryId: mc.id,
                    regionId: region.id
                })
            )
        );

        await Promise.all([
            TestFactory.createProductAttributeValue({
                userId: user.id,
                productId: products[0].id,
                attributeId: attr.id,
                value: ['qweASDzxc']
            }),
            TestFactory.createProductAttributeValue({
                userId: user.id,
                productId: products[1].id,
                attributeId: attr.id,
                value: ['qweFOO', 'tyuooo']
            }),
            TestFactory.createProductAttributeValue({
                userId: user.id,
                productId: products[2].id,
                attributeId: attr.id,
                value: ['qweZXCzxc', 'mnbhjkuio', 'tyuASDzxc']
            }),
            TestFactory.createProductAttributeValue({
                userId: user.id,
                productId: products[3].id,
                attributeId: attr.id,
                value: ['some aSd value', 'qweZXCzxc', 'mnbhjkuio', 'tyuASDzxc']
            })
            // Один товар с пустым значением атрибута
        ]);

        const suites = [
            {
                value: [null, null],
                expectedIds: [
                    products[0].identifier,
                    products[1].identifier,
                    products[2].identifier,
                    products[3].identifier,
                    products[4].identifier
                ]
            },
            {
                value: [null, 3],
                expectedIds: [
                    products[0].identifier,
                    products[1].identifier,
                    products[2].identifier,
                    products[4].identifier
                ]
            },
            {
                value: [3, null],
                expectedIds: [products[2].identifier, products[3].identifier]
            },
            {
                value: [2, 3],
                expectedIds: [products[1].identifier, products[2].identifier]
            },
            {
                value: [0, 2],
                expectedIds: [products[0].identifier, products[1].identifier, products[4].identifier]
            },
            {
                value: [0, null],
                expectedIds: [
                    products[0].identifier,
                    products[1].identifier,
                    products[2].identifier,
                    products[3].identifier,
                    products[4].identifier
                ]
            }
        ];

        for (const suite of suites) {
            const res = await getProductsHandler.handle({
                context,
                data: {
                    body: {
                        ...BASE_BODY,
                        filters: {
                            attributes: {
                                [attr.code]: {
                                    action: 'array-length',
                                    values: suite.value
                                }
                            }
                        }
                    }
                }
            });

            expect(res.totalCount).toBe(suite.expectedIds.length);
            expect(res.list.map((it: any) => it.identifier).sort()).toEqual(suite.expectedIds.sort());
        }
    });

    it('should return products by number range', async () => {
        const {mc} = await createBase(region, user);

        const attr = await createAttributeAndLink({type: AttributeType.NUMBER, isArray: true}, mc.infoModelId);

        const products = await Promise.all([
            TestFactory.createProduct({
                userId: user.id,
                masterCategoryId: mc.id,
                regionId: region.id
            }),
            TestFactory.createProduct({
                userId: user.id,
                masterCategoryId: mc.id,
                regionId: region.id
            }),
            TestFactory.createProduct({
                userId: user.id,
                masterCategoryId: mc.id,
                regionId: region.id
            })
        ]);

        await Promise.all([
            TestFactory.createProductAttributeValue({
                userId: user.id,
                productId: products[0].id,
                attributeId: attr.id,
                value: [1, 2]
            }),
            TestFactory.createProductAttributeValue({
                userId: user.id,
                productId: products[1].id,
                attributeId: attr.id,
                value: [0.1, 0.4]
            }),
            TestFactory.createProductAttributeValue({
                userId: user.id,
                productId: products[2].id,
                attributeId: attr.id,
                value: [10, 11]
            })
        ]);

        const suites = [
            {
                value: [null, 1.1],
                expectedIds: [products[0].identifier, products[1].identifier]
            },
            {
                value: [0.1, 1],
                expectedIds: [products[1].identifier]
            },
            {
                value: [0.2, 2],
                expectedIds: [products[0].identifier, products[1].identifier]
            },
            {
                value: [5, null],
                expectedIds: [products[2].identifier]
            }
        ];

        for (const suite of suites) {
            const res = await getProductsHandler.handle({
                context,
                data: {
                    body: {
                        ...BASE_BODY,
                        filters: {
                            attributes: {
                                [attr.code]: {
                                    action: 'range',
                                    values: suite.value
                                }
                            }
                        }
                    }
                }
            });

            expect(res.totalCount).toBe(suite.expectedIds.length);
            expect(res.list.map((it: any) => it.identifier).sort()).toEqual(suite.expectedIds.sort());
        }
    });

    it('should return products by number equal', async () => {
        const {mc} = await createBase(region, user);

        const attr = await createAttributeAndLink({type: AttributeType.NUMBER, isArray: true}, mc.infoModelId);

        const products = await Promise.all([
            TestFactory.createProduct({
                userId: user.id,
                masterCategoryId: mc.id,
                regionId: region.id
            }),
            TestFactory.createProduct({
                userId: user.id,
                masterCategoryId: mc.id,
                regionId: region.id
            }),
            TestFactory.createProduct({
                userId: user.id,
                masterCategoryId: mc.id,
                regionId: region.id
            })
        ]);

        await Promise.all([
            TestFactory.createProductAttributeValue({
                userId: user.id,
                productId: products[0].id,
                attributeId: attr.id,
                value: [1, 2]
            }),
            TestFactory.createProductAttributeValue({
                userId: user.id,
                productId: products[1].id,
                attributeId: attr.id,
                value: [0.4, 5]
            }),
            TestFactory.createProductAttributeValue({
                userId: user.id,
                productId: products[2].id,
                attributeId: attr.id,
                value: [10, 11]
            })
        ]);

        const suites = [
            {
                value: [1, 0.4],
                expectedIds: [products[0].identifier, products[1].identifier]
            },
            {
                value: [10, 99999],
                expectedIds: [products[2].identifier]
            }
        ];

        for (const suite of suites) {
            const res = await getProductsHandler.handle({
                context,
                data: {
                    body: {
                        ...BASE_BODY,
                        filters: {
                            attributes: {
                                [attr.code]: {
                                    action: 'equal',
                                    values: suite.value
                                }
                            }
                        }
                    }
                }
            });

            expect(res.totalCount).toBe(suite.expectedIds.length);
            expect(res.list.map((it: any) => it.identifier).sort()).toEqual(suite.expectedIds.sort());
        }
    });

    it('should return products by number not equal', async () => {
        const {mc} = await createBase(region, user);

        const attr = await createAttributeAndLink({type: AttributeType.NUMBER, isArray: true}, mc.infoModelId);

        const products = await Promise.all([
            TestFactory.createProduct({
                userId: user.id,
                masterCategoryId: mc.id,
                regionId: region.id
            }),
            TestFactory.createProduct({
                userId: user.id,
                masterCategoryId: mc.id,
                regionId: region.id
            }),
            TestFactory.createProduct({
                userId: user.id,
                masterCategoryId: mc.id,
                regionId: region.id
            })
        ]);

        await Promise.all([
            TestFactory.createProductAttributeValue({
                userId: user.id,
                productId: products[0].id,
                attributeId: attr.id,
                value: [1, 2]
            }),
            TestFactory.createProductAttributeValue({
                userId: user.id,
                productId: products[1].id,
                attributeId: attr.id,
                value: [0.4, 5]
            }),
            TestFactory.createProductAttributeValue({
                userId: user.id,
                productId: products[2].id,
                attributeId: attr.id,
                value: [10, 11]
            })
        ]);

        const suites = [
            {
                value: [1, 0.4],
                expectedIds: [products[2].identifier]
            },
            {
                value: [10],
                expectedIds: [products[0].identifier, products[1].identifier]
            }
        ];

        for (const suite of suites) {
            const res = await getProductsHandler.handle({
                context,
                data: {
                    body: {
                        ...BASE_BODY,
                        filters: {
                            attributes: {
                                [attr.code]: {
                                    action: 'not-equal',
                                    values: suite.value
                                }
                            }
                        }
                    }
                }
            });

            expect(res.totalCount).toBe(suite.expectedIds.length);
            expect(res.list.map((it: any) => it.identifier).sort()).toEqual(suite.expectedIds.sort());
        }
    });

    it('should return products by number array-length', async () => {
        const {mc} = await createBase(region, user);

        const attr = await createAttributeAndLink({type: AttributeType.NUMBER, isArray: true}, mc.infoModelId);

        const products = await Promise.all(
            times(5).map(() =>
                TestFactory.createProduct({
                    userId: user.id,
                    masterCategoryId: mc.id,
                    regionId: region.id
                })
            )
        );

        await Promise.all([
            TestFactory.createProductAttributeValue({
                userId: user.id,
                productId: products[0].id,
                attributeId: attr.id,
                value: [1]
            }),
            TestFactory.createProductAttributeValue({
                userId: user.id,
                productId: products[1].id,
                attributeId: attr.id,
                value: [1, 2]
            }),
            TestFactory.createProductAttributeValue({
                userId: user.id,
                productId: products[2].id,
                attributeId: attr.id,
                value: [1, 2, 3]
            }),
            TestFactory.createProductAttributeValue({
                userId: user.id,
                productId: products[3].id,
                attributeId: attr.id,
                value: [1, 2, 3, 4]
            })
            // Один товар с пустым значением атрибута
        ]);

        const suites = [
            {
                value: [null, null],
                expectedIds: [
                    products[0].identifier,
                    products[1].identifier,
                    products[2].identifier,
                    products[3].identifier,
                    products[4].identifier
                ]
            },
            {
                value: [null, 3],
                expectedIds: [
                    products[0].identifier,
                    products[1].identifier,
                    products[2].identifier,
                    products[4].identifier
                ]
            },
            {
                value: [3, null],
                expectedIds: [products[2].identifier, products[3].identifier]
            },
            {
                value: [2, 3],
                expectedIds: [products[1].identifier, products[2].identifier]
            },
            {
                value: [0, 2],
                expectedIds: [products[0].identifier, products[1].identifier, products[4].identifier]
            },
            {
                value: [0, null],
                expectedIds: [
                    products[0].identifier,
                    products[1].identifier,
                    products[2].identifier,
                    products[3].identifier,
                    products[4].identifier
                ]
            }
        ];

        for (const suite of suites) {
            const res = await getProductsHandler.handle({
                context,
                data: {
                    body: {
                        ...BASE_BODY,
                        filters: {
                            attributes: {
                                [attr.code]: {
                                    action: 'array-length',
                                    values: suite.value
                                }
                            }
                        }
                    }
                }
            });

            expect(res.totalCount).toBe(suite.expectedIds.length);
            expect(res.list.map((it: any) => it.identifier).sort()).toEqual(suite.expectedIds.sort());
        }
    });

    it('should return products by string is not defined (null)', async () => {
        const {mc} = await createBase(region, user);

        const attr = await createAttributeAndLink({type: AttributeType.STRING, isArray: true}, mc.infoModelId);

        const products = await Promise.all(
            Array.from({length: 3}, () =>
                TestFactory.createProduct({
                    userId: user.id,
                    masterCategoryId: mc.id,
                    regionId: region.id
                })
            )
        );

        await Promise.all(
            products.slice(0, -1).map(({id}) =>
                TestFactory.createProductAttributeValue({
                    userId: user.id,
                    productId: id,
                    attributeId: attr.id,
                    value: [id, id + 1, id - 1].map((n) => `foo_${n}`)
                })
            )
        );

        const res = await getProductsHandler.handle({
            context,
            data: {
                body: {
                    ...BASE_BODY,
                    filters: {
                        attributes: {
                            [attr.code]: {
                                action: 'null',
                                values: []
                            }
                        }
                    }
                }
            }
        });

        expect(res.totalCount).toBe(1);
        expect(res.list.map((it: any) => it.identifier).sort()).toEqual([products[2].identifier]);
    });

    it('should return products by string is defined (not-null)', async () => {
        const {mc} = await createBase(region, user);

        const attr = await createAttributeAndLink({type: AttributeType.STRING, isArray: true}, mc.infoModelId);

        const products = await Promise.all(
            Array.from({length: 3}, () =>
                TestFactory.createProduct({
                    userId: user.id,
                    masterCategoryId: mc.id,
                    regionId: region.id
                })
            )
        );

        await Promise.all(
            products.slice(0, -1).map(({id}) =>
                TestFactory.createProductAttributeValue({
                    userId: user.id,
                    productId: id,
                    attributeId: attr.id,
                    value: [id, id + 1, id - 1].map((n) => `foo_${n}`)
                })
            )
        );

        const res = await getProductsHandler.handle({
            context,
            data: {
                body: {
                    ...BASE_BODY,
                    filters: {
                        attributes: {
                            [attr.code]: {
                                action: 'not-null',
                                values: []
                            }
                        }
                    }
                }
            }
        });

        expect(res.totalCount).toBe(2);
        expect(res.list.map((it: any) => it.identifier).sort()).toEqual(
            products
                .slice(0, -1)
                .map((it: any) => it.identifier)
                .sort()
        );
    });

    it('should return products by number is not defined (null)', async () => {
        const {mc} = await createBase(region, user);

        const attr = await createAttributeAndLink({type: AttributeType.NUMBER, isArray: true}, mc.infoModelId);

        const products = await Promise.all(
            Array.from({length: 3}, () =>
                TestFactory.createProduct({
                    userId: user.id,
                    masterCategoryId: mc.id,
                    regionId: region.id
                })
            )
        );

        await Promise.all(
            products.slice(0, -1).map(({id}) =>
                TestFactory.createProductAttributeValue({
                    userId: user.id,
                    productId: id,
                    attributeId: attr.id,
                    value: [id, id + 1, id - 1]
                })
            )
        );

        const res = await getProductsHandler.handle({
            context,
            data: {
                body: {
                    ...BASE_BODY,
                    filters: {
                        attributes: {
                            [attr.code]: {
                                action: 'null',
                                values: []
                            }
                        }
                    }
                }
            }
        });

        expect(res.totalCount).toBe(1);
        expect(res.list.map((it: any) => it.identifier).sort()).toEqual([products[2].identifier]);
    });

    it('should return products by number is defined (not-null)', async () => {
        const {mc} = await createBase(region, user);

        const attr = await createAttributeAndLink({type: AttributeType.NUMBER, isArray: true}, mc.infoModelId);

        const products = await Promise.all(
            Array.from({length: 3}, () =>
                TestFactory.createProduct({
                    userId: user.id,
                    masterCategoryId: mc.id,
                    regionId: region.id
                })
            )
        );

        await Promise.all(
            products.slice(0, -1).map(({id}) =>
                TestFactory.createProductAttributeValue({
                    userId: user.id,
                    productId: id,
                    attributeId: attr.id,
                    value: [id, id + 1, id - 1]
                })
            )
        );

        const res = await getProductsHandler.handle({
            context,
            data: {
                body: {
                    ...BASE_BODY,
                    filters: {
                        attributes: {
                            [attr.code]: {
                                action: 'not-null',
                                values: []
                            }
                        }
                    }
                }
            }
        });

        expect(res.totalCount).toBe(2);
        expect(res.list.map((it: any) => it.identifier).sort()).toEqual(
            products
                .slice(0, -1)
                .map((it: any) => it.identifier)
                .sort()
        );
    });

    it('should return products by image is not defined (null)', async () => {
        const {mc} = await createBase(region, user);

        const attr = await createAttributeAndLink({type: AttributeType.IMAGE}, mc.infoModelId);

        const products = await Promise.all(
            Array.from({length: 3}, () =>
                TestFactory.createProduct({
                    userId: user.id,
                    masterCategoryId: mc.id,
                    regionId: region.id
                })
            )
        );

        await Promise.all(
            products.slice(0, -1).map(({id}) =>
                TestFactory.createProductAttributeValue({
                    userId: user.id,
                    productId: id,
                    attributeId: attr.id,
                    value: 'foo.png'
                })
            )
        );

        const res = await getProductsHandler.handle({
            context,
            data: {
                body: {
                    ...BASE_BODY,
                    filters: {
                        attributes: {
                            [attr.code]: {
                                action: 'null',
                                values: []
                            }
                        }
                    }
                }
            }
        });

        expect(res.totalCount).toBe(1);
        expect(res.list.map((it: any) => it.identifier).sort()).toEqual([products[2].identifier]);
    });

    it('should return products by image is defined (not-null)', async () => {
        const {mc} = await createBase(region, user);

        const attr = await createAttributeAndLink({type: AttributeType.IMAGE}, mc.infoModelId);

        const products = await Promise.all(
            Array.from({length: 3}, () =>
                TestFactory.createProduct({
                    userId: user.id,
                    masterCategoryId: mc.id,
                    regionId: region.id
                })
            )
        );

        await Promise.all(
            products.slice(0, -1).map(({id}) =>
                TestFactory.createProductAttributeValue({
                    userId: user.id,
                    productId: id,
                    attributeId: attr.id,
                    value: 'foo.png'
                })
            )
        );

        const res = await getProductsHandler.handle({
            context,
            data: {
                body: {
                    ...BASE_BODY,
                    filters: {
                        attributes: {
                            [attr.code]: {
                                action: 'not-null',
                                values: []
                            }
                        }
                    }
                }
            }
        });

        expect(res.totalCount).toBe(2);
        expect(res.list.map((it: any) => it.identifier).sort()).toEqual(
            products
                .slice(0, -1)
                .map((it: any) => it.identifier)
                .sort()
        );
    });

    it('should return products by image array-length', async () => {
        const {mc} = await createBase(region, user);

        const attr = await createAttributeAndLink({type: AttributeType.IMAGE, isArray: true}, mc.infoModelId);

        const products = await Promise.all(
            times(5).map(() =>
                TestFactory.createProduct({
                    userId: user.id,
                    masterCategoryId: mc.id,
                    regionId: region.id
                })
            )
        );

        await Promise.all([
            TestFactory.createProductAttributeValue({
                userId: user.id,
                productId: products[0].id,
                attributeId: attr.id,
                value: ['foo.png']
            }),
            TestFactory.createProductAttributeValue({
                userId: user.id,
                productId: products[1].id,
                attributeId: attr.id,
                value: ['foo1.png', 'foo2.png']
            }),
            TestFactory.createProductAttributeValue({
                userId: user.id,
                productId: products[2].id,
                attributeId: attr.id,
                value: ['foo1.png', 'foo2.png', 'foo3.png']
            }),
            TestFactory.createProductAttributeValue({
                userId: user.id,
                productId: products[3].id,
                attributeId: attr.id,
                value: ['foo1.png', 'foo2.png', 'foo3.png', 'foo4.png']
            })
            // Один товар с пустым значением атрибута
        ]);

        const suites = [
            {
                value: [null, null],
                expectedIds: [
                    products[0].identifier,
                    products[1].identifier,
                    products[2].identifier,
                    products[3].identifier,
                    products[4].identifier
                ]
            },
            {
                value: [null, 3],
                expectedIds: [
                    products[0].identifier,
                    products[1].identifier,
                    products[2].identifier,
                    products[4].identifier
                ]
            },
            {
                value: [3, null],
                expectedIds: [products[2].identifier, products[3].identifier]
            },
            {
                value: [2, 3],
                expectedIds: [products[1].identifier, products[2].identifier]
            },
            {
                value: [0, 2],
                expectedIds: [products[0].identifier, products[1].identifier, products[4].identifier]
            },
            {
                value: [0, null],
                expectedIds: [
                    products[0].identifier,
                    products[1].identifier,
                    products[2].identifier,
                    products[3].identifier,
                    products[4].identifier
                ]
            }
        ];

        for (const suite of suites) {
            const res = await getProductsHandler.handle({
                context,
                data: {
                    body: {
                        ...BASE_BODY,
                        filters: {
                            attributes: {
                                [attr.code]: {
                                    action: 'array-length',
                                    values: suite.value
                                }
                            }
                        }
                    }
                }
            });

            expect(res.totalCount).toBe(suite.expectedIds.length);
            expect(res.list.map((it: any) => it.identifier).sort()).toEqual(suite.expectedIds.sort());
        }
    });

    it('should return products by unused boolean', async () => {
        const {mc, im} = await createBase(region, user);

        const attr = await createAttributeAndLink({type: AttributeType.BOOLEAN}, mc.infoModelId);

        const products = await Promise.all(
            Array.from({length: 3}, () =>
                TestFactory.createProduct({
                    userId: user.id,
                    masterCategoryId: mc.id,
                    regionId: region.id
                })
            )
        );

        await Promise.all(
            products.slice(0, -1).map(({id}) =>
                TestFactory.createProductAttributeValue({
                    userId: user.id,
                    productId: id,
                    attributeId: attr.id,
                    value: true
                })
            )
        );

        await TestFactory.unlinkAttributesFromInfoModel({
            userId: user.id,
            infoModelId: im.id,
            attributes: [{id: attr.id}]
        });

        const res = await getProductsHandler.handle({
            context,
            data: {
                body: {
                    ...BASE_BODY,
                    filters: {
                        attributes: {
                            [attr.code]: {
                                action: 'unused',
                                values: []
                            }
                        }
                    }
                }
            }
        });

        expect(res.totalCount).toBe(2);
        expect(res.list.map((it: any) => it.identifier).sort()).toEqual(
            products
                .slice(0, -1)
                .map((it: any) => it.identifier)
                .sort()
        );
    });

    it('should return products by unused string', async () => {
        const {mc, im} = await createBase(region, user);

        const attr = await createAttributeAndLink({type: AttributeType.STRING}, mc.infoModelId);

        const products = await Promise.all(
            Array.from({length: 3}, () =>
                TestFactory.createProduct({
                    userId: user.id,
                    masterCategoryId: mc.id,
                    regionId: region.id
                })
            )
        );

        await Promise.all(
            products.slice(0, -1).map(({id}) =>
                TestFactory.createProductAttributeValue({
                    userId: user.id,
                    productId: id,
                    attributeId: attr.id,
                    value: 'test'
                })
            )
        );

        await TestFactory.unlinkAttributesFromInfoModel({
            userId: user.id,
            infoModelId: im.id,
            attributes: [{id: attr.id}]
        });

        const res = await getProductsHandler.handle({
            context,
            data: {
                body: {
                    ...BASE_BODY,
                    filters: {
                        attributes: {
                            [attr.code]: {
                                action: 'unused',
                                values: []
                            }
                        }
                    }
                }
            }
        });

        expect(res.totalCount).toBe(2);
        expect(res.list.map((it: any) => it.identifier).sort()).toEqual(
            products
                .slice(0, -1)
                .map((it: any) => it.identifier)
                .sort()
        );
    });

    it('should return products by unused number', async () => {
        const {mc, im} = await createBase(region, user);

        const attr = await createAttributeAndLink({type: AttributeType.NUMBER}, mc.infoModelId);

        const products = await Promise.all(
            Array.from({length: 3}, () =>
                TestFactory.createProduct({
                    userId: user.id,
                    masterCategoryId: mc.id,
                    regionId: region.id
                })
            )
        );

        await Promise.all(
            products.slice(0, -1).map(({id}) =>
                TestFactory.createProductAttributeValue({
                    userId: user.id,
                    productId: id,
                    attributeId: attr.id,
                    value: 10
                })
            )
        );

        await TestFactory.unlinkAttributesFromInfoModel({
            userId: user.id,
            infoModelId: im.id,
            attributes: [{id: attr.id}]
        });

        const res = await getProductsHandler.handle({
            context,
            data: {
                body: {
                    ...BASE_BODY,
                    filters: {
                        attributes: {
                            [attr.code]: {
                                action: 'unused',
                                values: []
                            }
                        }
                    }
                }
            }
        });

        expect(res.totalCount).toBe(2);
        expect(res.list.map((it: any) => it.identifier).sort()).toEqual(
            products
                .slice(0, -1)
                .map((it: any) => it.identifier)
                .sort()
        );
    });

    it('should return products by unused select', async () => {
        const {mc, im} = await createBase(region, user);

        const attr = await createAttributeAndLink({type: AttributeType.SELECT}, mc.infoModelId);

        const products = await Promise.all(
            Array.from({length: 3}, () =>
                TestFactory.createProduct({
                    userId: user.id,
                    masterCategoryId: mc.id,
                    regionId: region.id
                })
            )
        );

        await Promise.all([
            TestFactory.createProductAttributeValue({
                userId: user.id,
                productId: products[1].id,
                attributeId: attr.id,
                value: 'bar'
            }),
            TestFactory.createProductAttributeValue({
                userId: user.id,
                productId: products[2].id,
                attributeId: attr.id,
                value: 'zxc'
            })
        ]);

        await TestFactory.unlinkAttributesFromInfoModel({
            userId: user.id,
            infoModelId: im.id,
            attributes: [{id: attr.id}]
        });

        const res = await getProductsHandler.handle({
            context,
            data: {
                body: {
                    ...BASE_BODY,
                    filters: {
                        attributes: {
                            [attr.code]: {
                                action: 'unused',
                                values: []
                            }
                        }
                    }
                }
            }
        });

        expect(res.totalCount).toBe(2);
        expect(res.list.map((it: any) => it.identifier).sort()).toEqual(
            products
                .slice(1)
                .map((it: any) => it.identifier)
                .sort()
        );
    });

    it('should return products by unused multiselect', async () => {
        const {mc, im} = await createBase(region, user);

        const attr = await createAttributeAndLink({type: AttributeType.MULTISELECT}, mc.infoModelId);

        const products = await Promise.all(
            Array.from({length: 3}, () =>
                TestFactory.createProduct({
                    userId: user.id,
                    masterCategoryId: mc.id,
                    regionId: region.id
                })
            )
        );

        await Promise.all([
            TestFactory.createProductAttributeValue({
                userId: user.id,
                productId: products[1].id,
                attributeId: attr.id,
                value: ['bar', 'foo']
            }),
            TestFactory.createProductAttributeValue({
                userId: user.id,
                productId: products[2].id,
                attributeId: attr.id,
                value: ['zxc']
            })
        ]);

        await TestFactory.unlinkAttributesFromInfoModel({
            userId: user.id,
            infoModelId: im.id,
            attributes: [{id: attr.id}]
        });

        const res = await getProductsHandler.handle({
            context,
            data: {
                body: {
                    ...BASE_BODY,
                    filters: {
                        attributes: {
                            [attr.code]: {
                                action: 'unused',
                                values: []
                            }
                        }
                    }
                }
            }
        });

        expect(res.totalCount).toBe(2);
        expect(res.list.map((it: any) => it.identifier).sort()).toEqual(
            products
                .slice(1)
                .map((it: any) => it.identifier)
                .sort()
        );
    });

    it('should not return products by attributes out of info model', async () => {
        const {mc: rootMc, im: baseIm} = await createBase(region, user);

        const anotherIm = await TestFactory.createInfoModel({
            userId: user.id,
            regionId: region.id
        });

        const mc = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            parentId: rootMc.id,
            infoModelId: baseIm.id
        });
        const anotherMc = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            parentId: rootMc.id,
            infoModelId: anotherIm.id
        });

        const attr = await createAttributeAndLink({type: AttributeType.STRING}, baseIm.id);
        const anotherAttr = await createAttributeAndLink({type: AttributeType.STRING}, baseIm.id);

        await TestFactory.linkAttributesToInfoModel({
            userId: user.id,
            infoModelId: anotherIm.id,
            attributes: [anotherAttr]
        });

        const products = await Promise.all(
            Array.from({length: 3}, (_v, i) =>
                TestFactory.createProduct({
                    userId: user.id,
                    masterCategoryId: i === 1 ? anotherMc.id : mc.id,
                    regionId: region.id
                })
            )
        );

        await Promise.all(
            products.flatMap(({id}) => [
                TestFactory.createProductAttributeValue({
                    userId: user.id,
                    productId: id,
                    attributeId: attr.id,
                    value: 'foo'
                }),
                TestFactory.createProductAttributeValue({
                    userId: user.id,
                    productId: id,
                    attributeId: anotherAttr.id,
                    value: 'bar'
                })
            ])
        );

        const res = await getProductsHandler.handle({
            context,
            data: {
                body: {
                    ...BASE_BODY,
                    filters: {
                        attributes: {
                            [attr.code]: {
                                action: 'contain',
                                values: ['foo']
                            },
                            [anotherAttr.code]: {
                                action: 'contain',
                                values: ['bar']
                            }
                        }
                    }
                }
            }
        });

        expect(res.totalCount).toEqual(2);
        expect(res.list).toEqual(
            expect.arrayContaining([
                expect.objectContaining({identifier: products[0].identifier}),
                expect.objectContaining({identifier: products[2].identifier})
            ])
        );
    });

    it('should return products by any type important and without value', async () => {
        // 1. товар с important атрибутом и значением
        // 2. товар с important атрибутом и без значения
        // 3. товар с not-important атрибутом и значением
        // 4. товар с not-important атрибутом и без значения
        // фильтр -> Должен вернуть 2

        const {mc: mc1, im: im1} = await createBase(region, user);
        const {mc: mc2, im: im2} = await createBase(region, user, mc1.id);

        const attributes = await Promise.all([
            TestFactory.createAttribute({
                userId: user.id,
                attribute: {
                    type: AttributeType.BOOLEAN
                }
            }),
            TestFactory.createAttribute({
                userId: user.id,
                attribute: {
                    type: AttributeType.STRING
                }
            }),
            TestFactory.createAttribute({
                userId: user.id,
                attribute: {
                    type: AttributeType.TEXT
                }
            }),
            TestFactory.createAttribute({
                userId: user.id,
                attribute: {
                    type: AttributeType.NUMBER
                }
            }),
            TestFactory.createAttribute({
                userId: user.id,
                attribute: {
                    type: AttributeType.SELECT
                }
            }),
            TestFactory.createAttribute({
                userId: user.id,
                attribute: {
                    type: AttributeType.MULTISELECT
                }
            })
        ]);

        // Другой атрибут для шума, чтобы проверить left join && is null
        const otherAttribute = await TestFactory.createAttribute({
            userId: user.id,
            attribute: {
                type: AttributeType.BOOLEAN
            }
        });

        await linkImportantAttribute(user, im1.id, otherAttribute.id);
        await linkNotImportantAttribute(user, im2.id, otherAttribute.id);

        // Добавляем в инфо модели все типы атрибутов
        for (const attr of attributes) {
            await linkImportantAttribute(user, im1.id, attr.id);
            await linkNotImportantAttribute(user, im2.id, attr.id);
        }

        const products = await Promise.all([
            ...times(2).map(() =>
                TestFactory.createProduct({
                    userId: user.id,
                    masterCategoryId: mc1.id,
                    regionId: region.id
                })
            ),
            ...times(2).map(() =>
                TestFactory.createProduct({
                    userId: user.id,
                    masterCategoryId: mc2.id,
                    regionId: region.id
                })
            )
        ]);

        // Все тот же атрибут для шума
        for (const product of products) {
            await TestFactory.createProductAttributeValue({
                userId: user.id,
                productId: product.id,
                attributeId: otherAttribute.id,
                value: 'value'
            });
        }

        for (const attr of attributes) {
            await Promise.all([
                TestFactory.createProductAttributeValue({
                    userId: user.id,
                    productId: products[0].id,
                    attributeId: attr.id,
                    value: 'value'
                }),
                TestFactory.createProductAttributeValue({
                    userId: user.id,
                    productId: products[2].id,
                    attributeId: attr.id,
                    value: 'value'
                })
            ]);
        }

        for (const attr of attributes) {
            const res = await getProductsHandler.handle({
                context,
                data: {
                    body: {
                        ...BASE_BODY,
                        filters: {
                            attributes: {
                                [attr.code]: {
                                    action: 'important-and-null',
                                    values: []
                                }
                            }
                        }
                    }
                }
            });

            expect(res.totalCount).toBe(1);
            expect(res.list.map((it: any) => it.identifier)).toEqual([products[1].identifier]);
        }
    });
});
