import {getDraftDiffFields} from '../matchers';

describe('api/drafts/matchers', () => {
    test('Кейс из тарифов', () => {
        const draft = {
            diff: {
                categories: {
                    0: {
                        driver_change_cost: [{}, {step: 1, max_delta: 1}]
                    }
                }
            }
        } as any;

        const actual = getDraftDiffFields(draft);
        const expected = {
            'categories.0.driver_change_cost.step': [undefined, 1],
            'categories.0.driver_change_cost.max_delta': [undefined, 1]
        };

        expect(actual.$diff).toEqual(expected);
    });
});
