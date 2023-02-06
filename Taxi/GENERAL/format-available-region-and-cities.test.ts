import {CityGeoId} from 'tests/unit/types';

import {FEATURE_ACCESS_DEFAULT, FEATURE_ACCESS_FULL, FEATURE_ACCESS_NONE} from 'constants/idm';
import {formatAvailableRegionsAndCities} from 'server/utils/format-available-region-and-cities';
import {AnalystEntity} from 'types/analyst';
import {IdmPathRole, Role} from 'types/idm';

describe('formatAvailableRegionsAndCities()', () => {
    it('should format global access object given global FULL_ACCESS role', () => {
        const idmPath: IdmPathRole = {
            path: `project.group.role.${Role.FULL_ACCESS}`,
            uid: '666',
            fields: {}
        };

        const result = formatAvailableRegionsAndCities([idmPath]);
        expect(result).toEqual({
            regions: {},
            featureAccess: FEATURE_ACCESS_FULL,
            allRegionsAvailable: true
        });
    });

    it('should format access object given RU/Moscow FULL_ACCESS role', () => {
        const cityGeoId = CityGeoId.MOSCOW;
        const region = 'RU';
        const idmPath = {
            path: `project.path.country.${region}.access.${cityGeoId}.access_city.all.role.${Role.FULL_ACCESS}`,
            uid: '666',
            fields: {}
        };

        const result = formatAvailableRegionsAndCities([idmPath]);
        expect(result).toEqual({
            regions: {
                RU: {
                    cities: {[CityGeoId.MOSCOW]: {cityGeoId, featureAccess: FEATURE_ACCESS_FULL}},
                    isoCode: 'RU',
                    allCitiesAvailable: false,
                    featureAccess: FEATURE_ACCESS_NONE
                }
            },
            featureAccess: FEATURE_ACCESS_NONE,
            allRegionsAvailable: false
        });
    });

    it('should format access object given FULL_ACCESS role in RU', () => {
        const region = 'RU';
        const idmPath = {
            path: `project.path.country.${region}.access.all.role.${Role.FULL_ACCESS}`,
            uid: '666',
            fields: {}
        };

        const result = formatAvailableRegionsAndCities([idmPath]);
        expect(result).toEqual({
            regions: {
                RU: {
                    cities: {},
                    isoCode: 'RU',
                    allCitiesAvailable: true,
                    featureAccess: FEATURE_ACCESS_FULL
                }
            },
            featureAccess: FEATURE_ACCESS_NONE,
            allRegionsAvailable: false
        });
    });

    it('should format access object given combined MANAGER and FULL_ACCESS roles on different levels', () => {
        const result = formatAvailableRegionsAndCities([
            {
                path: `project.path.country.RU.access.all.role.${Role.FULL_ACCESS}`,
                uid: '666',
                fields: {}
            },
            {
                path: `project.group.role.${Role.MANAGER}`,
                uid: '666',
                fields: FEATURE_ACCESS_DEFAULT
            },
            {
                path: `project.path.country.RU.access.${CityGeoId.MOSCOW}.access_city.all.role.${Role.MANAGER}`,
                uid: '666',
                fields: FEATURE_ACCESS_DEFAULT
            }
        ]);
        expect(result).toEqual({
            regions: {
                RU: {
                    cities: {[CityGeoId.MOSCOW]: {cityGeoId: CityGeoId.MOSCOW, featureAccess: FEATURE_ACCESS_DEFAULT}},
                    isoCode: 'RU',
                    allCitiesAvailable: true,
                    featureAccess: FEATURE_ACCESS_FULL
                }
            },
            featureAccess: FEATURE_ACCESS_DEFAULT,
            allRegionsAvailable: true
        });
    });

    it('should format access object given combined FULL_ACCESS in different cities', () => {
        const result = formatAvailableRegionsAndCities([
            {
                path: `project.path.country.RU.access.${CityGeoId.SPB}.access_city.all.role.${Role.FULL_ACCESS}`,
                uid: '666',
                fields: {}
            },
            {
                path: `project.path.country.RU.access.${CityGeoId.MOSCOW}.access_city.all.role.${Role.FULL_ACCESS}`,
                uid: '666',
                fields: {}
            }
        ]);
        expect(result).toEqual({
            regions: {
                RU: {
                    cities: {
                        [CityGeoId.MOSCOW]: {cityGeoId: CityGeoId.MOSCOW, featureAccess: FEATURE_ACCESS_FULL},
                        [CityGeoId.SPB]: {cityGeoId: CityGeoId.SPB, featureAccess: FEATURE_ACCESS_FULL}
                    },
                    isoCode: 'RU',
                    allCitiesAvailable: false,
                    featureAccess: FEATURE_ACCESS_NONE
                }
            },
            featureAccess: FEATURE_ACCESS_NONE,
            allRegionsAvailable: false
        });
    });

    it('should format access object given custom partial access', () => {
        const customFields = {
            [AnalystEntity.SOCDEM_C1C2RES]: false,
            [AnalystEntity.SOCDEM_TTL_RESIDENTS_REAL]: false,
            [AnalystEntity.EDA_ORDERS_COUNT]: true,
            [AnalystEntity.EDA_ORDERS_AVG_PRICE]: true,
            [AnalystEntity.LAVKA_ORDERS_COUNT]: true,
            [AnalystEntity.LAVKA_ORDERS_AVG_PRICE]: true
        };
        const result = formatAvailableRegionsAndCities([
            {
                path: `project.path.country.RU.access.${CityGeoId.SPB}.access_city.all.role.${Role.MANAGER}`,
                uid: '666',
                fields: customFields
            }
        ]);
        expect(result).toEqual({
            regions: {
                RU: {
                    cities: {
                        [CityGeoId.SPB]: {
                            cityGeoId: CityGeoId.SPB,
                            featureAccess: {...FEATURE_ACCESS_DEFAULT, ...customFields}
                        }
                    },
                    isoCode: 'RU',
                    allCitiesAvailable: false,
                    featureAccess: FEATURE_ACCESS_NONE
                }
            },
            featureAccess: FEATURE_ACCESS_NONE,
            allRegionsAvailable: false
        });
    });
});
