import {ActiveDayType, CalculationMethod, DiscountTarget, ZoneType} from '../../enums';

import {
    DiscountViewModel,
    LimitedRidesParams,
    RandomApplicationParams,
    SaveZoneRequest,
} from '../../types';
import {
    prepareActiveLocalHours,
    prepareDatetimeParams,
    prepareLimitedRidesParams,
    prepareRandomApplicationParams,
    prepareSchedules,
    preSaveDiscount,
    preSaveZone,
} from '../matchers';
import {
    ACTIVE_LOCAL_HOURS_LIST,
    DATETIME_PARAMS,
    DATETIME_PARAMS_VIEW,
    DEFAULT_DISCOUNT,
    DEFAULT_DISCOUNT_MODEL,
    DEFAULT_ZONE_VIEW_MODEL,
    SAVE_DISCOUNT_REQUEST,
    SCHEDULE_VIEW_LIST,
    SHEDULES,
    TIME_INTERVAL_LIST,
    ZONES_LIST
} from './consts';

describe('preSaveZone', () => {
    it('Корректное преобразование тарифной зоны', () => {
        const allZones: string[] = ['moscow', 'ekb'];

        const expectedValue: SaveZoneRequest = {
            discounts_list: [
                {discount_series_id: '56'},
            ],
            zone_id: 4,
            zone_name: 'moscow',
            zone_type: ZoneType.TariffZone,
            enabled: true,
        };

        expect(preSaveZone(DEFAULT_ZONE_VIEW_MODEL, allZones)).toEqual(expectedValue);
    });
});

describe('prepareActiveLocalHours', () => {
    it('Корректное преобразование active_local_hours', () => {
        expect(prepareActiveLocalHours(ACTIVE_LOCAL_HOURS_LIST, ActiveDayType.Everyday)).toEqual(TIME_INTERVAL_LIST);
    });

    it('Возвращает undefined при activeDayType = Schedules', () => {
        expect(prepareActiveLocalHours(ACTIVE_LOCAL_HOURS_LIST, ActiveDayType.Schedules)).toBeUndefined();
    });
});

describe('prepareSchedules', () => {
    it('Корректное преобразование временных интервалов', () => {
        expect(prepareSchedules('utc', SCHEDULE_VIEW_LIST)).toEqual(SHEDULES);
    });
});

describe('prepareDatetimeParams', () => {
    it('Корректное преобразование datetime_params', () => {
        expect(prepareDatetimeParams(DATETIME_PARAMS_VIEW)).toEqual(DATETIME_PARAMS);
    });
});

describe('prepareRandomApplicationParams', () => {
    it('Корректное преобразование random_application_params', () => {
        const model: RandomApplicationParams = {
            apply_randomly: true,
            discount_cache_ttl: '9' as any as number,
            random_probability: '8' as any as number,
            use_user_id: true,
        };

        expect(prepareRandomApplicationParams(model)).toEqual({
            apply_randomly: true,
            discount_cache_ttl: 9,
            random_probability: 8,
            use_user_id: true,
        });

        expect(prepareRandomApplicationParams({
            ...model,
            apply_randomly: false,
        })).toBeUndefined();
    });
});

describe('prepareLimitedRidesParams', () => {
    it('Корректное преобразование limited_rides_params', () => {
        const model: LimitedRidesParams = {
            num_rides_for_newbies: '9' as any as number,
            limited_rides: true,
            rides_num: '10' as any as number,
        };

        expect(prepareLimitedRidesParams(undefined)).toBeUndefined();
        expect(prepareLimitedRidesParams({})).toBeUndefined();
        expect(prepareLimitedRidesParams(model)).toEqual({
            num_rides_for_newbies: 9,
            limited_rides: true,
            rides_num: 10,
        });
    });
});

