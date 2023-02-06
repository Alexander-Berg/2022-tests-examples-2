import {describe, expect, it} from 'tests/jest.globals';

import {StructValidationError} from '@/src/errors';
import {createStructValidator} from 'server/routes/api/api-handler';
import {ProductComboStatus, ProductComboStruct, ProductComboType} from 'types/product-combo';

describe('check product combo body validation', () => {
    const validate = createStructValidator({body: ProductComboStruct});

    function executeValidation(body: unknown) {
        return validate({
            context: {} as never,
            payload: {body}
        });
    }

    it('should validate product combo body', async () => {
        const baseBody = {
            productIds: [],
            nameTranslations: {},
            descriptionTranslations: {},
            status: ProductComboStatus.ACTIVE,
            type: ProductComboType.DISCOUNT
        };

        // Позитивный кейс без указания прилинкованного мета-товара
        const body1 = {
            ...baseBody,
            groups: [
                {
                    id: null,
                    nameTranslations: {},
                    optionsToSelect: 1,
                    isSelectUnique: true,
                    options: [{productId: 1, id: null}]
                },
                {
                    id: null,
                    nameTranslations: {},
                    optionsToSelect: 1,
                    isSelectUnique: true,
                    options: [{productId: 2, id: null}]
                }
            ]
        };

        expect(() => executeValidation(body1)).not.toThrow();

        // Позитивный кейс без c указанием прилинкованных мета-товаров
        const body2 = {
            ...baseBody,
            productIds: [1, 2],
            groups: [
                {
                    id: null,
                    nameTranslations: {},
                    optionsToSelect: 1,
                    isSelectUnique: true,
                    options: [{productId: 1, id: null}]
                },
                {
                    id: null,
                    nameTranslations: {},
                    optionsToSelect: 1,
                    isSelectUnique: true,
                    options: [{productId: 2, id: null}]
                }
            ]
        };

        expect(() => executeValidation(body2)).not.toThrow();

        // Негативный кейс: пустые группы
        const body3 = {
            ...baseBody,
            groups: []
        };

        expect(() => executeValidation(body3)).toThrow(StructValidationError);

        // Негативный кейс: пустые опции в группе
        const body4 = {
            ...baseBody,
            groups: [
                {
                    id: null,
                    nameTranslations: {},
                    optionsToSelect: 2,
                    isSelectUnique: false,
                    options: [{productId: 1, id: null}]
                },
                {
                    id: null,
                    nameTranslations: {},
                    optionsToSelect: 1,
                    isSelectUnique: true,
                    options: []
                }
            ]
        };

        expect(() => executeValidation(body4)).toThrow(StructValidationError);
    });
});
