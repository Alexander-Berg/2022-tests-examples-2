import {beforeEach, describe, expect, it} from 'tests/jest.globals';
import {attributesFactory, infoModelsFactory, TestFactory} from 'tests/unit/test-factory';

import {IDENTIFIER_HEADER, MASTER_CATEGORY_HEADER} from '@/src/constants/import';
import type {Attribute} from '@/src/entities/attribute/entity';
import type {InfoModel} from '@/src/entities/info-model/entity';
import type {Lang} from '@/src/entities/lang/entity';
import type {MasterCategory} from '@/src/entities/master-category/entity';
import type {Region} from '@/src/entities/region/entity';
import type {User} from '@/src/entities/user/entity';
import type {ApiRequestContext} from '@/src/server/routes/api/api-handler';
import {AttributeType} from '@/src/types/attribute';
import {createProductHandler} from 'server/routes/api/v1/products/create-product';
import {updateProductHandler} from 'server/routes/api/v1/products/update-product';
import {env} from 'service/cfg';
import {CommitHandler} from 'service/import/commit-handler';
import TankerProvider from 'service/tanker-provider';
import {Product, ProductStatus} from 'types/product';

import {processTaskQueue} from '..';

const mockUpsertKeysetWithRetry = jest.fn();
jest.mock('service/tanker-provider', () => {
    return jest.fn().mockImplementation(() => {
        return {upsertKeysetWithRetry: mockUpsertKeysetWithRetry};
    });
});

