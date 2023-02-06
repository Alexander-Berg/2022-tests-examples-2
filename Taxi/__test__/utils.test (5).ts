import {ROUTE} from '../consts';
import {createUrl} from '../utils';

describe('Проверка функции createUrl', () => {
    it('Формирование url без мода и имени', () => {
        expect(createUrl('taxi')).toEqual(`${ROUTE}/taxi`);
    });
    it('Формирование url с модом и без имени', () => {
        expect(createUrl('taxi', 'new')).toEqual(`${ROUTE}/taxi/new`);
        expect(createUrl('eda', 'new')).toEqual(`${ROUTE}/eda/new`);
    });
    it('Формирование url с модом и именем', () => {
        expect(createUrl('taxi', 'old', 'test_67')).toEqual(`${ROUTE}/taxi/old/test_67`);
        expect(createUrl('eda', 'old', 'test_67')).toEqual(`${ROUTE}/eda/old/test_67`);
    });
});
