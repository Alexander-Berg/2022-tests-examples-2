import {somePage} from '../mock/page';

describe('Тестирование findByText', () => {
    test('должен вернуть указанный ID с префиксом data-cy', async () => {
        expect(typeof somePage.findByText_1).toBe('object');
        expect(somePage.findByText_1 instanceof Promise).toBe(true);
        expect(await somePage.findByText_1)
            .toBe('prefix_./*/*[text()=\'test_test\']');
    });
});
