import cloneDeep from 'lodash/cloneDeep';

import mapTariffToNewScheme from '../mapTariffToNewScheme';
import {CATEGORY_NAME_1, CATEGORY_NAME_2, NEW_TARIFF, OLD_TARIFF} from './const';

describe('mapTariffToNewScheme', () => {
    const INITIAL_TARIFF = cloneDeep(OLD_TARIFF);
    const tariff = mapTariffToNewScheme(OLD_TARIFF);
    const tariff2 = mapTariffToNewScheme({...OLD_TARIFF, inherited: true});
    const tariff3 = mapTariffToNewScheme(NEW_TARIFF);

    test('Проверем наличие кастомного флага', () => {
        expect(tariff).toHaveProperty('mapped_from_old_scheme');
        expect(tariff.mapped_from_old_scheme).toBe(true);
    });

    test('Проверем наличие основных полей в классах', () => {
        expect(tariff).toHaveProperty('classes');

        tariff.classes?.forEach(({inherited, policy, name, intervals}) => {
            expect(inherited).toBe(OLD_TARIFF.inherited);
            expect(policy).toEqual(OLD_TARIFF.policy);
            expect(name).toBeDefined();
            expect(intervals).toBeDefined();

            intervals?.forEach(interval => {
                expect(interval).toHaveProperty('category_index');
            });
        });
    });

    test('Проверем правильность схлапывания категорий в классы', () => {
        expect(tariff.classes).toHaveLength(2);

        expect(tariff.classes?.[0].name).toBe(CATEGORY_NAME_1);
        expect(tariff.classes?.[0].intervals).toHaveLength(2);

        expect(tariff.classes?.[1].name).toBe(CATEGORY_NAME_2);
    });

    test('Проверем классы у наследуемого тарифа', () => {
        expect(tariff2.classes).toHaveLength(0);
    });

    test('Новый тариф не мапим. Его просто возвращаем.', () => {
        expect(tariff3).toBe(NEW_TARIFF);
    });

    test('Проверяем что функция иммутабельна', () => {
        expect(tariff).not.toBe(OLD_TARIFF);
        expect(OLD_TARIFF).toEqual(INITIAL_TARIFF);
    });
});
