import {LIMIT_ID_PREFIX} from '../../consts';
import {DiscountValueType, DiscountViewValueType, RidesIntervalType, WeeklyLimitType} from '../../enums';
import {Discount, FlatDiscountView, LadderDiscountView, TableDiscountView} from '../../types';
import {makeBudgetModel} from '../../utils';
import {
    makeLimits,
    makeNoviceMeta,
    makeRidesParams,
    makeTripsRestriction,
    prepareBudgetModel,
    prepareCashbackMoneyModel,
    prepareCashbackMoneyValue,
} from '../commonDiscount';

describe('makeTripsRestriction', () => {
    it('Заполнены все поля', () => {
        const result = makeTripsRestriction({
            minTripsCount: '1',
            maxTripsCount: '2',
            brand: 'br',
            paymentType: 'pay',
            tariffClass: 'econ',
        });
        expect(result).toEqual([
            {
                brand: 'br',
                payment_type: 'pay',
                allowed_trips_count: {
                    start: 1,
                    end: 2,
                },
                tariff_class: 'econ',
            },
        ]);
    });

    it('Заполнен только минимум', () => {
        const result = makeTripsRestriction({
            minTripsCount: '1',
            maxTripsCount: '',
            brand: 'br',
            paymentType: 'pay',
            tariffClass: 'econ',
        });
        expect(result).toEqual([
            {
                allowed_trips_count: {
                    start: 1,
                    end: undefined,
                },
                brand: 'br',
                payment_type: 'pay',
                tariff_class: 'econ',
            },
        ]);
    });

    it('Пустая модель', () => {
        const result = makeTripsRestriction({
            minTripsCount: '',
            maxTripsCount: '',
            brand: '',
            paymentType: '',
            tariffClass: '',
        });
        expect(result).toBeUndefined();
    });
});

describe('makeLimits', () => {
    it('Заполнены все поля', () => {
        const result = makeLimits(
            {
                dailyValue: '1',
                dailyThreshold: '2',
                weeklyValue: '3',
                weeklyThreshold: '4',
                trackWeeklyBudget: true,
            },
            'id_1',
        );
        expect(result).toEqual({
            id: `${LIMIT_ID_PREFIX}id_1`,
            daily_limit: {
                value: '1',
                threshold: 2,
            },
            weekly_limit: {
                value: '3',
                threshold: 4,
                type: WeeklyLimitType.Sliding,
            },
        });
    });

    it('Пустая модель', () => {
        const result = makeLimits(
            {
                dailyValue: '',
                dailyThreshold: '',
                weeklyValue: '',
                weeklyThreshold: '',
                trackWeeklyBudget: false,
            },
            'id_1',
        );
        expect(result).toBeUndefined();
    });
});

const FLAT_DISCOUNT_VIEW: FlatDiscountView = {
    type: DiscountViewValueType.Flat,
    value: '5',
    maxValue: '10',
};
const FLAT_DISCOUNT: Discount = {
    discount_value: {
        value_type: DiscountValueType.Flat,
        value: 5,
    },
    max_absolute_value: 10,
};

const LADDER_DISCOUNT_VIEW: LadderDiscountView = {
    type: DiscountViewValueType.Ladder,
    maxValue: '',
    steps: [
        {fromCost: '0', discount: '10', maxDiscount: '45'},
        {fromCost: '3', discount: '15', maxDiscount: '45'},
    ],
};
const LADDER_DISCOUNT: Discount = {
    discount_value: {
        value_type: DiscountValueType.Hyperbolas,
        value: {
            threshold: 1000,
            hyperbola_lower: {
                p: 10,
                a: 0,
                c: 1,
            },
            hyperbola_upper: {
                p: 10,
                a: 0,
                c: 1,
            },
        },
    },
    max_absolute_value: 45,
    discounts_with_discount_counters: [
        {
            discount_value: {
                value_type: DiscountValueType.Hyperbolas,
                value: {
                    threshold: 1000,
                    hyperbola_lower: {
                        p: 15,
                        a: 0,
                        c: 1,
                    },
                    hyperbola_upper: {
                        p: 15,
                        a: 0,
                        c: 1,
                    },
                },
            },
            min_discounts_count: 3,
            max_absolute_value: 45,
        },
    ],
};

