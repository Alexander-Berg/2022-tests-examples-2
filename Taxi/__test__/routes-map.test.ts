import {findRouteMatch} from '../routes-map';

const routesMap = {
    '/cities': 'geo',
    '/discounts2/users': 'efficiency',
    '/tariff': 'monetization',
    '/tariff-settings': 'monetization',
};

describe('routes-map/findRouteMatch', () => {
    test('exact match', () => {
        const match = findRouteMatch(routesMap, '/cities');
        expect(match).toBe('/cities');
    });

    test('starts with', () => {
        const match = findRouteMatch(routesMap, '/cities/moscow/edit');
        expect(match).toBe('/cities');
    });

    test('different sub urls', () => {
        const match = findRouteMatch(routesMap, '/discounts2/yaplus');
        expect(match).toBe('/discounts2/users');
    });

    test('partly matched', () => {
        const match = findRouteMatch(routesMap, '/tariff-settings');
        expect(match).toBe('/tariff-settings');
    });
});
