import {CommissionType} from '../../enums';
import {getErrors} from '../validate';

describe('Проверка валидации при создании комиссий', () => {
    test('При вводе отрицательных чисел должна возвращаться соответствующая ошибка', () => {
        const commissionPercentModel = {
            type: 'fixed_rate' as CommissionType,
            user_cancel_min_td: -1,
            user_cancel_max_td: -1,
            billable_cancel_distance: -1,
            park_cancel_min_td: -1,
            park_cancel_max_td: -1,
            min_order_cost: '-1',
            max_order_cost: '-1',
            agent_percent: '-1',
            hiring_age: -1,
            hiring_commercial: '-1',
            hiring: '-1',
            taximeter_payment: '-1',
            callcenter_commission_percent: '-1',
            acquiring_percent: '-1',
            vat: '-1',
            percent: '-1',
            expired_cost: '-1',
            expired_percent: '-1',
            unrealized_rate: -1,
            tag: '123',
            branding_discounts: [
                {
                    marketing_level: ['lightbox'],
                    value: '-1',
                },
            ],
        };

        const expectedErrors = {
            vat: 'Число должно быть не меньше 0',
            percent: 'Число должно быть не меньше 0',
            agent_percent: 'commissions.negative_numbers_error',
            asymp: false,
            billable_cancel_distance: 'commissions.negative_numbers_error',
            cancel_commission: false,
            cancel_percent: true,
            commission: false,
            cost_norm: false,
            expired_commission: false,
            expired_cost: 'commissions.negative_numbers_error',
            expired_percent: 'Число должно быть не меньше 0',
            max_commission_percent: false,
            max_order_cost: 'commissions.negative_numbers_error',
            min_order_cost: 'commissions.negative_numbers_error',
            numerator: false,
            park_cancel_max_td: 'commissions.negative_numbers_error',
            park_cancel_min_td: 'commissions.negative_numbers_error',
            user_cancel_max_td: 'commissions.negative_numbers_error',
            user_cancel_min_td: 'commissions.negative_numbers_error',
            ['branding_discounts[0].value']: 'commissions.negative_numbers_error',
            unrealized_rate: 'Число должно быть не меньше 0',
        };

        return expect(getErrors(commissionPercentModel)).toEqual(expectedErrors);
    });
});
