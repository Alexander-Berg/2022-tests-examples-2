import {stringToUrlItem, transformTextWithUrl, UrlItem, UrlMapper} from '../transformTextWithUrl';

const REPLACED_VALUE = 'URL';
const customUrlMapper: UrlMapper = ({value, isUrl}: UrlItem) => (isUrl ? REPLACED_VALUE : value);

describe('utils/getTextWithClickableUrl', () => {
    test('Регулярка корректно определяет https url', () => {
        expect(stringToUrlItem('https://yandex.ru/legal/rules').isUrl).toBe(true);
        expect(stringToUrlItem('https://yandex.ru/').isUrl).toBe(true);
        expect(stringToUrlItem('https://yandex.ru').isUrl).toBe(true);
        expect(stringToUrlItem('https://www.yandex.ru/legal/rules').isUrl).toBe(true);
        expect(stringToUrlItem('https://www.yandex.ru/').isUrl).toBe(true);
        expect(stringToUrlItem('https://www.yandex.ru').isUrl).toBe(true);
        expect(stringToUrlItem('https://t.me/joinchat/chat_id').isUrl).toBe(true);
    });

    test('Регулярка корректно определяет http url', () => {
        expect(stringToUrlItem('http://yandex.ru/legal/rules').isUrl).toBe(true);
        expect(stringToUrlItem('http://yandex.ru/').isUrl).toBe(true);
        expect(stringToUrlItem('http://yandex.ru').isUrl).toBe(true);
        expect(stringToUrlItem('http://www.yandex.ru/legal/rules').isUrl).toBe(true);
        expect(stringToUrlItem('http://www.yandex.ru/').isUrl).toBe(true);
        expect(stringToUrlItem('http://www.yandex.ru').isUrl).toBe(true);
        expect(stringToUrlItem('http://t.me/joinchat/chat_id').isUrl).toBe(true);
    });

    test('Регулярка корректно работает с параметрами', () => {
        expect(stringToUrlItem('https://yandex.ru/legal/rules/?a=1&b=1970').isUrl).toBe(true);
        expect(stringToUrlItem('http://yandex.ru/legal/rules/?a=1&b=1970').isUrl).toBe(true);
        expect(stringToUrlItem('https://www.yandex.ru/legal/rules/?a=1&b=1970').isUrl).toBe(true);
        expect(stringToUrlItem('http://www.yandex.ru/legal/rules/?a=1&b=1970').isUrl).toBe(true);

        expect(stringToUrlItem('https://yandex.ru/?a=1&b=1970').isUrl).toBe(true);
        expect(stringToUrlItem('http://yandex.ru/?a=1&b=1970').isUrl).toBe(true);
        expect(stringToUrlItem('https://www.yandex.ru/?a=1&b=1970').isUrl).toBe(true);
        expect(stringToUrlItem('http://www.yandex.ru/?a=1&b=1970').isUrl).toBe(true);

        expect(stringToUrlItem('https://yandex.ru?a=1&b=1970').isUrl).toBe(true);
        expect(stringToUrlItem('http://yandex.ru?a=1&b=1970').isUrl).toBe(true);
        expect(stringToUrlItem('https://www.yandex.ru?a=1&b=1970').isUrl).toBe(true);
        expect(stringToUrlItem('http://www.yandex.ru?a=1&b=1970').isUrl).toBe(true);
    });

    test('Регулярка корректно работает с якорем', () => {
        expect(stringToUrlItem('https://yandex.ru#hello_world').isUrl).toBe(true);
        expect(stringToUrlItem('http://yandex.ru#hello_world').isUrl).toBe(true);
        expect(stringToUrlItem('https://yandex.ru/#hello_world').isUrl).toBe(true);
        expect(stringToUrlItem('http://yandex.ru/#hello_world').isUrl).toBe(true);

        expect(stringToUrlItem('https://yandex.ru/legal/rules#hello_world').isUrl).toBe(true);
        expect(stringToUrlItem('http://yandex.ru/legal/rules#hello_world').isUrl).toBe(true);
        expect(stringToUrlItem('https://yandex.ru/legal/rules/#hello_world').isUrl).toBe(true);
        expect(stringToUrlItem('http://yandex.ru/legal/rules/#hello_world').isUrl).toBe(true);
    });

    test('Регулярка корректно работает с параметрами и якорем', () => {
        expect(stringToUrlItem('https://yandex.ru?a=1&b=1970#hello_world').isUrl).toBe(true);
        expect(stringToUrlItem('http://yandex.ru?a=1&b=1970#hello_world').isUrl).toBe(true);

        expect(stringToUrlItem('https://yandex.ru/legal/rules?a=1&b=1970#hello_world').isUrl).toBe(true);
        expect(stringToUrlItem('http://yandex.ru/legal/rules?a=1&b=1970#hello_world').isUrl).toBe(true);
    });

    test('Корректно заменяет url', () => {
        const url = 'https://yandex.ru/legal/rules';

        const text = `Пользовательское соглашение сервисов Яндекса: ${url}/. Перечень Служб Такси доступен по адресу ${url}.`;
        const transformResult = [
            'Пользовательское соглашение сервисов Яндекса: ',
            REPLACED_VALUE,
            '. Перечень Служб Такси доступен по адресу ',
            REPLACED_VALUE,
            '.'
        ];

        expect(transformTextWithUrl(text, customUrlMapper)).toMatchObject(transformResult);
    });
});
