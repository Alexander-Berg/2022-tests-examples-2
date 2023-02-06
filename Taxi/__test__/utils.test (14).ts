import {TariffClass} from '../../types';
import {makeNewTariffClass} from '../utils';

describe('Tariff class utils tests', () => {
    test('Функция для создания нового тарифного класса', () => {
        const NEW_NAME = 'some_id';
        const IS_CORP_TARIFF = true;
        const TARIFF_CLASS: TariffClass = {
            intervals: [{category_type: 'alo'} as any],
            name: 'some tariff',
            inherited: true
        };
        const newClass = makeNewTariffClass(IS_CORP_TARIFF, TARIFF_CLASS, NEW_NAME);

        expect(newClass.name).toBe(NEW_NAME);
        expect(newClass.intervals).toHaveLength(0);
        expect(newClass.inherited).toBe(false);
    });
});
