import {somePage} from '../mock/page';

describe('Тестирование findMultipleElements', () => {
    test('должен вернуть массив указанного ID с префиксами', async () => {
        expect(typeof somePage.findMultiplyText_1).toBe('object');
        expect(somePage.findMultiplyText_1 instanceof Promise).toBe(true);
        expect(await somePage.findMultiplyText_1)
            .toStrictEqual([
                'prefix_2_#simplePattern_1_even_result',
                'prefix_1_#simplePattern_1_even_result',
            ]);
    });
});
