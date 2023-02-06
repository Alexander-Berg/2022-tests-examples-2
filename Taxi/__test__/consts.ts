import moment from 'moment';

import {ActiveDayType, CalculationMethod, DiscountTarget, ZoneType} from '../../enums';
import {
    ActiveLocalHours,
    DatetimeParams,
    DatetimeParamsView,
    Discount,
    DiscountViewModel,
    ExtendZoneList,
    SaveDiscountRequest,
    Schedules,
    ScheduleView,
    TimeInterval,
    ZoneViewModel
} from '../../types';

export const ACTIVE_LOCAL_HOURS_LIST: ActiveLocalHours[] = [
    {from_time: '12:50', to_time: '13:49'},
];

export const SCHEDULE_VIEW_LIST: ScheduleView[] = [
    {days: [1, 4, 6], from: '12:45', to: '14:13'},
];

export const DATETIME_PARAMS_VIEW: DatetimeParamsView = {
    date_from: moment('2019-10-01'),
    date_from_time: '15:55',
    date_to: moment('2020-03-03'),
    date_to_time: '12:10',
    active_day_type: ActiveDayType.Everyday,
    timezone_type: 'utc',
};

export const DEFAULT_DISCOUNT_MODEL: ExtendZoneList<DiscountViewModel> = {
    discount_class: 'class',
    description: 'desc',
    discount_method: 'full',
    zones_list: ['br_abakan'],
    discount_series_id: '56',
    driver_less_coeff: '89' as any as number,
    enabled: true,
    select_params: {
        discount_target: DiscountTarget.All,
        classes: ['join'],
        datetime_params: DATETIME_PARAMS_VIEW,
    },
    calculation_params: {
        round_digits: '0' as any as number,
        calculation_method: CalculationMethod.Formula,
        min_value: '8' as any as number,
        max_value: '8' as any as number,
        max_absolute_value: '8' as any as number,
        newbie_max_coeff: '8' as any as number,
        newbie_num_coeff: '8' as any as number,
        discount_calculator: {
            calculation_formula_v1_a1: '4' as any as number,
            calculation_formula_v1_a2: '4' as any as number,
            calculation_formula_v1_p1: '45' as any as number,
            calculation_formula_v1_p2: '4' as any as number,
            calculation_formula_v1_c1: '4' as any as number,
            calculation_formula_v1_c2: '4' as any as number,
            calculation_formula_v1_threshold: '667' as any as number,
        },
    },
    $view: {},
};

export const ZONES_LIST = [5];

export const TIME_INTERVAL_LIST: TimeInterval[] = [
    {
        from_time: {hour: 12, minute: 50},
        to_time: {hour: 13, minute: 49},
    },
];

export const SHEDULES: Schedules = [
    {
        timezone: 'utc',
        intervals: [
            {
                exclude: false,
                day: [1, 4, 6],
            },
            {
                exclude: false,
                daytime: [{
                    from: '12:45:00',
                    to: '14:13:00',
                }],
            },
        ],
    },
];

export const DATETIME_PARAMS: DatetimeParams = {
    date_from: '2019-10-01T15:55:00',
    date_to: '2020-03-03T12:10:00',
    timezone_type: 'utc',
    active_day_type: ActiveDayType.Everyday,
    active_local_hours: undefined,
    schedules: undefined,
};

export const DEFAULT_DISCOUNT: Discount = {
    discount_class: 'class',
    description: 'desc',
    discount_method: 'full',
    zones_list: [5],
    discount_series_id: '56',
    driver_less_coeff: 89,
    enabled: true,
    select_params: {
        discount_target: 'all',
        classes: ['join'],
        datetime_params: DATETIME_PARAMS,
        point_a_is_enough: false,
        bin_filter: undefined,
        disable_by_surge: undefined,
        geoarea: undefined,
        geoarea_a_list: undefined,
        geoarea_b_list: undefined,
        limited_rides_params: undefined,
        random_application_params: undefined,
        selected_user_tags: undefined,
        user_tags: undefined,
    },
    calculation_params: {
        round_digits: 0,
        calculation_method: 'calculation_formula',
        min_value: 8,
        max_value: 8,
        max_absolute_value: 8,
        newbie_max_coeff: 8,
        newbie_num_coeff: 8,
        discount_calculator: {
            calculation_formula_v1_a1: 4,
            calculation_formula_v1_a2: 4,
            calculation_formula_v1_p1: 45,
            calculation_formula_v1_p2: 4,
            calculation_formula_v1_c1: 4,
            calculation_formula_v1_c2: 4,
            calculation_formula_v1_threshold: 667,
        },
    },
};

export const SAVE_DISCOUNT_REQUEST: SaveDiscountRequest = {
    discount: DEFAULT_DISCOUNT,
    limits: undefined,
    zones_update_params: undefined,
};

export const DEFAULT_ZONE_VIEW_MODEL: ZoneViewModel = {
    discounts: [
        DEFAULT_DISCOUNT,
    ],
    zone_id: 4,
    zone_name: 'moscow',
    zone_type: ZoneType.Agglomeration,
    enabled: true,
    discounts_list: [
        {discount_series_id: '3'},
        {discount_series_id: 'df'},
        {discount_series_id: '3321'},
    ],
    subvention_start: moment('2019-10-10T15:30:10'),
    subvention_end: moment('2020-03-03T14:01:55'),
    $view: {},
};
