import {CategoryOrigin, TariffClass, TariffOrigin} from '../../../types';

export const CATEGORY_NAME_1 = 'some_category';
export const CATEGORY_NAME_2 = 'another_category';

const CATEGORY: CategoryOrigin = {
    category_name: CATEGORY_NAME_1,
    category_type: 'application',
    time_from: '123',
    time_to: '123',
    name_key: 'alo',
    day_type: 0,
    currency: 'RUB',
    included_one_of: [],
    minimal: 1,
    paid_cancel_fix: 0,
    add_minimal_to_paid_cancel: true,
    meters: [],
    special_taximeters: [],
    zonal_prices: []
};

export const POLICY: TariffOrigin['policy'] = {
    multiplier: 1,
    category: null,
    transfer: null
};

export const OLD_TARIFF: TariffOrigin = {
    home_zone: 'moscow',
    country: 'rus',
    name: 'some_tariff',
    tariff_series_id: 'id1',
    usage_count: 0,
    inherited: false,
    categories: [
        CATEGORY,
        {...CATEGORY, category_type: 'call_center'},
        {...CATEGORY, category_name: CATEGORY_NAME_2}
    ],
    policy: POLICY
};

const CLASS_ITEM: TariffClass = {
    policy: POLICY,
    name: CATEGORY_NAME_1,
    inherited: false,
    intervals: [CATEGORY, CATEGORY]
};

export const NEW_TARIFF: TariffOrigin = {
    home_zone: 'moscow',
    country: 'rus',
    name: 'some_tariff',
    tariff_series_id: 'id1',
    usage_count: 0,
    classes: [CLASS_ITEM, {...CLASS_ITEM, inherited: true}],
    categories: [],
};