describe('tanker export', () => {
    let region: Region;
    let user: User;
    let context: ApiRequestContext;
    let langs: Lang[];

    let attributes: Attribute[];
    let infoModels: InfoModel[];
    let mc0: MasterCategory;
    let product: Product;

    beforeEach(async () => {
        langs = await Promise.all([TestFactory.createLang({isoCode: 'ru'}), TestFactory.createLang({isoCode: 'en'})]);
        user = await TestFactory.createUser({rules: {product: {canEdit: true}}});
        region = await TestFactory.createRegion();
        await TestFactory.createLocale({regionId: region.id, langIds: langs.map(({id}) => id)});
        context = await TestFactory.createApiContext({lang: langs[0], user, region});

        attributes = await attributesFactory(user, [
            {type: AttributeType.STRING},
            {type: AttributeType.STRING, isValueLocalizable: true}
        ]);
        infoModels = await infoModelsFactory(user, region, [
            [
                {id: attributes[0].id, isImportant: false},
                {id: attributes[1].id, isImportant: false}
            ]
        ]);

        const mcRoot = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            infoModelId: infoModels[0].id
        });
        mc0 = await TestFactory.createMasterCategory({
            userId: user.id,
            regionId: region.id,
            parentId: mcRoot.id,
            infoModelId: infoModels[0].id
        });

        product = await createProductHandler.handle({
            context,
            data: {
                body: {
                    status: ProductStatus.ACTIVE,
                    masterCategoryId: mc0.id,
                    frontCategoryIds: [],
                    attributes: [
                        {
                            attributeId: attributes[0].id,
                            value: 'abcOLD'
                        },
                        {
                            attributeId: attributes[1].id,
                            value: {
                                [langs[0].isoCode]: 'fooOLD',
                                [langs[1].isoCode]: 'barOLD'
                            }
                        }
                    ]
                }
            }
        });

        await processTaskQueue();

        (TankerProvider as jest.Mock).mockClear();
        mockUpsertKeysetWithRetry.mockClear();
    });

    it('create product should push localizable attribute into tanker', async () => {
        const product = await createProductHandler.handle({
            context,
            data: {
                body: {
                    status: ProductStatus.ACTIVE,
                    masterCategoryId: mc0.id,
                    frontCategoryIds: [],
                    attributes: [
                        {
                            attributeId: attributes[0].id,
                            value: 'abc'
                        },
                        {
                            attributeId: attributes[1].id,
                            value: {
                                [langs[0].isoCode]: 'foo',
                                [langs[1].isoCode]: 'bar'
                            }
                        }
                    ]
                }
            }
        });

        await processTaskQueue();

        expect(mockUpsertKeysetWithRetry.mock.calls[0][0]).toEqual({
            keyset: `product:${attributes[1].code}:${env}`,
            keys: [
                {
                    name: '' + product.identifier,
                    translations: {
                        ru: 'foo',
                        en: 'bar'
                    }
                }
            ]
        });
    });

    it('update product should push localizable attribute into tanker', async () => {
        const updatedProduct = await updateProductHandler.handle({
            context,
            data: {
                params: {
                    identifier: product.identifier
                },
                body: {
                    status: ProductStatus.ACTIVE,
                    masterCategoryId: mc0.id,
                    frontCategoryIds: [],
                    attributes: [
                        {
                            attributeId: attributes[0].id,
                            value: 'abcNEW'
                        },
                        {
                            attributeId: attributes[1].id,
                            value: {
                                [langs[0].isoCode]: 'fooNEW',
                                [langs[1].isoCode]: 'barNEW'
                            }
                        }
                    ]
                }
            }
        });

        await processTaskQueue();

        expect(mockUpsertKeysetWithRetry.mock.calls[0][0]).toEqual({
            keyset: `product:${attributes[1].code}:${env}`,
            keys: [
                {
                    name: '' + updatedProduct.identifier,
                    translations: {
                        ru: 'fooNEW',
                        en: 'barNEW'
                    }
                }
            ]
        });
    });

    it('create product via import should push localizable attribute into tanker', async () => {
        const content = [
            [MASTER_CATEGORY_HEADER, attributes[0].code, `${attributes[1].code}|ru`, `${attributes[1].code}|en`],
            ['' + mc0.code, 'abc', 'foo', 'bar']
        ];
        const {importKey} = await TestFactory.createImportSpreadsheet({regionId: region.id, content});
        const commitHandler = new CommitHandler({importKey, authorId: user.id});
        expect(await commitHandler.handle()).toBeUndefined();
        const newProductIdentifiers = commitHandler.getNewProductIdentifiers();
        expect(newProductIdentifiers).toHaveLength(1);
        const newProductIds = commitHandler.getNewProductIds();
        expect(newProductIds).toHaveLength(1);

        // на первой итерации считается полнота и в ней создается новая задача на экспорт в танкер
        // поэтому необходим два раза обработать очередь
        await processTaskQueue();
        await processTaskQueue();

        expect(mockUpsertKeysetWithRetry.mock.calls[0][0]).toEqual({
            keyset: `product:${attributes[1].code}:${env}`,
            keys: [
                {
                    name: '' + newProductIdentifiers[0],
                    translations: {
                        ru: 'foo',
                        en: 'bar'
                    }
                }
            ]
        });
    });

    it('update product via import should push localizable attribute into tanker', async () => {
        const content = [
            [IDENTIFIER_HEADER, attributes[0].code, `${attributes[1].code}|ru`, `${attributes[1].code}|en`],
            ['' + product.identifier, 'abcNEW', 'fooNEW', 'barNEW']
        ];
        const {importKey} = await TestFactory.createImportSpreadsheet({regionId: region.id, content});
        const commitHandler = new CommitHandler({importKey, authorId: user.id});
        expect(await commitHandler.handle()).toBeUndefined();
        const newProductIdentifiers = commitHandler.getUpdatedProductIdentifiers();
        expect(newProductIdentifiers).toHaveLength(1);

        await processTaskQueue();
        await processTaskQueue();

        expect(mockUpsertKeysetWithRetry.mock.calls[0][0]).toEqual({
            keyset: `product:${attributes[1].code}:${env}`,
            keys: [
                {
                    name: '' + newProductIdentifiers[0],
                    translations: {
                        ru: 'fooNEW',
                        en: 'barNEW'
                    }
                }
            ]
        });
    });
});