describe('preSaveDiscount', () => {
    it('Преобразование полей из корня модели', () => {
        expect(preSaveDiscount(DEFAULT_DISCOUNT_MODEL, ZONES_LIST)).toEqual(SAVE_DISCOUNT_REQUEST);
    });

    it('select_params.discount_target = All', () => {
        const modelForDiscountTarget: DiscountViewModel = {
            ...DEFAULT_DISCOUNT_MODEL,
            select_params: {
                ...DEFAULT_DISCOUNT_MODEL.select_params,
                user_tags: ['user1'],
                selected_user_tags: ['s_user1'],
            },
        };

        const resultAll = preSaveDiscount(modelForDiscountTarget);

        expect(resultAll.discount.select_params).toEqual({
            ...DEFAULT_DISCOUNT.select_params,
            discount_target: DiscountTarget.All,
        });

        const resultTagService = preSaveDiscount({
            ...modelForDiscountTarget,
            select_params: {
                ...modelForDiscountTarget.select_params,
                discount_target: DiscountTarget.TagService,
            }
        });

        expect(resultTagService.discount.select_params).toEqual({
            ...DEFAULT_DISCOUNT.select_params,
            discount_target: DiscountTarget.TagService,
            user_tags: ['user1'],
        });

        const resultSelected = preSaveDiscount({
            ...modelForDiscountTarget,
            select_params: {
                ...modelForDiscountTarget.select_params,
                discount_target: DiscountTarget.Selected,
            }
        });

        expect(resultSelected.discount.select_params).toEqual({
            ...DEFAULT_DISCOUNT.select_params,
            discount_target: DiscountTarget.Selected,
            selected_user_tags: ['s_user1'],
        });
    });

    it('select_params.disable_by_surge', () => {
        const modelWithSurgeEnabled: DiscountViewModel = {
            ...DEFAULT_DISCOUNT_MODEL,
            select_params: {
                ...DEFAULT_DISCOUNT_MODEL.select_params,
                disable_by_surge: '78' as any as number,
            },
            $view: {
                disable_by_surge_enabled: true,
            }
        };

        expect(preSaveDiscount(modelWithSurgeEnabled).discount.select_params).toEqual({
            ...DEFAULT_DISCOUNT.select_params,
            disable_by_surge: 78,
        });

        expect(preSaveDiscount({
            ...modelWithSurgeEnabled,
            $view: {},
        }).discount.select_params).toEqual(DEFAULT_DISCOUNT.select_params);
    });

    it('select_params.geoarea', () => {
        const modelWithGeoarea: DiscountViewModel = {
            ...DEFAULT_DISCOUNT_MODEL,
            select_params: {
                ...DEFAULT_DISCOUNT_MODEL.select_params,
                geoarea: 'geo',
            },
            $view: {
                geoarea_enabled: true,
            },
        };

        expect(preSaveDiscount(modelWithGeoarea).discount.select_params).toEqual({
            ...DEFAULT_DISCOUNT.select_params,
            geoarea: 'geo',
        });

        expect(preSaveDiscount({
            ...modelWithGeoarea,
            $view: {},
        }).discount.select_params).toEqual(DEFAULT_DISCOUNT.select_params);
    });

    it('select_params.geoarea_a_list, geoarea_b_list', () => {
        const modelWithGeoareasEnabled: DiscountViewModel = {
            ...DEFAULT_DISCOUNT_MODEL,
            select_params: {
                ...DEFAULT_DISCOUNT_MODEL.select_params,
                geoarea_a_list: 'a_geo',
                geoarea_b_list: ['b_geo'],
            },
            $view: {
                geoareas_enabled: true,
            },
        };

        expect(preSaveDiscount(modelWithGeoareasEnabled).discount.select_params).toEqual({
            ...DEFAULT_DISCOUNT.select_params,
            geoarea_a_list: undefined,
            geoarea_b_list: undefined,
        });

        expect(preSaveDiscount({
            ...modelWithGeoareasEnabled,
            select_params: {
                ...modelWithGeoareasEnabled.select_params,
                geoarea_a_b_relation: 'only_b',
            }
        }).discount.select_params).toEqual({
            ...DEFAULT_DISCOUNT.select_params,
            geoarea_a_list: undefined,
            geoarea_b_list: ['b_geo'],
            geoarea_a_b_relation: 'only_b',
        });

        expect(preSaveDiscount({
            ...modelWithGeoareasEnabled,
            select_params: {
                ...modelWithGeoareasEnabled.select_params,
                geoarea_a_b_relation: 'only_a',
            }
        }).discount.select_params).toEqual({
            ...DEFAULT_DISCOUNT.select_params,
            geoarea_a_list: ['a_geo'],
            geoarea_b_list: undefined,
            geoarea_a_b_relation: 'only_a',
        });
    });

    it('select_params.bin_filter', () => {
        expect(preSaveDiscount({
            ...DEFAULT_DISCOUNT_MODEL,
            select_params: {
                ...DEFAULT_DISCOUNT_MODEL.select_params,
                bin_filter: ' bin_1  \n bin_2  \n  ' as any as string[],
            },
        }).discount.select_params).toEqual({
            ...DEFAULT_DISCOUNT.select_params,
            bin_filter: ['bin_1', 'bin_2'],
        });

        expect(preSaveDiscount({
            ...DEFAULT_DISCOUNT_MODEL,
            select_params: {
                ...DEFAULT_DISCOUNT_MODEL.select_params,
                bin_filter: ['bin_1', 'bin_2'],
            },
        }).discount.select_params).toEqual({
            ...DEFAULT_DISCOUNT.select_params,
            bin_filter: ['bin_1', 'bin_2'],
        });
    });

    it('calculation_params.discount_calculator', () => {
        const model: DiscountViewModel = {
            ...DEFAULT_DISCOUNT_MODEL,
            calculation_params: {
                ...DEFAULT_DISCOUNT_MODEL.calculation_params,
                calculation_method: CalculationMethod.Formula,
            },
        };

        expect(preSaveDiscount(model).discount.calculation_params).toEqual(DEFAULT_DISCOUNT.calculation_params);

        expect(preSaveDiscount({
            ...model,
            $view: {formula_flat: true},
        }).discount.calculation_params.discount_calculator).toEqual({
            calculation_formula_v1_threshold: 667,
            calculation_formula_v1_p1: 45,
            calculation_formula_v1_p2: 45,
            calculation_formula_v1_a1: 0,
            calculation_formula_v1_a2: 0,
            calculation_formula_v1_c1: 1,
            calculation_formula_v1_c2: 1
        });

        expect(preSaveDiscount({
            ...model,
            calculation_params: {
                ...model.calculation_params,
                calculation_method: CalculationMethod.Table,
                discount_calculator: {
                    table: [{
                        cost: '67' as any as number,
                        discount: '67' as any as number,
                    }]
                },
            },
        }).discount.calculation_params.discount_calculator).toEqual({
            table: [{
                cost: 67,
                discount: 67,
            }]
        });
    });

    it('zones_update_params', () => {
        expect(preSaveDiscount({
            ...DEFAULT_DISCOUNT_MODEL,
            $view: {
                update_position: true,
                zone_list_position: 'first',
            },
        }).zones_update_params).toEqual({
            zone_list_position: 'first',
            update_only_new: false,
        });

        expect(preSaveDiscount({
            ...DEFAULT_DISCOUNT_MODEL,
            $view: {
                zone_list_position: 'first',
            },
        }).zones_update_params).toBeUndefined();
    });
});
