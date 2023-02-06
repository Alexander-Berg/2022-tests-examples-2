import {ScriptLoader} from '_pkg/utils/scriptLoader';

describe('utils/scriptLoader', () => {
    test('Повторный запрос скрипта не добавляет его в дом еще раз', () => {
        const url = 'http://localhost/url';
        const scriptLoader = new ScriptLoader();

        scriptLoader.load(url);
        scriptLoader.load(url);
        const scripts = document.body.getElementsByTagName('script');

        let count = 0;

        Object.keys(scripts).forEach(id => {
            if (scripts[id].src === url) {
                count++;
            }
        });

        expect(count).toBe(1);
    });
});
