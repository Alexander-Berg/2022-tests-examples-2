import {somePage} from '../mock/page';

describe('Тестирование findMultipleByText', () => {
    test('должен вернуть массив указанного ID с префиксами', async () => {
        expect(typeof somePage.findMultipleByText_1).toBe('object');
        expect(somePage.findMultipleByText_1 instanceof Promise).toBe(true);
        expect(await somePage.findMultipleByText_1)
            .toStrictEqual([
                'prefix_2_./*/*[text()=\'#simplePattern_1_even\']',
                'prefix_1_./*/*[text()=\'#simplePattern_1_even\']',
            ]);
    });
});
