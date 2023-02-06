import {somePage} from '../mock/page';

describe('Тестирование findMultipleByData', () => {
    test('должен вернуть массив указанного ID с префиксами', async () => {
        expect(typeof somePage.findMultipleByData_1).toBe('object');
        expect(somePage.findMultipleByData_1 instanceof Promise).toBe(true);
        expect(await somePage.findMultipleByData_1)
            .toStrictEqual([
                'prefix_2_[data-cy=\'#simplePattern_1_even\']',
                'prefix_1_[data-cy=\'#simplePattern_1_even\']',
            ]);
    });
});
