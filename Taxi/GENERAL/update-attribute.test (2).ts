/* eslint-disable @typescript-eslint/no-non-null-assertion */
import {random, range} from 'lodash';
import {beforeEach, describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';

import type {Lang} from '@/src/entities/lang/entity';
import type {User} from '@/src/entities/user/entity';
import {AccessForbidden, EntityNotFoundError, ForbidClientAttributeOnSystem} from '@/src/errors';
import type {ApiRequestContext} from 'server/routes/api/api-handler';
import {AttributeType, UpdatedAttribute} from 'types/attribute';

import {updateAttributeHandler} from './update-attribute';

describe('update attribute', () => {
    let user: User;
    let langs: Lang[];
    let langCodes: string[];
    let context: ApiRequestContext;

    beforeEach(async () => {
        user = await TestFactory.createUser({rules: {attribute: {canEdit: true}}});
        langs = await Promise.all([TestFactory.createLang(), TestFactory.createLang()]);
        langCodes = langs.map(({isoCode}) => isoCode);
        context = await TestFactory.createApiContext({lang: langs[0], user});
    });

    it('should add new attribute and options translations', async () => {
        const existingAttribute = await TestFactory.createAttribute({
            userId: user.id,
            attribute: {
                type: AttributeType.SELECT,
                isArray: false,
                isValueLocalizable: false
            }
        });

        const existingAttributeOptions = await Promise.all(
            range(3).map((i) =>
                TestFactory.createAttributeOption({
                    userId: user.id,
                    attributeOption: {
                        attributeId: existingAttribute.id,
                        sortOrder: i
                    }
                })
            )
        );

        const updatedAttributeData: UpdatedAttribute = {
            nameTranslations: {
                [langCodes[0]]: 'некий атрибут',
                [langCodes[1]]: 'some attribute'
            },
            descriptionTranslations: {
                [langCodes[0]]: 'некое описание атрибута',
                [langCodes[1]]: 'some attribute description'
            },
            properties: {
                options: existingAttributeOptions.map(({code}, i) => ({
                    code,
                    translations: {
                        [langCodes[0]]: `опция атрибута ${i}`,
                        [langCodes[1]]: `first attribute option ${i}`
                    }
                }))
            }
        };

        await updateAttributeHandler.handle({
            context,
            data: {
                params: {
                    id: existingAttribute.id
                },
                body: updatedAttributeData
            }
        });

        const foundAttribute = (await TestFactory.getAttributes())[0];

        expect(foundAttribute.nameTranslationMap).toEqual(updatedAttributeData.nameTranslations);
        expect(foundAttribute.descriptionTranslationMap).toEqual(updatedAttributeData.descriptionTranslations);

        const foundOptions = await TestFactory.getAttributeOptions(existingAttribute.id);

        expect(foundOptions.map(({nameTranslationMap}) => nameTranslationMap)).toEqual(
            updatedAttributeData.properties?.options.map(({translations}) => translations)
        );
    });

    it('should update attribute and options translations', async () => {
        const existingAttribute = await TestFactory.createAttribute({
            userId: user.id,
            attribute: {
                type: AttributeType.SELECT,
                isArray: false,
                isValueLocalizable: false,
                nameTranslationMap: TestFactory.createTranslationMap({langCodes}),
                descriptionTranslationMap: TestFactory.createTranslationMap({langCodes})
            }
        });

        const existingAttributeOptions = await Promise.all(
            range(3).map((i) =>
                TestFactory.createAttributeOption({
                    userId: user.id,
                    attributeOption: {
                        attributeId: existingAttribute.id,
                        sortOrder: i,
                        nameTranslationMap: TestFactory.createTranslationMap({langCodes})
                    }
                })
            )
        );

        const updatedAttributeData: UpdatedAttribute = {
            nameTranslations: {
                [langCodes[0]]: 'некий атрибут',
                [langCodes[1]]: 'some attribute'
            },
            descriptionTranslations: {
                [langCodes[0]]: 'некое описание атрибута',
                [langCodes[1]]: 'some attribute description'
            },
            properties: {
                options: existingAttributeOptions.map(({code}, i) => ({
                    code,
                    translations: {
                        [langCodes[0]]: `опция атрибута ${i}`,
                        [langCodes[1]]: `first attribute option ${i}`
                    }
                }))
            }
        };

        await updateAttributeHandler.handle({
            context,
            data: {
                params: {
                    id: existingAttribute.id
                },
                body: updatedAttributeData
            }
        });

        const foundAttribute = (await TestFactory.getAttributes())[0];

        expect(foundAttribute.nameTranslationMap).toEqual(updatedAttributeData.nameTranslations);
        expect(foundAttribute.descriptionTranslationMap).toEqual(updatedAttributeData.descriptionTranslations);

        const foundOptions = await TestFactory.getAttributeOptions(existingAttribute.id);

        expect(foundOptions.map(({nameTranslationMap}) => nameTranslationMap)).toEqual(
            updatedAttributeData.properties?.options.map(({translations}) => translations)
        );
    });

    it('should update only "isClient" param', async () => {
        const existingAttribute = await TestFactory.createAttribute({
            userId: user.id,
            attribute: {
                type: AttributeType.SELECT,
                isArray: false,
                isValueLocalizable: false,
                nameTranslationMap: TestFactory.createTranslationMap({langCodes}),
                descriptionTranslationMap: TestFactory.createTranslationMap({langCodes})
            }
        });

        expect(existingAttribute.isClient).toBe(false);

        const updatedAttributeData: UpdatedAttribute = {
            isClient: true
        };

        await updateAttributeHandler.handle({
            context,
            data: {
                params: {
                    id: existingAttribute.id
                },
                body: updatedAttributeData
            }
        });

        const foundAttribute = (await TestFactory.getAttributes())[0];

        expect(foundAttribute.nameTranslationMap).toEqual(existingAttribute.nameTranslationMap);
        expect(foundAttribute.descriptionTranslationMap).toEqual(existingAttribute.descriptionTranslationMap);
        expect(foundAttribute.isClient).toEqual(true);
    });

    it('should update attribute and options translations partially', async () => {
        const existingAttribute = await TestFactory.createAttribute({
            userId: user.id,
            attribute: {
                type: AttributeType.SELECT,
                isArray: false,
                isValueLocalizable: false,
                nameTranslationMap: TestFactory.createTranslationMap({langCodes}),
                descriptionTranslationMap: TestFactory.createTranslationMap({langCodes})
            }
        });

        const existingAttributeOptions = await Promise.all(
            range(3).map((i) =>
                TestFactory.createAttributeOption({
                    userId: user.id,
                    attributeOption: {
                        attributeId: existingAttribute.id,
                        sortOrder: i,
                        nameTranslationMap: TestFactory.createTranslationMap({langCodes})
                    }
                })
            )
        );

        const updatedAttributeData: UpdatedAttribute = {
            nameTranslations: {
                [langCodes[0]]: 'некий атрибут'
            },
            descriptionTranslations: {
                [langCodes[0]]: 'некое описание атрибута'
            },
            properties: {
                options: existingAttributeOptions.map(({code}, i) => ({
                    code,
                    translations: {
                        [langCodes[0]]: `опция атрибута ${i}`
                    }
                }))
            }
        };

        await updateAttributeHandler.handle({
            context,
            data: {
                params: {
                    id: existingAttribute.id
                },
                body: updatedAttributeData
            }
        });

        const foundAttribute = (await TestFactory.getAttributes())[0];

        expect(foundAttribute.nameTranslationMap).toEqual({
            ...existingAttribute.nameTranslationMap,
            ...updatedAttributeData.nameTranslations
        });

        expect(foundAttribute.descriptionTranslationMap).toEqual({
            ...existingAttribute.descriptionTranslationMap,
            ...updatedAttributeData.descriptionTranslations
        });

        const foundOptions = await TestFactory.getAttributeOptions(existingAttribute.id);

        expect(foundOptions.map(({nameTranslationMap}) => nameTranslationMap)).toEqual(
            updatedAttributeData.properties?.options.map(({translations}, i) => ({
                ...existingAttributeOptions[i].nameTranslationMap,
                ...translations
            }))
        );
    });

    it('should update attribute options order', async () => {
        const existingAttribute = await TestFactory.createAttribute({
            userId: user.id,
            attribute: {
                type: AttributeType.SELECT,
                isArray: false,
                isValueLocalizable: false
            }
        });

        await Promise.all(
            range(3).map((i) =>
                TestFactory.createAttributeOption({
                    userId: user.id,
                    attributeOption: {
                        attributeId: existingAttribute.id,
                        code: `attribute_option_${i}`,
                        sortOrder: i
                    }
                })
            )
        );

        let existingAttributeOptions = await TestFactory.getAttributeOptions(existingAttribute.id);

        expect(existingAttributeOptions.map(({code}) => code)).toEqual([
            'attribute_option_0',
            'attribute_option_1',
            'attribute_option_2'
        ]);

        const updatedAttributeData: UpdatedAttribute = {
            nameTranslations: {},
            descriptionTranslations: {},
            properties: {
                options: [
                    {
                        code: 'attribute_option_2',
                        translations: {}
                    },
                    {
                        code: 'attribute_option_1',
                        translations: {}
                    },
                    {
                        code: 'attribute_option_0',
                        translations: {}
                    }
                ]
            }
        };

        await updateAttributeHandler.handle({
            context,
            data: {
                params: {
                    id: existingAttribute.id
                },
                body: updatedAttributeData
            }
        });

        existingAttributeOptions = await TestFactory.getAttributeOptions(existingAttribute.id);

        expect(existingAttributeOptions.map(({code}) => code)).toEqual([
            'attribute_option_2',
            'attribute_option_1',
            'attribute_option_0'
        ]);
    });

    it('should throw error if attribute does not exist', async () => {
        let error = null;
        const unknownId = random(999999);
        const updatedAttributeData: UpdatedAttribute = {};

        try {
            await updateAttributeHandler.handle({
                context,
                data: {
                    params: {
                        id: unknownId
                    },
                    body: updatedAttributeData
                }
            });
        } catch (err) {
            error = err;
        }

        expect(error).toBeInstanceOf(EntityNotFoundError);
        expect(error.parameters).toMatchObject({entity: 'Attribute'});
    });

    it('should throw error if "isClient" setting on system attribute', async () => {
        let error = null;
        const existingAttribute = await TestFactory.createAttribute({
            userId: user.id,
            attribute: {
                type: AttributeType.SELECT,
                isArray: false,
                isValueLocalizable: false,
                isValueRequired: true
            }
        });
        const updatedAttributeData: UpdatedAttribute = {
            isClient: true
        };

        try {
            await updateAttributeHandler.handle({
                context,
                data: {
                    params: {
                        id: existingAttribute.id
                    },
                    body: updatedAttributeData
                }
            });
        } catch (err) {
            error = err;
        }

        expect(error).toBeInstanceOf(ForbidClientAttributeOnSystem);
    });

    it('should update products revision if "isClient" changed', async () => {
        const attribute = await TestFactory.createAttribute({
            userId: user.id,
            attribute: {
                type: AttributeType.TEXT,
                isArray: false,
                isValueLocalizable: false,
                isClient: false
            }
        });

        expect(attribute.isClient).toBe(false);

        const region = await TestFactory.createRegion();

        const {id: infoModelId} = await TestFactory.createInfoModel({
            userId: user.id,
            regionId: region.id
        });

        const mc = await TestFactory.createMasterCategory({
            userId: user.id,
            infoModelId,
            regionId: region.id
        });

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

        await TestFactory.createProductAttributeValue({
            productId: products[0].id,
            attributeId: attribute.id,
            userId: user.id,
            value: 'foo'
        });

        await TestFactory.createProductAttributeValue({
            productId: products[1].id,
            attributeId: attribute.id,
            userId: user.id,
            value: 'bar'
        });

        const updatedAttributeData: UpdatedAttribute = {
            isClient: true
        };

        const productsBefore = await TestFactory.getProducts();

        await updateAttributeHandler.handle({
            context,
            data: {
                params: {
                    id: attribute.id
                },
                body: updatedAttributeData
            }
        });

        const productsAfter = await TestFactory.getProducts();

        products.forEach((product, i) => {
            const productBefore = productsBefore.find((it) => it.id === product.id)!;
            const productAfter = productsAfter.find((it) => it.id === product.id)!;

            if (i === 2) {
                expect(productBefore.historySubject.revision).toBe(productAfter.historySubject.revision);
            } else {
                expect(productBefore.historySubject.revision).toBeLessThan(productAfter.historySubject.revision);
            }
        });
    });

    it('should throw when user has not permission', async () => {
        const user = await TestFactory.createUser();
        const context = await TestFactory.createApiContext({lang: langs[0], user});
        const existingAttribute = await TestFactory.createAttribute({
            userId: user.id,
            attribute: {
                type: AttributeType.SELECT,
                isArray: false,
                isValueLocalizable: false,
                isValueRequired: true
            }
        });
        const updatedAttributeData: UpdatedAttribute = {
            isClient: true
        };

        await expect(
            updateAttributeHandler.handle({
                context,
                data: {params: {id: existingAttribute.id}, body: updatedAttributeData}
            })
        ).rejects.toThrow(AccessForbidden);
    });
});
