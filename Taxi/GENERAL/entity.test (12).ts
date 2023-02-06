import {describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';
import {createMasterCategoryWithInfoModel, madeJsonError} from 'tests/unit/util';

import {delayMs} from 'service/helper/delay';
import {AttributeType} from 'types/attribute';

describe('"product_attribute_value" entity', () => {
    it('should handle attribute value uniqueness', async () => {
        const {user, region, masterCategory} = await createMasterCategoryWithInfoModel();

        const stringAttr = await TestFactory.createAttribute({
            attribute: {type: AttributeType.STRING, isUnique: true},
            userId: user.id
        });

        for (let k = 0; k < 2; k++) {
            const product = await TestFactory.createProduct({
                userId: user.id,
                masterCategoryId: masterCategory.id,
                regionId: region.id
            });

            const promise = TestFactory.createProductAttributeValue({
                userId: user.id,
                value: 'srt_a',
                productId: product.id,
                attributeId: stringAttr.id
            });

            if (k > 0) {
                // Вторая итерация должна бросать ошибку...
                expect(await madeJsonError(() => promise)).toEqual({
                    error: 'Non unique attribute value',
                    code: stringAttr.code,
                    dup: 'srt_a',
                    region_id: region.id
                });
            } else {
                await promise;
            }
        }
    });

    it('should handle attribute value uniqueness in different regions', async () => {
        const data = await Promise.all([createMasterCategoryWithInfoModel(), createMasterCategoryWithInfoModel()]);

        const stringAttr = await TestFactory.createAttribute({
            attribute: {type: AttributeType.STRING, isUnique: true},
            userId: data[0].user.id
        });

        for (let k = 0; k < 2; k++) {
            const product = await TestFactory.createProduct({
                userId: data[k].user.id,
                masterCategoryId: data[k].masterCategory.id,
                regionId: data[k].region.id
            });

            const promise = TestFactory.createProductAttributeValue({
                userId: data[0].user.id,
                value: 'srt_a',
                productId: product.id,
                attributeId: stringAttr.id
            });

            if (k > 0) {
                // Вторая итерация НЕ должна бросать ошибку
                expect(await madeJsonError(() => promise)).toBeUndefined();
            } else {
                await promise;
            }
        }
    });

    it('should update product "updated_at" after inserting new attributes', async () => {
        const {user, role, region, masterCategory, infoModel} = await createMasterCategoryWithInfoModel();

        const attribute = await TestFactory.createAttribute({
            attribute: {type: AttributeType.STRING},
            userId: user.id
        });

        await TestFactory.linkAttributesToInfoModel({
            userId: user.id,
            infoModelId: infoModel.id,
            attributes: [attribute]
        });

        const product = await TestFactory.createProduct({
            userId: user.id,
            masterCategoryId: masterCategory.id,
            regionId: region.id
        });

        const hsBefore = await TestFactory.getHistorySubject(product.historySubjectId);

        await delayMs(200);

        await TestFactory.updateProductViaUi(product, {
            user,
            role,
            region,
            productData: {
                changeAttributes: (attrs) => [...attrs, {attributeId: attribute.id, value: 'foo'}]
            }
        });

        const hsAfter = await TestFactory.getHistorySubject(product.historySubjectId);
        expect(hsBefore.updatedAt.getTime()).toBeLessThan(hsAfter.updatedAt.getTime());
    });

    it('should update product "updated_at" after updating new attributes', async () => {
        const {user, role, region, masterCategory, infoModel} = await createMasterCategoryWithInfoModel();

        const attribute = await TestFactory.createAttribute({
            attribute: {type: AttributeType.STRING},
            userId: user.id
        });

        await TestFactory.linkAttributesToInfoModel({
            userId: user.id,
            infoModelId: infoModel.id,
            attributes: [attribute]
        });

        const product = await TestFactory.createProduct({
            userId: user.id,
            masterCategoryId: masterCategory.id,
            regionId: region.id
        });

        await TestFactory.createProductAttributeValue({
            userId: user.id,
            value: 'foo',
            productId: product.id,
            attributeId: attribute.id
        });

        const hsBefore = await TestFactory.getHistorySubject(product.historySubjectId);

        await delayMs(200);

        await TestFactory.updateProductViaUi(product, {
            user,
            role,
            region,
            productData: {
                changeAttributes: (attrs) =>
                    attrs.map((attr) => (attr.attributeId === attribute.id ? {...attr, value: 'new_foo'} : attr))
            }
        });

        const hsAfter = await TestFactory.getHistorySubject(product.historySubjectId);
        expect(hsBefore.updatedAt.getTime()).toBeLessThan(hsAfter.updatedAt.getTime());
    });

    it('should update product "updated_at" after deleting new attributes', async () => {
        const {user, role, region, masterCategory, infoModel} = await createMasterCategoryWithInfoModel();

        const attribute = await TestFactory.createAttribute({
            attribute: {type: AttributeType.STRING},
            userId: user.id
        });

        await TestFactory.linkAttributesToInfoModel({
            userId: user.id,
            infoModelId: infoModel.id,
            attributes: [attribute]
        });

        const product = await TestFactory.createProduct({
            userId: user.id,
            masterCategoryId: masterCategory.id,
            regionId: region.id
        });

        await TestFactory.createProductAttributeValue({
            userId: user.id,
            value: 'foo',
            productId: product.id,
            attributeId: attribute.id
        });

        const hsBefore = await TestFactory.getHistorySubject(product.historySubjectId);

        await delayMs(200);

        await TestFactory.updateProductViaUi(product, {
            user,
            role,
            region,
            productData: {
                changeAttributes: (attrs) => attrs.filter(({attributeId}) => attributeId !== attribute.id)
            }
        });

        const hsAfter = await TestFactory.getHistorySubject(product.historySubjectId);
        expect(hsBefore.updatedAt.getTime()).toBeLessThan(hsAfter.updatedAt.getTime());
    });

    it('should forbid "lang_id" change', async () => {
        const {user, region, masterCategory} = await createMasterCategoryWithInfoModel();
        const lang = await TestFactory.createLang();
        const anotherLang = await TestFactory.createLang();

        const attribute = await TestFactory.createAttribute({
            attribute: {type: AttributeType.STRING, isValueLocalizable: true},
            userId: user.id
        });

        const product = await TestFactory.createProduct({
            userId: user.id,
            masterCategoryId: masterCategory.id,
            regionId: region.id
        });

        await TestFactory.createProductAttributeValue({
            userId: user.id,
            value: 'foo',
            langId: lang.id,
            productId: product.id,
            attributeId: attribute.id
        });

        await expect(
            TestFactory.updateProductAttributeValue({
                userId: user.id,
                productId: product.id,
                attributeId: attribute.id,
                volume: {langId: anotherLang.id}
            })
        ).rejects.toThrow('LANG_ID_UPDATE_IS_FORBIDDEN');
    });

    it('should forbid "lang_id" add', async () => {
        const {user, region, masterCategory} = await createMasterCategoryWithInfoModel();
        const lang = await TestFactory.createLang();

        const attribute = await TestFactory.createAttribute({
            attribute: {type: AttributeType.STRING, isValueLocalizable: false},
            userId: user.id
        });

        const product = await TestFactory.createProduct({
            userId: user.id,
            masterCategoryId: masterCategory.id,
            regionId: region.id
        });

        await TestFactory.createProductAttributeValue({
            userId: user.id,
            value: 'foo',
            productId: product.id,
            attributeId: attribute.id
        });

        await expect(
            TestFactory.updateProductAttributeValue({
                userId: user.id,
                productId: product.id,
                attributeId: attribute.id,
                volume: {langId: lang.id}
            })
        ).rejects.toThrow('LANG_ID_UPDATE_IS_FORBIDDEN');
    });

    it('should forbid "lang_id" remove', async () => {
        const {user, region, masterCategory} = await createMasterCategoryWithInfoModel();
        const lang = await TestFactory.createLang();

        const attribute = await TestFactory.createAttribute({
            attribute: {type: AttributeType.STRING, isValueLocalizable: true},
            userId: user.id
        });

        const product = await TestFactory.createProduct({
            userId: user.id,
            masterCategoryId: masterCategory.id,
            regionId: region.id
        });

        await TestFactory.createProductAttributeValue({
            userId: user.id,
            value: 'foo',
            langId: lang.id,
            productId: product.id,
            attributeId: attribute.id
        });

        await expect(
            TestFactory.updateProductAttributeValue({
                userId: user.id,
                productId: product.id,
                attributeId: attribute.id,
                volume: {langId: null}
            })
        ).rejects.toThrow('LANG_ID_UPDATE_IS_FORBIDDEN');
    });

    it('should forbid localizable attribute value without lang', async () => {
        const {user, region, masterCategory} = await createMasterCategoryWithInfoModel();

        const attribute = await TestFactory.createAttribute({
            attribute: {type: AttributeType.STRING, isValueLocalizable: true},
            userId: user.id
        });

        const product = await TestFactory.createProduct({
            userId: user.id,
            masterCategoryId: masterCategory.id,
            regionId: region.id
        });

        const promise = TestFactory.createProductAttributeValue({
            userId: user.id,
            value: 'foo',
            productId: product.id,
            attributeId: attribute.id
        });

        await expect(madeJsonError(() => promise)).resolves.toEqual({
            error: 'Localizable attribute value without lang',
            code: attribute.code
        });
    });

    it('should forbid non localizable attribute value with lang', async () => {
        const {user, region, masterCategory} = await createMasterCategoryWithInfoModel();
        const lang = await TestFactory.createLang();

        const attribute = await TestFactory.createAttribute({
            attribute: {type: AttributeType.STRING, isValueLocalizable: false},
            userId: user.id
        });

        const product = await TestFactory.createProduct({
            userId: user.id,
            masterCategoryId: masterCategory.id,
            regionId: region.id
        });

        const promise = TestFactory.createProductAttributeValue({
            userId: user.id,
            value: 'foo',
            langId: lang.id,
            productId: product.id,
            attributeId: attribute.id
        });

        await expect(madeJsonError(() => promise)).resolves.toEqual({
            error: 'Non localizable attribute value with lang',
            code: attribute.code,
            lang_id: lang.id
        });
    });
});
