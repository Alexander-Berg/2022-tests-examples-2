const {getFallbackEmailFactory, normalizeQueryString} = require('../help');

describe('common/server/utils/help', () => {
    describe('getFallbackEmailFactory', () => {
        describe('only default', () => {
            const data = {
                default: 'support@support-uber.com'
            };
            const getFallbackEmailUber = getFallbackEmailFactory(data);

            test('Для убера всегда один и тот же', () => {
                expect(getFallbackEmailUber({})).toEqual(data.default);
                expect(getFallbackEmailUber({service: 'uber'})).toEqual(data.default);
                expect(getFallbackEmailUber({service: 'uber', countryISOName: 'RU'})).toEqual(data.default);
            });
        });

        describe('many variants', () => {
            const data = {
                taxi: {
                    ru: 'support@taxi.yandex.ru',
                    by: 'support@taxi.yandex.by'
                },
                yango: {
                    default: 'support@yango.yandex.com'
                },
                default: 'support@taxi.yandex.com'
            };
            const getFallbackEmailYandex = getFallbackEmailFactory(data);

            expect(getFallbackEmailYandex({})).toEqual(data.default);

            const getFallbackEmailTaxi = countryISOName => getFallbackEmailYandex({service: 'taxi', countryISOName});
            const getFallbackEmailYango = countryISOName => getFallbackEmailYandex({service: 'yango', countryISOName});

            expect(getFallbackEmailTaxi('RU')).toEqual(data.taxi.ru);
            expect(getFallbackEmailTaxi('BY')).toEqual(data.taxi.by);
            expect(getFallbackEmailTaxi('AZ')).toEqual(data.default);

            expect(getFallbackEmailYango('RU')).toEqual(data.yango.default);
            expect(getFallbackEmailYango('BY')).toEqual(data.yango.default);
            expect(getFallbackEmailYango('AZ')).toEqual(data.yango.default);
        });
    });

    describe('normalizeQueryString', () => {
        it('Параметры верно нормализуются', () => {
            expect(
                normalizeQueryString({
                    query: {
                        user_id: '1234',
                        zone_name: 'ekb',
                        phone: '+7-(111)-234',
                        orderId: 'orderid',
                        service: 'a',
                        services: 'a, b, c',
                        services_on_demand: 'false',
                        v: '2',
                        lat: '15.10',
                        lon: '16.20'
                    },
                    headers: {},
                    get: () => {}
                })
            ).toEqual({
                id: '1234',
                city: 'ekb',
                phone: '7111234',
                orderid: 'orderid',
                service: 'a',
                services: ['a', 'b', 'c'],
                services_on_demand: false,
                v: 2,
                lat: 15.1,
                lon: 16.2,
                uiControls: ['content_back_button', 'menu_back_button']
            });
        });
    });
});
