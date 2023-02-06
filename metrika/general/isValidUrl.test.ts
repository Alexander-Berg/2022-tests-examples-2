import { isValidUrl } from './isValidUrl';

describe('isValidUrl', () => {
    describe('Test cases with valid urls', () => {
        it('should return true, it check standard url with protocol https', () => {
            expect(isValidUrl('https://ya.ru')).toBeTruthy();
        });

        it('should return true, it check standard url without any protocols', () => {
            expect(isValidUrl('metrika.yandex.ru')).toBeTruthy();
        });

        it('should return true, it check long url with protocol https, and query params, going after /?', () => {
            expect(
                isValidUrl(
                    'https://st.yandex-team.ru/issues/?_q=%28Author%3A+shevmichael17%40+or+Assignee%3A+shevmichael17%40%29+and+Resolution%3A+empty%28%29',
                ),
            ).toBeTruthy();
        });

        it('should return true, it check standard url with protocol http', () => {
            expect(isValidUrl('http://st.yandex-team.ru/OFFICEAPPROV-25399')).toBeTruthy();
        });

        it('should return true, it check standard russian domain url without any protocols', () => {
            expect(isValidUrl('правительство.рф')).toBeTruthy();
        });

        it('should return true, it check standard russian domain url with protocol http, and query params going after ?', () => {
            expect(isValidUrl('http://майями.рф?utm=12kiu23')).toBeTruthy();
        });

        it('should return true, it check very long url with different query params', () => {
            expect(
                isValidUrl(
                    'https://test.metrika.yandex.ru/stat/new?metric=ym%3As%3ApageDepth&sort=-ym%3As%3ApageDepth&chart_type=line&period=week&table=visits&title=Глубина+просмотра&accuracy=1&id=67483357&stateHash=61cc711dc95f8e001835a055',
                ),
            ).toBeTruthy();
        });

        // it looks like an url
        it('should return true, because in start we have url, and this string are like url', () => {
            expect(isValidUrl('yandex.ru? lets go here')).toBeTruthy();
        });
    });

    describe('Test cases with invalid urls', () => {
        it('should return false, check simple long text', () => {
            expect(
                isValidUrl(
                    'Помогите клиентам быстро найти вашу страницу в интернете. Благодаря QR-коду клиентам не придётся вводить вручную ссылку на ваш сайт или любой другой онлайн-ресурс.',
                ),
            ).toBeFalsy();
        });

        it('should return false, check simple question', () => {
            expect(isValidUrl('What is qr code?')).toBeFalsy();
        });

        it('should return false, check text with url inside', () => {
            expect(isValidUrl('Hello, lets go to yandex.ru')).toBeFalsy();
        });
    });
});
