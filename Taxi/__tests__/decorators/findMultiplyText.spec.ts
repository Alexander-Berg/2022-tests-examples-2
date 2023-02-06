import {somePage} from '../mock/page';

describe('Тестирование findMultiplyText', () => {
    test('должен вернуть массив указанного ID с префиксами', async () => {
        expect(typeof somePage.findText_1).toBe('object');
        expect(somePage.findText_1 instanceof Promise).toBe(true);

        expect(await somePage.findText_1)
            .toBe('prefix_test_test_result');
    });
});
