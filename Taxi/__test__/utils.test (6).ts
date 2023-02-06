import {OrderApplications} from '../consts';
import {calcCostByThreshold, getAppNameByStatApp} from '../utils';

const APPLICATIONS = {
    uber: 'uber_android',
    rutaxi: 'rutaxi_android',
    uberKz: 'uber_kz_iphone'
};

describe('utils/getAppNameByStatApp', () => {
    test('detect UberKz', () => {
        const appType = getAppNameByStatApp(APPLICATIONS.uberKz);
        expect(appType).toEqual(OrderApplications.UberKz);
    });
    test('detect UberRussia', () => {
        const appType = getAppNameByStatApp(APPLICATIONS.uber);
        expect(appType).toEqual(OrderApplications.UberRussia);
    });
});

describe('utils/calcCostByThreshold', () => {
    test('Корректно округляет стоимость до целого', () => {
        expect(calcCostByThreshold(0.99, 1)).toBe(1);
        expect(calcCostByThreshold(1.01, 1)).toBe(2);
    });

    test('Корректно округляет стоимость до десятых', () => {
        expect(calcCostByThreshold(1.89, 0.1)).toBe(1.9);
        expect(calcCostByThreshold(1.99, 0.1)).toBe(2);
    });

    test('Корректно округляет стоимость до сотых', () => {
        expect(calcCostByThreshold(0.001, 0.01)).toBe(0.01);
        expect(calcCostByThreshold(1.999, 0.01)).toBe(2);
    });

    test('Корректно округляет стоимость до ближайшей сотни', () => {
        expect(calcCostByThreshold(99, 100)).toBe(100);
        expect(calcCostByThreshold(101, 100)).toBe(200);
    });

    test('Корректно округляет стоимость с произвольным шагом', () => {
        expect(calcCostByThreshold(100.45, 0.5)).toBe(100.5);
        expect(calcCostByThreshold(100.51, 0.5)).toBe(101);

        expect(calcCostByThreshold(100.18, 0.2)).toBe(100.2);
        expect(calcCostByThreshold(100.21, 0.2)).toBe(100.4);
    });
});
