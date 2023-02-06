import {somePage} from '../mock/page';

describe('Тестирование findElement', () => {
    test('должен вернуть указанный ID с префиксом', async () => {
        expect(typeof somePage.findElement_1).toBe('object');
        expect(somePage.findElement_1 instanceof Promise).toBe(true);
        expect(await somePage.findElement_1)
            .toBe('prefix_#simplePattern_1_even');
    });

    test('должен вернуть только префикс', async () => {
        expect(typeof somePage.findElement_2).toBe('object');
        expect(somePage.findElement_2 instanceof Promise).toBe(true);
        expect(await somePage.findElement_2)
            .toBe('prefix_');
    });
});