const TABLE_DISCOUNT_VIEW: TableDiscountView = {
    type: DiscountViewValueType.Table,
    maxValue: '70',
    steps: [
        {fromCost: '3', discount: '20'},
        {fromCost: '7', discount: '25'},
    ],
};
const TABLE_DISCOUNT: Discount = {
    discount_value: {
        value_type: DiscountValueType.Table,
        value: [
            {from_cost: 3, discount: 20},
            {from_cost: 7, discount: 25},
        ],
    },
    max_absolute_value: 70,
};

describe('prepareCashbackMoneyValue', () => {
    it('FlatDiscountView', () => {
        const result = prepareCashbackMoneyValue(FLAT_DISCOUNT_VIEW);
        expect(result).toEqual(FLAT_DISCOUNT);
    });

    it('LadderDiscountView', () => {
        const result = prepareCashbackMoneyValue(LADDER_DISCOUNT_VIEW);
        expect(result).toEqual(LADDER_DISCOUNT);
    });

    it('TableDiscountView', () => {
        const result = prepareCashbackMoneyValue(TABLE_DISCOUNT_VIEW);
        expect(result).toEqual(TABLE_DISCOUNT);
    });
});

describe('prepareCashbackMoneyModel', () => {
    it('FlatDiscountView', () => {
        const result = prepareCashbackMoneyModel(FLAT_DISCOUNT);
        expect(result).toEqual(FLAT_DISCOUNT_VIEW);
    });

    it('LadderDiscountView', () => {
        const result = prepareCashbackMoneyModel(LADDER_DISCOUNT);
        expect(result).toEqual(LADDER_DISCOUNT_VIEW);
    });

    it('TableDiscountView', () => {
        const result = prepareCashbackMoneyModel(TABLE_DISCOUNT);
        expect(result).toEqual(TABLE_DISCOUNT_VIEW);
    });
});

describe('makeRidesParams', () => {
    it('Заполненная модель', () => {
        const result = makeRidesParams([
            {
                max_count: 34,
                interval: {
                    count: 18000,
                    type: 'last_seconds',
                },
            },
        ]);
        expect(result).toEqual({
            ridesNum: '34',
            ridesInterval: '18000',
            ridesIntervalType: RidesIntervalType.Seconds,
        });
    });

    it('Пустая модель', () => {
        const result = makeRidesParams(undefined);
        expect(result).toEqual({
            ridesNum: '',
            ridesInterval: '',
            ridesIntervalType: '',
        });
    });
});

describe('makeNoviceMeta', () => {
    it('Заполненная модель', () => {
        const result = makeNoviceMeta([
            {
                allowed_trips_count: {
                    start: 4,
                    end: 5,
                },
                brand: 'br',
                payment_type: 'pay',
                tariff_class: 'econ',
            },
        ]);
        expect(result).toEqual({
            brand: 'br',
            paymentType: 'pay',
            minTripsCount: '4',
            maxTripsCount: '5',
            tariffClass: 'econ',
        });
    });

    it('Пустая модель', () => {
        const result = makeNoviceMeta(undefined);
        expect(result).toEqual({
            brand: '',
            paymentType: '',
            minTripsCount: '',
            maxTripsCount: '',
            tariffClass: '',
        });
    });
});

describe('prepareBudgetModel', () => {
    it('Заполненные лимиты', () => {
        const result = prepareBudgetModel({
            id: '_id',
            daily_limit: {
                value: '1',
                threshold: 200,
            },
            weekly_limit: {
                value: '7',
                threshold: 120,
                type: WeeklyLimitType.Sliding,
            },
        });
        expect(result).toEqual({
            dailyValue: '1',
            dailyThreshold: '200',
            weeklyValue: '7',
            weeklyThreshold: '120',
            trackWeeklyBudget: true,
            manuallyEnterDaily: false,
        });
    });

    it('Пустые лимиты', () => {
        const result = prepareBudgetModel(undefined);
        expect(result).toEqual(makeBudgetModel());
    });

    it('Использован ручной ввод дневного лимита', () => {
        const result = prepareBudgetModel({
            id: '_id',
            daily_limit: {
                value: '23',
                threshold: 200,
            },
            weekly_limit: {
                value: '18',
                threshold: 120,
                type: WeeklyLimitType.Sliding,
            },
        });
        expect(result).toEqual({
            dailyValue: '23',
            dailyThreshold: '200',
            weeklyValue: '18',
            weeklyThreshold: '120',
            trackWeeklyBudget: true,
            manuallyEnterDaily: true,
        });
    });
});
