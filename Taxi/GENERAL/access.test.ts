import {CityGeoId} from 'tests/unit/types';

import {FEATURE_ACCESS_DEFAULT, FEATURE_ACCESS_FULL, FEATURE_ACCESS_NONE} from 'constants/idm';
import {AnalystEntity} from 'types/analyst';

import {formatCityFeatureAccess} from './access';

describe('formatCityFeatureAccess()', () => {
    const city = {
        id: CityGeoId.MOSCOW,
        region: {
            isoCode: 'RU'
        }
    };

    it('should resolve to full access if availableRegionsAndCities has full access to this city only', () => {
        const featureAccess = formatCityFeatureAccess(city, {
            regions: {
                RU: {
                    isoCode: city.region.isoCode,
                    allCitiesAvailable: false,
                    featureAccess: FEATURE_ACCESS_NONE,
                    cities: {[CityGeoId.MOSCOW]: {cityGeoId: CityGeoId.MOSCOW, featureAccess: FEATURE_ACCESS_FULL}}
                }
            },
            featureAccess: FEATURE_ACCESS_NONE,
            allRegionsAvailable: false
        });
        expect(featureAccess).toEqual(FEATURE_ACCESS_FULL);
    });

    it('should resolve to full access if availableRegionsAndCities has full access to this region only', () => {
        const featureAccess = formatCityFeatureAccess(city, {
            regions: {
                RU: {
                    isoCode: city.region.isoCode,
                    allCitiesAvailable: true,
                    featureAccess: FEATURE_ACCESS_FULL,
                    cities: {}
                }
            },
            featureAccess: FEATURE_ACCESS_NONE,
            allRegionsAvailable: false
        });
        expect(featureAccess).toEqual(FEATURE_ACCESS_FULL);
    });

    it('should resolve to full access if availableRegionsAndCities has global full access only', () => {
        const featureAccess = formatCityFeatureAccess(city, {
            regions: {},
            featureAccess: FEATURE_ACCESS_FULL,
            allRegionsAvailable: true
        });
        expect(featureAccess).toEqual(FEATURE_ACCESS_FULL);
    });

    it(
        'should resolve to combined partial access ' +
            "if availableRegionsAndCities has distinct partial access' on different levels",
        () => {
            const featureAccess = formatCityFeatureAccess(city, {
                regions: {
                    RU: {
                        isoCode: city.region.isoCode,
                        allCitiesAvailable: true,
                        featureAccess: {...FEATURE_ACCESS_NONE, socdem_c1c2Res: true},
                        cities: {
                            [CityGeoId.MOSCOW]: {
                                cityGeoId: CityGeoId.MOSCOW,
                                featureAccess: {...FEATURE_ACCESS_NONE, socdem_isochrone_c1c2_res: true}
                            }
                        }
                    }
                },
                featureAccess: {...FEATURE_ACCESS_NONE, export: true},
                allRegionsAvailable: true
            });
            expect(featureAccess).toEqual({
                ...FEATURE_ACCESS_NONE,
                export: true,
                socdem_isochrone_c1c2_res: true,
                socdem_c1c2Res: true
            });
        }
    );

    it(
        'should resolve to full access if ' +
            'availableRegionsAndCities has global full access and local partial access',
        () => {
            const featureAccess = formatCityFeatureAccess(city, {
                regions: {
                    RU: {
                        isoCode: city.region.isoCode,
                        allCitiesAvailable: false,
                        featureAccess: FEATURE_ACCESS_NONE,
                        cities: {
                            [CityGeoId.MOSCOW]: {cityGeoId: CityGeoId.MOSCOW, featureAccess: FEATURE_ACCESS_DEFAULT}
                        }
                    }
                },
                featureAccess: FEATURE_ACCESS_FULL,
                allRegionsAvailable: true
            });
            expect(featureAccess).toEqual(FEATURE_ACCESS_FULL);
        }
    );

    it('should resolve to none access if availableRegionsAndCities has access to different city only', () => {
        const featureAccess = formatCityFeatureAccess(city, {
            regions: {
                RU: {
                    isoCode: city.region.isoCode,
                    allCitiesAvailable: false,
                    featureAccess: FEATURE_ACCESS_NONE,
                    cities: {
                        [CityGeoId.SPB]: {
                            cityGeoId: CityGeoId.SPB,
                            featureAccess: {...FEATURE_ACCESS_NONE, socdem_isochrone_c1c2_res: true}
                        }
                    }
                }
            },
            featureAccess: FEATURE_ACCESS_NONE,
            allRegionsAvailable: false
        });
        expect(featureAccess).toEqual(FEATURE_ACCESS_NONE);
    });

    it('should resolve to custom access if availableRegionsAndCities has only this custom access', () => {
        const customFields = {
            ...FEATURE_ACCESS_NONE,
            [AnalystEntity.SOCDEM_C1C2RES]: false,
            [AnalystEntity.SOCDEM_TTL_RESIDENTS_REAL]: false,
            [AnalystEntity.EDA_ORDERS_COUNT]: true,
            [AnalystEntity.EDA_ORDERS_AVG_PRICE]: true,
            [AnalystEntity.LAVKA_ORDERS_COUNT]: true,
            [AnalystEntity.LAVKA_ORDERS_AVG_PRICE]: true
        };
        const featureAccess = formatCityFeatureAccess(city, {
            regions: {
                RU: {
                    cities: {
                        [CityGeoId.MOSCOW]: {cityGeoId: CityGeoId.MOSCOW, featureAccess: customFields}
                    },
                    isoCode: 'RU',
                    allCitiesAvailable: false,
                    featureAccess: FEATURE_ACCESS_NONE
                }
            },
            featureAccess: FEATURE_ACCESS_NONE,
            allRegionsAvailable: false
        });
        expect(featureAccess).toEqual(customFields);
    });
});
