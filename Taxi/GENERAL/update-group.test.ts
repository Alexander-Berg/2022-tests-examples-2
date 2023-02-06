/* eslint-disable @typescript-eslint/no-non-null-assertion */
import {beforeEach, describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';

import type {Lang} from '@/src/entities/lang/entity';
import type {Region} from '@/src/entities/region/entity';
import type {User} from '@/src/entities/user/entity';
import {ActivateGroupWithoutImagesIsForbidden, EntityNotFoundError} from '@/src/errors';
import type {ApiRequestContext} from 'server/routes/api/api-handler';
import {CatalogStatus} from 'types/catalog/base';
import type {UpdatedGroup} from 'types/catalog/group';

import {updateGroupHandler} from './update-group';

describe('update group', () => {
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

    it('should update group itself', async () => {
        const group = await TestFactory.createGroup({
            userId: user.id,
            regionId: regions[0].id,
            status: CatalogStatus.DISABLED,
            shortTitleTranslationMap: {
                [langCodes[0]]: 'прилавок'
            },
            longTitleTranslationMap: {
                [langCodes[0]]: 'прилаво',
                [langCodes[1]]: 'grou'
            },
            images: [{imageUrl: 'http://avatars/111', filename: '111.png', width: 2, height: 2}]
        });

        const updateParams: UpdatedGroup = {
            status: CatalogStatus.ACTIVE,
            shortTitleTranslations: {
                [langCodes[1]]: 'group'
            },
            longTitleTranslations: {
                [langCodes[0]]: 'прилавок',
                [langCodes[1]]: 'group'
            },
            meta: {foo: 'bar'},
            description: 'description',
            grids: []
        };

        await updateGroupHandler.handle({context, data: {params: {id: group.id}, body: updateParams}});
        const updatedGroup = (await TestFactory.getGroups()).find(({id}) => id === group.id)!;

        expect(updatedGroup).toEqual({
            ...group,
            status: updateParams.status,
            shortTitleTranslationMap: updateParams.shortTitleTranslations,
            longTitleTranslationMap: updateParams.longTitleTranslations,
            meta: updateParams.meta,
            description: updateParams.description
        });
    });

    it('should update images', async () => {
        const group = await TestFactory.createGroup({
            userId: user.id,
            regionId: regions[0].id,
            images: [
                {imageUrl: 'http://avatars/111', filename: '111.png', width: 2, height: 2},
                {imageUrl: 'http://avatars/222', filename: '222.png', width: 2, height: 2}
            ]
        });

        const updateParams: UpdatedGroup = {
            images: [
                {imageUrl: 'http://avatars/333', filename: '333.png'},
                {imageUrl: 'http://avatars/111', filename: '111_old.png'}
            ],
            grids: []
        };

        const groupImages = await TestFactory.getGroupImages(group.id);

        expect(groupImages).toHaveLength(2);
        expect(groupImages).toEqual(
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

        await updateGroupHandler.handle({context, data: {params: {id: group.id}, body: updateParams}});
        const updatedGroupImages = await TestFactory.getGroupImages(group.id);

        expect(updatedGroupImages).toHaveLength(2);
        expect(updatedGroupImages).toEqual(
            expect.arrayContaining([
                expect.objectContaining({
                    imageUrl: 'http://avatars/111',
                    filename: '111_old.png',
                    imageDimension: expect.objectContaining({width: 2, height: 2})
                }),
                expect.objectContaining({
                    imageUrl: 'http://avatars/333',
                    filename: '333.png',
                    imageDimension: expect.objectContaining({width: 2, height: 2})
                })
            ])
        );
    });

    it('should throw error if linked group image is removing', async () => {
        const grid = await TestFactory.createGrid({
            userId: user.id,
            regionId: regions[0].id
        });

        const group = await TestFactory.createGroup({
            userId: user.id,
            regionId: regions[0].id,
            images: [{imageUrl: 'http://avatars/111', filename: '111.png', width: 2, height: 2}]
        });

        await TestFactory.linkGroupToGrid({
            userId: user.id,
            gridId: grid.id,
            groupId: group.id,
            images: [{imageUrl: 'http://avatars/111', width: 2, height: 2}]
        });

        const updateParams: UpdatedGroup = {images: [], grids: [{id: grid.id}]};

        await expect(
            updateGroupHandler.handle({context, data: {params: {id: group.id}, body: updateParams}})
        ).rejects.toThrow(/fk__grid_group_image__group_image_id__group_image/);
    });

    it('should update linked categories', async () => {
        const group = await TestFactory.createGroup({
            userId: user.id,
            regionId: regions[0].id
        });

        const categories = await Promise.all([
            TestFactory.createCategory({
                userId: user.id,
                regionId: regions[0].id,
                images: [
                    {imageUrl: 'http://avatars/0/111', filename: '0_111.png', width: 2, height: 2},
                    {imageUrl: 'http://avatars/0/222', filename: '0_222.png', width: 2, height: 2}
                ]
            }),
            TestFactory.createCategory({
                userId: user.id,
                regionId: regions[0].id,
                images: [
                    {imageUrl: 'http://avatars/1/111', filename: '1_111.png', width: 2, height: 2},
                    {imageUrl: 'http://avatars/1/222', filename: '1_222.png', width: 2, height: 2}
                ]
            }),
            TestFactory.createCategory({
                userId: user.id,
                regionId: regions[0].id,
                images: [
                    {imageUrl: 'http://avatars/2/111', filename: '2_111.png', width: 2, height: 2},
                    {imageUrl: 'http://avatars/2/222', filename: '2_222.png', width: 2, height: 2}
                ]
            }),
            TestFactory.createCategory({
                userId: user.id,
                regionId: regions[0].id,
                images: [
                    {imageUrl: 'http://avatars/3/111', filename: '3_111.png', width: 2, height: 2},
                    {imageUrl: 'http://avatars/3/222', filename: '3_222.png', width: 2, height: 2}
                ]
            })
        ]);

        await TestFactory.linkCategoryToGroup({
            userId: user.id,
            groupId: group.id,
            categoryId: categories[0].id,
            images: [{imageUrl: 'http://avatars/0/111', width: 2, height: 2}]
        });

        await TestFactory.linkCategoryToGroup({
            userId: user.id,
            groupId: group.id,
            categoryId: categories[1].id,
            images: [
                {imageUrl: 'http://avatars/1/111', width: 2, height: 2},
                {imageUrl: 'http://avatars/1/222', width: 2, height: 2}
            ],
            meta: {foo: 'bar'}
        });

        await TestFactory.linkCategoryToGroup({
            userId: user.id,
            groupId: group.id,
            categoryId: categories[2].id,
            images: [{imageUrl: 'http://avatars/2/222', width: 2, height: 2}]
        });

        const updateParams: UpdatedGroup = {
            categories: [
                {
                    id: categories[1].id,
                    linkImages: [{imageUrl: 'http://avatars/1/111', filename: '1_111.png', formats: [2]}],
                    linkMeta: {foo: 'bar100500'}
                },
                {
                    id: categories[3].id,
                    linkImages: [
                        {imageUrl: 'http://avatars/3/222', filename: '3_222.png', formats: [2]},
                        {imageUrl: 'http://avatars/3/111', filename: '3_111.png', formats: [2]}
                    ],
                    linkMeta: {}
                },
                {
                    id: categories[2].id,
                    linkImages: [{imageUrl: 'http://avatars/2/222', filename: '2_222.png', formats: [2]}],
                    linkMeta: {}
                }
            ],
            grids: []
        };

        await updateGroupHandler.handle({context, data: {params: {id: group.id}, body: updateParams}});
        const groupCategories = await TestFactory.getGroupCategories(group.id);

        expect(groupCategories).toEqual([
            expect.objectContaining({
                categoryId: categories[1].id,
                meta: {foo: 'bar100500'},
                categoryImages: [
                    expect.objectContaining({
                        imageUrl: 'http://avatars/1/111',
                        filename: '1_111.png',
                        imageDimension: expect.objectContaining({width: 2, height: 2})
                    })
                ]
            }),
            expect.objectContaining({
                categoryId: categories[3].id,
                meta: {},
                categoryImages: [
                    expect.objectContaining({
                        imageUrl: 'http://avatars/3/111',
                        filename: '3_111.png',
                        imageDimension: expect.objectContaining({width: 2, height: 2})
                    }),
                    expect.objectContaining({
                        imageUrl: 'http://avatars/3/222',
                        filename: '3_222.png',
                        imageDimension: expect.objectContaining({width: 2, height: 2})
                    })
                ]
            }),
            expect.objectContaining({
                categoryId: categories[2].id,
                meta: {},
                categoryImages: [
                    expect.objectContaining({
                        imageUrl: 'http://avatars/2/222',
                        filename: '2_222.png',
                        imageDimension: expect.objectContaining({width: 2, height: 2})
                    })
                ]
            })
        ]);
    });

    it('should not link category from another region', async () => {
        const group = await TestFactory.createGroup({
            userId: user.id,
            regionId: regions[0].id
        });

        const category = await TestFactory.createCategory({
            userId: user.id,
            regionId: regions[1].id
        });

        const updateParams: UpdatedGroup = {
            grids: [],
            categories: [{id: category.id, linkMeta: {}, linkImages: []}]
        };

        await expect(
            updateGroupHandler.handle({context, data: {params: {id: group.id}, body: updateParams}})
        ).rejects.toThrow('FALSY check_group_category_region');
    });

    it('should not link foreign category images', async () => {
        const group = await TestFactory.createGroup({
            userId: user.id,
            regionId: regions[0].id
        });

        const categories = await Promise.all([
            TestFactory.createCategory({
                userId: user.id,
                regionId: regions[0].id,
                images: [{imageUrl: 'http://avatars/0/111', filename: '0_111.png', width: 2, height: 2}]
            }),
            TestFactory.createCategory({
                userId: user.id,
                regionId: regions[0].id,
                images: [{imageUrl: 'http://avatars/1/111', filename: '1_111.png', width: 2, height: 2}]
            })
        ]);

        await TestFactory.linkCategoryToGroup({
            userId: user.id,
            groupId: group.id,
            categoryId: categories[0].id,
            images: [{imageUrl: 'http://avatars/0/111', width: 2, height: 2}]
        });

        await TestFactory.linkCategoryToGroup({
            userId: user.id,
            groupId: group.id,
            categoryId: categories[1].id,
            images: [{imageUrl: 'http://avatars/1/111', width: 2, height: 2}]
        });

        const updateParams: UpdatedGroup = {
            grids: [],
            categories: [
                {
                    id: categories[0].id,
                    linkMeta: {},
                    linkImages: [{imageUrl: 'http://avatars/1/111', filename: '1_111.png', formats: [2]}]
                },
                {
                    id: categories[1].id,
                    linkMeta: {},
                    linkImages: [{imageUrl: 'http://avatars/0/111', filename: '0_111.png', formats: [2]}]
                }
            ]
        };

        await expect(
            updateGroupHandler.handle({context, data: {params: {id: group.id}, body: updateParams}})
        ).rejects.toThrow(EntityNotFoundError);
    });

    it('should update group when all grids selected', async () => {
        const grids = await Promise.all([
            TestFactory.createGrid({
                userId: user.id,
                regionId: regions[0].id
            }),
            TestFactory.createGrid({
                userId: user.id,
                regionId: regions[0].id
            })
        ]);

        const group = await TestFactory.createGroup({
            userId: user.id,
            regionId: regions[0].id
        });

        await TestFactory.linkGroupToGrid({
            userId: user.id,
            gridId: grids[0].id,
            groupId: group.id
        });

        await TestFactory.linkGroupToGrid({
            userId: user.id,
            gridId: grids[1].id,
            groupId: group.id
        });

        const updateParams: UpdatedGroup = {meta: {foo: 'bar'}, grids: grids.map(({id}) => ({id}))};

        await updateGroupHandler.handle({context, data: {params: {id: group.id}, body: updateParams}});
        const updatedGroup = (await TestFactory.getGroups()).find(({id}) => id === group.id)!;

        expect(updatedGroup).toEqual({...group, meta: updateParams.meta});
    });

    it('should duplicate group with images and links when part of grids selected', async () => {
        const grids = await Promise.all([
            TestFactory.createGrid({
                userId: user.id,
                regionId: regions[0].id
            }),
            TestFactory.createGrid({
                userId: user.id,
                regionId: regions[0].id
            })
        ]);

        const group = await TestFactory.createGroup({
            userId: user.id,
            regionId: regions[0].id,
            status: CatalogStatus.DISABLED,
            meta: {foo: 'bar'},
            shortTitleTranslationMap: {
                [langCodes[0]]: 'прилавок'
            },
            longTitleTranslationMap: {
                [langCodes[1]]: 'group'
            },
            description: 'description',
            images: [
                {imageUrl: 'http://avatars/group/111', filename: '111.png', width: 2, height: 2},
                {imageUrl: 'http://avatars/group/222', filename: '222.png', width: 2, height: 2},
                {imageUrl: 'http://avatars/group/333', filename: '333.png', width: 2, height: 2}
            ]
        });

        const categories = await Promise.all([
            TestFactory.createCategory({
                userId: user.id,
                regionId: regions[0].id,
                images: [
                    {imageUrl: 'http://avatars/category/0/111', filename: '0_111.png', width: 2, height: 2},
                    {imageUrl: 'http://avatars/category/0/222', filename: '0_222.png', width: 2, height: 2}
                ]
            }),
            TestFactory.createCategory({
                userId: user.id,
                regionId: regions[0].id,
                images: [
                    {imageUrl: 'http://avatars/category/1/111', filename: '1_111.png', width: 2, height: 2},
                    {imageUrl: 'http://avatars/category/1/222', filename: '1_222.png', width: 2, height: 2}
                ]
            })
        ]);

        await TestFactory.linkGroupToGrid({
            userId: user.id,
            gridId: grids[0].id,
            groupId: group.id,
            meta: {foo: 'grid link meta 0'},
            images: [{imageUrl: 'http://avatars/group/111', width: 2, height: 2}]
        });

        await TestFactory.linkGroupToGrid({
            userId: user.id,
            gridId: grids[1].id,
            groupId: group.id,
            meta: {foo: 'grid link meta 1'},
            images: [{imageUrl: 'http://avatars/group/222', width: 2, height: 2}]
        });

        await TestFactory.linkCategoryToGroup({
            userId: user.id,
            groupId: group.id,
            categoryId: categories[0].id,
            images: [{imageUrl: 'http://avatars/category/0/111', width: 2, height: 2}],
            meta: {foo: 'category link meta 0'}
        });

        await TestFactory.linkCategoryToGroup({
            userId: user.id,
            groupId: group.id,
            categoryId: categories[1].id,
            images: [{imageUrl: 'http://avatars/category/1/111', width: 2, height: 2}],
            meta: {foo: 'category link meta 1'}
        });

        const updateParams: UpdatedGroup = {
            code: group.code + '_duplicated',
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
                {imageUrl: 'http://avatars/group/111', filename: '111.png'},
                {imageUrl: 'http://avatars/group/222', filename: '222.png'}
            ],
            categories: [
                {
                    id: categories[0].id,
                    linkMeta: {foo: 'category link meta 0'},
                    linkImages: [{imageUrl: 'http://avatars/category/0/222', filename: '0_222.png', formats: [2]}]
                },
                {
                    id: categories[1].id,
                    linkMeta: {foo: 'category link meta 1'},
                    linkImages: [{imageUrl: 'http://avatars/category/1/222', filename: '1_222.png', formats: [2]}]
                }
            ],
            grids: [{id: grids[1].id}]
        };

        const newGroup = await updateGroupHandler.handle({
            context,
            data: {params: {id: group.id}, body: updateParams}
        });

        const untouchedGroup = (await TestFactory.getGroups()).find(({id}) => id === group.id)!;
        const untouchedGroupImages = await TestFactory.getGroupImages(group.id);
        const untouchedGroupCategories = await TestFactory.getGroupCategories(group.id);

        expect(untouchedGroup).toEqual(group);
        expect(untouchedGroupImages).toHaveLength(3);
        expect(untouchedGroupImages).toEqual(
            expect.arrayContaining([
                expect.objectContaining({
                    imageUrl: 'http://avatars/group/111',
                    filename: '111.png',
                    imageDimension: expect.objectContaining({width: 2, height: 2})
                }),
                expect.objectContaining({
                    imageUrl: 'http://avatars/group/222',
                    filename: '222.png',
                    imageDimension: expect.objectContaining({width: 2, height: 2})
                }),
                expect.objectContaining({
                    imageUrl: 'http://avatars/group/333',
                    filename: '333.png',
                    imageDimension: expect.objectContaining({width: 2, height: 2})
                })
            ])
        );
        expect(untouchedGroupCategories).toEqual([
            expect.objectContaining({
                categoryId: categories[0].id,
                meta: {foo: 'category link meta 0'},
                categoryImages: [
                    expect.objectContaining({
                        imageUrl: 'http://avatars/category/0/111',
                        filename: '0_111.png',
                        imageDimension: expect.objectContaining({width: 2, height: 2})
                    })
                ]
            }),
            expect.objectContaining({
                categoryId: categories[1].id,
                meta: {foo: 'category link meta 1'},
                categoryImages: [
                    expect.objectContaining({
                        imageUrl: 'http://avatars/category/1/111',
                        filename: '1_111.png',
                        imageDimension: expect.objectContaining({width: 2, height: 2})
                    })
                ]
            })
        ]);

        const updatedGroup = (await TestFactory.getGroups()).find(({id}) => id === newGroup.id)!;
        const updatedGroupImages = await TestFactory.getGroupImages(newGroup.id);
        const updatedGroupCategories = await TestFactory.getGroupCategories(newGroup.id);

        expect(updatedGroup).toEqual({
            ...group,
            id: newGroup.id,
            historySubjectId: expect.any(Number),
            legacyId: newGroup.legacyId,
            code: newGroup.code,
            status: updateParams.status,
            shortTitleTranslationMap: updateParams.shortTitleTranslations,
            longTitleTranslationMap: updateParams.longTitleTranslations,
            meta: updateParams.meta,
            description: updateParams.description
        });
        expect(updatedGroupImages).toHaveLength(2);
        expect(updatedGroupImages).toEqual(
            expect.arrayContaining([
                expect.objectContaining({
                    imageUrl: 'http://avatars/group/111',
                    filename: '111.png',
                    imageDimension: expect.objectContaining({width: 2, height: 2})
                }),
                expect.objectContaining({
                    imageUrl: 'http://avatars/group/222',
                    filename: '222.png',
                    imageDimension: expect.objectContaining({width: 2, height: 2})
                })
            ])
        );
        expect(updatedGroupCategories).toEqual([
            expect.objectContaining({
                categoryId: categories[0].id,
                meta: {foo: 'category link meta 0'},
                categoryImages: [
                    expect.objectContaining({
                        imageUrl: 'http://avatars/category/0/222',
                        filename: '0_222.png',
                        imageDimension: expect.objectContaining({width: 2, height: 2})
                    })
                ]
            }),
            expect.objectContaining({
                categoryId: categories[1].id,
                meta: {foo: 'category link meta 1'},
                categoryImages: [
                    expect.objectContaining({
                        imageUrl: 'http://avatars/category/1/222',
                        filename: '1_222.png',
                        imageDimension: expect.objectContaining({width: 2, height: 2})
                    })
                ]
            })
        ]);
    });

    it('should replace group with duplicated group in selected grids', async () => {
        const grids = await Promise.all([
            TestFactory.createGrid({
                userId: user.id,
                regionId: regions[0].id
            }),
            TestFactory.createGrid({
                userId: user.id,
                regionId: regions[0].id
            })
        ]);

        const group = await TestFactory.createGroup({
            userId: user.id,
            regionId: regions[0].id,
            images: [
                {imageUrl: 'http://avatars/group/111', filename: '111.png', width: 2, height: 2},
                {imageUrl: 'http://avatars/group/222', filename: '222.png', width: 2, height: 2}
            ]
        });

        await TestFactory.linkGroupToGrid({
            userId: user.id,
            gridId: grids[0].id,
            groupId: group.id,
            meta: {foo: 'link meta 1'},
            images: [{imageUrl: 'http://avatars/group/111', width: 2, height: 2}]
        });

        await TestFactory.linkGroupToGrid({
            userId: user.id,
            gridId: grids[1].id,
            groupId: group.id,
            meta: {foo: 'link meta 2'},
            images: [{imageUrl: 'http://avatars/group/222', width: 2, height: 2}]
        });

        const gridGroups = await Promise.all(grids.map(({id}) => TestFactory.getGridGroups(id)));

        expect(gridGroups).toEqual([
            [
                expect.objectContaining({
                    groupId: group.id,
                    meta: {foo: 'link meta 1'},
                    groupImages: [
                        expect.objectContaining({
                            imageUrl: 'http://avatars/group/111',
                            filename: '111.png',
                            imageDimension: expect.objectContaining({width: 2, height: 2})
                        })
                    ]
                })
            ],
            [
                expect.objectContaining({
                    groupId: group.id,
                    meta: {foo: 'link meta 2'},
                    groupImages: [
                        expect.objectContaining({
                            imageUrl: 'http://avatars/group/222',
                            filename: '222.png',
                            imageDimension: expect.objectContaining({width: 2, height: 2})
                        })
                    ]
                })
            ]
        ]);

        const updateParams: UpdatedGroup = {
            code: group.code + '_duplicated',
            grids: [{id: grids[1].id}]
        };

        const newGroup = await updateGroupHandler.handle({
            context,
            data: {params: {id: group.id}, body: updateParams}
        });

        const updatedGridGroups = await Promise.all(grids.map(({id}) => TestFactory.getGridGroups(id)));

        expect(updatedGridGroups).toEqual([
            [
                expect.objectContaining({
                    groupId: group.id,
                    meta: {foo: 'link meta 1'},
                    groupImages: [
                        expect.objectContaining({
                            imageUrl: 'http://avatars/group/111',
                            imageDimension: expect.objectContaining({width: 2, height: 2})
                        })
                    ]
                })
            ],
            [
                expect.objectContaining({
                    groupId: newGroup.id,
                    meta: {foo: 'link meta 2'},
                    groupImages: [
                        expect.objectContaining({
                            imageUrl: 'http://avatars/group/222',
                            imageDimension: expect.objectContaining({width: 2, height: 2})
                        })
                    ]
                })
            ]
        ]);
    });

    it('should throw error if selected grid is not linked', async () => {
        const grids = await Promise.all([
            TestFactory.createGrid({
                userId: user.id,
                regionId: regions[0].id
            }),
            TestFactory.createGrid({
                userId: user.id,
                regionId: regions[0].id
            })
        ]);

        const group = await TestFactory.createGroup({
            userId: user.id,
            regionId: regions[0].id
        });

        await TestFactory.linkGroupToGrid({
            userId: user.id,
            gridId: grids[0].id,
            groupId: group.id
        });

        const updateParams: UpdatedGroup = {grids: [{id: grids[1].id}]};

        await expect(
            updateGroupHandler.handle({context, data: {params: {id: group.id}, body: updateParams}})
        ).rejects.toThrow(EntityNotFoundError);
    });

    it('should throw error while trying activate group without images', async () => {
        const group = await TestFactory.createGroup({
            userId: user.id,
            regionId: regions[0].id,
            status: CatalogStatus.DISABLED
        });

        const updateParams: UpdatedGroup = {
            status: CatalogStatus.ACTIVE,
            grids: []
        };

        await expect(
            updateGroupHandler.handle({context, data: {params: {id: group.id}, body: updateParams}})
        ).rejects.toThrow(ActivateGroupWithoutImagesIsForbidden);
    });
});
