/* eslint-disable @typescript-eslint/no-non-null-assertion */
import {beforeEach, describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';

import type {Lang} from '@/src/entities/lang/entity';
import type {Region} from '@/src/entities/region/entity';
import type {User} from '@/src/entities/user/entity';
import {ActivateCategoryWithoutImagesIsForbidden, EntityNotFoundError} from '@/src/errors';
import type {ApiRequestContext} from 'server/routes/api/api-handler';
import {CatalogStatus} from 'types/catalog/base';
import type {UpdatedCategory} from 'types/catalog/category';

import {updateCategoryHandler} from './update-category';

describe('update category', () => {
    let user: User;
    let regions: Region[];
    let langs: Lang[];
    let langCodes: string[];
    let context: ApiRequestContext;

    beforeEach(async () => {
        user = await TestFactory.createUser({rules: {catalog: {canEdit: true}}});
        regions = await Promise.all([TestFactory.createRegion(), TestFactory.createRegion()]);
        langs = await Promise.all([TestFactory.createLang(), TestFactory.createLang()]);
        langCodes = langs.map(({isoCode}) => isoCode);
        context = await TestFactory.createApiContext({user, region: regions[0], lang: langs[0]});
    });

    it('should update category itself', async () => {
        const category = await TestFactory.createCategory({
            userId: user.id,
            regionId: regions[0].id,
            status: CatalogStatus.DISABLED,
            shortTitleTranslationMap: {
                [langCodes[0]]: 'категория'
            },
            longTitleTranslationMap: {
                [langCodes[0]]: 'категор',
                [langCodes[1]]: 'categor'
            },
            images: [{imageUrl: 'http://avatars/111', filename: '111.png', width: 2, height: 2}]
        });

        const updateParams: UpdatedCategory = {
            status: CatalogStatus.ACTIVE,
            shortTitleTranslations: {
                [langCodes[1]]: 'category'
            },
            longTitleTranslations: {
                [langCodes[0]]: 'категория',
                [langCodes[1]]: 'category'
            },
            meta: {foo: 'bar'},
            description: 'description',
            specialCategory: 'special',
            deeplink: 'deeplink',
            groups: []
        };

        await updateCategoryHandler.handle({context, data: {params: {id: category.id}, body: updateParams}});
        const updatedCategory = (await TestFactory.getCategories()).find(({id}) => id === category.id)!;

        expect(updatedCategory).toEqual({
            ...category,
            status: updateParams.status,
            shortTitleTranslationMap: updateParams.shortTitleTranslations,
            longTitleTranslationMap: updateParams.longTitleTranslations,
            meta: updateParams.meta,
            description: updateParams.description,
            specialCategory: updateParams.specialCategory,
            deeplink: updateParams.deeplink
        });
    });

    it('should update images', async () => {
        const category = await TestFactory.createCategory({
            userId: user.id,
            regionId: regions[0].id,
            images: [
                {imageUrl: 'http://avatars/111', filename: '111.png', width: 2, height: 2},
                {imageUrl: 'http://avatars/111', filename: '111.png', width: 4, height: 2},
                {imageUrl: 'http://avatars/222', filename: '222.png', width: 2, height: 2}
            ]
        });

        const updateParams: UpdatedCategory = {
            images: [
                {imageUrl: 'http://avatars/333', filename: '333.png', formats: [2]},
                {imageUrl: 'http://avatars/111', filename: '111_old.png', formats: [3, 4]}
            ],
            groups: []
        };

        const categoryImages = await TestFactory.getCategoryImages(category.id);

        expect(categoryImages).toHaveLength(3);
        expect(categoryImages).toEqual(
            expect.arrayContaining([
                expect.objectContaining({
                    imageUrl: 'http://avatars/111',
                    filename: '111.png',
                    imageDimension: expect.objectContaining({width: 2, height: 2})
                }),
                expect.objectContaining({
                    imageUrl: 'http://avatars/111',
                    filename: '111.png',
                    imageDimension: expect.objectContaining({width: 4, height: 2})
                }),
                expect.objectContaining({
                    imageUrl: 'http://avatars/222',
                    filename: '222.png',
                    imageDimension: expect.objectContaining({width: 2, height: 2})
                })
            ])
        );

        await updateCategoryHandler.handle({context, data: {params: {id: category.id}, body: updateParams}});
        const updatedCategoryImages = await TestFactory.getCategoryImages(category.id);

        expect(updatedCategoryImages).toHaveLength(3);
        expect(updatedCategoryImages).toEqual(
            expect.arrayContaining([
                expect.objectContaining({
                    imageUrl: 'http://avatars/111',
                    filename: '111_old.png',
                    imageDimension: expect.objectContaining({width: 3, height: 2})
                }),
                expect.objectContaining({
                    imageUrl: 'http://avatars/111',
                    filename: '111_old.png',
                    imageDimension: expect.objectContaining({width: 4, height: 2})
                }),
                expect.objectContaining({
                    imageUrl: 'http://avatars/333',
                    filename: '333.png',
                    imageDimension: expect.objectContaining({width: 2, height: 2})
                })
            ])
        );
    });

    it('should throw error if linked category image is removing', async () => {
        const group = await TestFactory.createGroup({
            userId: user.id,
            regionId: regions[0].id
        });

        const category = await TestFactory.createCategory({
            userId: user.id,
            regionId: regions[0].id,
            images: [{imageUrl: 'http://avatars/111', filename: '111.png', width: 2, height: 2}]
        });

        await TestFactory.linkCategoryToGroup({
            userId: user.id,
            groupId: group.id,
            categoryId: category.id,
            images: [{imageUrl: 'http://avatars/111', width: 2, height: 2}]
        });

        const updateParams: UpdatedCategory = {images: [], groups: [{id: group.id}]};

        await expect(
            updateCategoryHandler.handle({context, data: {params: {id: category.id}, body: updateParams}})
        ).rejects.toThrow(/fk__group_category_image__category_image_id__category_image/);
    });

    it('should update linked front categories', async () => {
        const category = await TestFactory.createCategory({
            userId: user.id,
            regionId: regions[0].id
        });

        const rootFrontCategory = await TestFactory.createFrontCategory({
            userId: user.id,
            regionId: regions[0].id
        });

        const parentFrontCategory = await TestFactory.createFrontCategory({
            userId: user.id,
            regionId: regions[0].id,
            parentId: rootFrontCategory.id
        });

        const frontCategories = await Promise.all([
            TestFactory.createFrontCategory({
                userId: user.id,
                regionId: regions[0].id,
                parentId: parentFrontCategory.id
            }),
            TestFactory.createFrontCategory({
                userId: user.id,
                regionId: regions[0].id,
                parentId: parentFrontCategory.id
            }),
            TestFactory.createFrontCategory({
                userId: user.id,
                regionId: regions[0].id,
                parentId: parentFrontCategory.id
            }),
            TestFactory.createFrontCategory({
                userId: user.id,
                regionId: regions[0].id,
                parentId: parentFrontCategory.id
            })
        ]);

        await TestFactory.linkFrontCategoryToCategory({
            userId: user.id,
            categoryId: category.id,
            frontCategoryId: frontCategories[0].id
        });

        await TestFactory.linkFrontCategoryToCategory({
            userId: user.id,
            categoryId: category.id,
            frontCategoryId: frontCategories[1].id
        });

        await TestFactory.linkFrontCategoryToCategory({
            userId: user.id,
            categoryId: category.id,
            frontCategoryId: frontCategories[2].id
        });

        const updateParams: UpdatedCategory = {
            frontCategories: [{id: frontCategories[1].id}, {id: frontCategories[3].id}, {id: frontCategories[2].id}],
            groups: []
        };

        await updateCategoryHandler.handle({context, data: {params: {id: category.id}, body: updateParams}});
        const categoryFrontCategories = await TestFactory.getCategoryFrontCategories(category.id);

        expect(categoryFrontCategories).toEqual([
            expect.objectContaining({frontCategoryId: frontCategories[1].id}),
            expect.objectContaining({frontCategoryId: frontCategories[3].id}),
            expect.objectContaining({frontCategoryId: frontCategories[2].id})
        ]);
    });

    it('should not link front category from another region', async () => {
        const category = await TestFactory.createCategory({
            userId: user.id,
            regionId: regions[0].id
        });

        const rootFrontCategory = await TestFactory.createFrontCategory({
            userId: user.id,
            regionId: regions[1].id
        });

        const parentFrontCategory = await TestFactory.createFrontCategory({
            userId: user.id,
            regionId: regions[1].id,
            parentId: rootFrontCategory.id
        });

        const frontCategory = await TestFactory.createFrontCategory({
            userId: user.id,
            regionId: regions[1].id,
            parentId: parentFrontCategory.id
        });

        const updateParams: UpdatedCategory = {
            groups: [],
            frontCategories: [{id: frontCategory.id}]
        };

        await expect(
            updateCategoryHandler.handle({context, data: {params: {id: category.id}, body: updateParams}})
        ).rejects.toThrow('FALSY check_category_front_category_region');
    });

    it('should update category when all groups selected', async () => {
        const groups = await Promise.all([
            TestFactory.createGroup({
                userId: user.id,
                regionId: regions[0].id
            }),
            TestFactory.createGroup({
                userId: user.id,
                regionId: regions[0].id
            })
        ]);

        const category = await TestFactory.createCategory({
            userId: user.id,
            regionId: regions[0].id
        });

        await TestFactory.linkCategoryToGroup({
            userId: user.id,
            groupId: groups[0].id,
            categoryId: category.id
        });

        await TestFactory.linkCategoryToGroup({
            userId: user.id,
            groupId: groups[1].id,
            categoryId: category.id
        });

        const updateParams: UpdatedCategory = {meta: {foo: 'bar'}, groups: groups.map(({id}) => ({id}))};

        await updateCategoryHandler.handle({context, data: {params: {id: category.id}, body: updateParams}});
        const updatedCategory = (await TestFactory.getCategories()).find(({id}) => id === category.id)!;

        expect(updatedCategory).toEqual({...category, meta: updateParams.meta});
    });

    it('should duplicate category with images and links when part of groups selected', async () => {
        const groups = await Promise.all([
            TestFactory.createGroup({
                userId: user.id,
                regionId: regions[0].id
            }),
            TestFactory.createGroup({
                userId: user.id,
                regionId: regions[0].id
            })
        ]);

        const category = await TestFactory.createCategory({
            userId: user.id,
            regionId: regions[0].id,
            status: CatalogStatus.DISABLED,
            meta: {foo: 'bar'},
            shortTitleTranslationMap: {
                [langCodes[0]]: 'категория'
            },
            longTitleTranslationMap: {
                [langCodes[1]]: 'category'
            },
            description: 'description',
            images: [
                {imageUrl: 'http://avatars/111', filename: '111.png', width: 2, height: 2},
                {imageUrl: 'http://avatars/222', filename: '222.png', width: 2, height: 2},
                {imageUrl: 'http://avatars/333', filename: '333.png', width: 2, height: 2}
            ],
            specialCategory: 'special',
            deeplink: 'deeplink'
        });

        const rootFrontCategory = await TestFactory.createFrontCategory({
            userId: user.id,
            regionId: regions[0].id
        });

        const parentFrontCategory = await TestFactory.createFrontCategory({
            userId: user.id,
            regionId: regions[0].id,
            parentId: rootFrontCategory.id
        });

        const frontCategories = await Promise.all([
            TestFactory.createFrontCategory({
                userId: user.id,
                regionId: regions[0].id,
                parentId: parentFrontCategory.id
            }),
            TestFactory.createFrontCategory({
                userId: user.id,
                regionId: regions[0].id,
                parentId: parentFrontCategory.id
            })
        ]);

        await TestFactory.linkCategoryToGroup({
            userId: user.id,
            groupId: groups[0].id,
            categoryId: category.id,
            meta: {foo: 'group link meta 0'},
            images: [{imageUrl: 'http://avatars/111', width: 2, height: 2}]
        });

        await TestFactory.linkCategoryToGroup({
            userId: user.id,
            groupId: groups[1].id,
            categoryId: category.id,
            meta: {foo: 'group link meta 1'},
            images: [{imageUrl: 'http://avatars/222', width: 2, height: 2}]
        });

        await TestFactory.linkFrontCategoryToCategory({
            userId: user.id,
            categoryId: category.id,
            frontCategoryId: frontCategories[0].id
        });

        await TestFactory.linkFrontCategoryToCategory({
            userId: user.id,
            categoryId: category.id,
            frontCategoryId: frontCategories[1].id
        });

        const updateParams: UpdatedCategory = {
            code: category.code + '_duplicated',
            status: CatalogStatus.ACTIVE,
            meta: {foo: 'bar100500'},
            shortTitleTranslations: {
                [langCodes[1]]: 'group'
            },
            longTitleTranslations: {
                [langCodes[0]]: 'прилавок'
            },
            description: 'description',
            images: [
                {imageUrl: 'http://avatars/111', filename: '111.png', formats: [2]},
                {imageUrl: 'http://avatars/222', filename: '222.png', formats: [2]}
            ],
            specialCategory: 'special',
            deeplink: 'deeplink',
            frontCategories: [{id: frontCategories[0].id}, {id: frontCategories[1].id}],
            groups: [{id: groups[1].id}]
        };

        const newCategory = await updateCategoryHandler.handle({
            context,
            data: {params: {id: category.id}, body: updateParams}
        });

        const untouchedCategory = (await TestFactory.getCategories()).find(({id}) => id === category.id)!;
        const untouchedCategoryImages = await TestFactory.getCategoryImages(category.id);
        const untouchedCategoryFrontCategories = await TestFactory.getCategoryFrontCategories(category.id);

        expect(untouchedCategory).toEqual(category);
        expect(untouchedCategoryImages).toHaveLength(3);
        expect(untouchedCategoryImages).toEqual(
            expect.arrayContaining([
                expect.objectContaining({
                    imageUrl: 'http://avatars/111',
                    filename: '111.png',
                    imageDimension: expect.objectContaining({width: 2, height: 2})
                }),
                expect.objectContaining({
                    imageUrl: 'http://avatars/222',
                    filename: '222.png',
                    imageDimension: expect.objectContaining({width: 2, height: 2})
                }),
                expect.objectContaining({
                    imageUrl: 'http://avatars/333',
                    filename: '333.png',
                    imageDimension: expect.objectContaining({width: 2, height: 2})
                })
            ])
        );
        expect(untouchedCategoryFrontCategories).toEqual([
            expect.objectContaining({frontCategoryId: frontCategories[0].id}),
            expect.objectContaining({frontCategoryId: frontCategories[1].id})
        ]);

        const updatedCategory = (await TestFactory.getCategories()).find(({id}) => id === newCategory.id)!;
        const updatedCategoryImages = await TestFactory.getCategoryImages(newCategory.id);
        const updatedCategoryFrontCategories = await TestFactory.getCategoryFrontCategories(newCategory.id);

        expect(updatedCategory).toEqual({
            ...category,
            id: newCategory.id,
            historySubjectId: expect.any(Number),
            legacyId: newCategory.legacyId,
            code: newCategory.code,
            status: updateParams.status,
            shortTitleTranslationMap: updateParams.shortTitleTranslations,
            longTitleTranslationMap: updateParams.longTitleTranslations,
            meta: updateParams.meta,
            description: updateParams.description,
            specialCategory: updateParams.specialCategory,
            deeplink: updateParams.deeplink
        });
        expect(updatedCategoryImages).toHaveLength(2);
        expect(updatedCategoryImages).toEqual(
            expect.arrayContaining([
                expect.objectContaining({
                    imageUrl: 'http://avatars/111',
                    filename: '111.png',
                    imageDimension: expect.objectContaining({width: 2, height: 2})
                }),
                expect.objectContaining({
                    imageUrl: 'http://avatars/222',
                    filename: '222.png',
                    imageDimension: expect.objectContaining({width: 2, height: 2})
                })
            ])
        );
        expect(updatedCategoryFrontCategories).toEqual([
            expect.objectContaining({frontCategoryId: frontCategories[0].id}),
            expect.objectContaining({frontCategoryId: frontCategories[1].id})
        ]);
    });

    it('should replace category with duplicated category in selected groups', async () => {
        const groups = await Promise.all([
            TestFactory.createGroup({
                userId: user.id,
                regionId: regions[0].id
            }),
            TestFactory.createGroup({
                userId: user.id,
                regionId: regions[0].id
            })
        ]);

        const category = await TestFactory.createCategory({
            userId: user.id,
            regionId: regions[0].id,
            images: [
                {imageUrl: 'http://avatars/111', filename: '111.png', width: 2, height: 2},
                {imageUrl: 'http://avatars/222', filename: '222.png', width: 2, height: 2}
            ]
        });

        await TestFactory.linkCategoryToGroup({
            userId: user.id,
            groupId: groups[0].id,
            categoryId: category.id,
            meta: {foo: 'link meta 1'},
            images: [{imageUrl: 'http://avatars/111', width: 2, height: 2}]
        });

        await TestFactory.linkCategoryToGroup({
            userId: user.id,
            groupId: groups[1].id,
            categoryId: category.id,
            meta: {foo: 'link meta 2'},
            images: [{imageUrl: 'http://avatars/222', width: 2, height: 2}]
        });

        const groupCategories = await Promise.all(groups.map(({id}) => TestFactory.getGroupCategories(id)));

        expect(groupCategories).toEqual([
            [
                expect.objectContaining({
                    categoryId: category.id,
                    meta: {foo: 'link meta 1'},
                    categoryImages: [
                        expect.objectContaining({
                            imageUrl: 'http://avatars/111',
                            filename: '111.png',
                            imageDimension: expect.objectContaining({width: 2, height: 2})
                        })
                    ]
                })
            ],
            [
                expect.objectContaining({
                    categoryId: category.id,
                    meta: {foo: 'link meta 2'},
                    categoryImages: [
                        expect.objectContaining({
                            imageUrl: 'http://avatars/222',
                            filename: '222.png',
                            imageDimension: expect.objectContaining({width: 2, height: 2})
                        })
                    ]
                })
            ]
        ]);

        const updateParams: UpdatedCategory = {
            code: category.code + '_duplicated',
            groups: [{id: groups[1].id}]
        };

        const newCategory = await updateCategoryHandler.handle({
            context,
            data: {params: {id: category.id}, body: updateParams}
        });

        const updatedGroupCategories = await Promise.all(groups.map(({id}) => TestFactory.getGroupCategories(id)));

        expect(updatedGroupCategories).toEqual([
            [
                expect.objectContaining({
                    categoryId: category.id,
                    meta: {foo: 'link meta 1'},
                    categoryImages: [
                        expect.objectContaining({
                            imageUrl: 'http://avatars/111',
                            filename: '111.png',
                            imageDimension: expect.objectContaining({width: 2, height: 2})
                        })
                    ]
                })
            ],
            [
                expect.objectContaining({
                    categoryId: newCategory.id,
                    meta: {foo: 'link meta 2'},
                    categoryImages: [
                        expect.objectContaining({
                            imageUrl: 'http://avatars/222',
                            filename: '222.png',
                            imageDimension: expect.objectContaining({width: 2, height: 2})
                        })
                    ]
                })
            ]
        ]);
    });

    it('should throw error if selected category is not linked', async () => {
        const groups = await Promise.all([
            TestFactory.createGroup({
                userId: user.id,
                regionId: regions[0].id
            }),
            TestFactory.createGroup({
                userId: user.id,
                regionId: regions[0].id
            })
        ]);

        const category = await TestFactory.createCategory({
            userId: user.id,
            regionId: regions[0].id
        });

        await TestFactory.linkCategoryToGroup({
            userId: user.id,
            groupId: groups[0].id,
            categoryId: category.id
        });

        const updateParams: UpdatedCategory = {groups: [{id: groups[1].id}]};

        await expect(
            updateCategoryHandler.handle({context, data: {params: {id: category.id}, body: updateParams}})
        ).rejects.toThrow(EntityNotFoundError);
    });

    it('should throw error while trying activate category without images', async () => {
        const category = await TestFactory.createCategory({
            userId: user.id,
            regionId: regions[0].id,
            status: CatalogStatus.DISABLED
        });

        const updateParams: UpdatedCategory = {
            status: CatalogStatus.ACTIVE,
            groups: []
        };

        await expect(
            updateCategoryHandler.handle({context, data: {params: {id: category.id}, body: updateParams}})
        ).rejects.toThrow(ActivateCategoryWithoutImagesIsForbidden);
    });
});
