import {somePage} from '../mock/page';

describe('Тестирование findByData', () => {
    test('должен вернуть указанный ID с префиксом data-cy', async () => {
        expect(typeof somePage.findByData_1).toBe('object');
        expect(somePage.findByData_1 instanceof Promise).toBe(true);
        expect(await somePage.findByData_1)
            .toBe('prefix_[data-cy=\'schedules-card-card_picker-complexity_simple-button-create\']');
    });
});
