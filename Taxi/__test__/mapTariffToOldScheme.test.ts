import cloneDeep from 'lodash/cloneDeep';

import {Tariff} from '../../../types';
import mapTariffToOldScheme from '../mapTariffToOldScheme';
import {NEW_TARIFF, POLICY} from './const';

describe('mapTariffToOldScheme', () => {
    const INITIAL_TARIFF = cloneDeep(NEW_TARIFF);
    const newTariff: Tariff = mapTariffToOldScheme(NEW_TARIFF);
    const oldTariff: Tariff = mapTariffToOldScheme({...NEW_TARIFF, mapped_from_old_scheme: true});

    test('Проверем правильность мапинга нового тарифа для апдейта', () => {
        expect(newTariff).not.toHaveProperty('categories');
        expect(newTariff.classes?.[0].intervals).toHaveLength(2);

        // у inherited=true класса не должно быть интервалов
        expect(newTariff.classes?.[1]).not.toHaveProperty('intervals');
    });

    test('Проверем правильность мапинга старого тарифа для апдейта', () => {
        expect(oldTariff).toHaveProperty('categories');
        expect(oldTariff.categories).toHaveLength(4);

        expect(oldTariff.categories).not.toHaveProperty('category_index');

        expect(oldTariff).toHaveProperty('policy');
        expect(oldTariff.policy).toEqual(POLICY);
    });

    test('Проверяем что функция иммутабельна', () => {
        expect(newTariff).not.toBe(NEW_TARIFF);
        expect(NEW_TARIFF).toEqual(INITIAL_TARIFF);
    });
});
