const deepMerge = require('deepmerge');

const i18nBuildMiddleware = require('../i18n').buildMiddleware;
const bunkerWithTankerNodes = require('./mocks/bunkerWithTankerNodes');

describe('server middleware: i18n', () => {
    const keysets = ['testkeyset1', 'testkeyset2'];
    const nodes = ['tanker1', 'tanker2'];

    test('Вызов мидлвары возвращает мидлвару и ключи i18n и tjson в req', () => {
        const {middleware, i18nKey, tjsonKey} = i18nBuildMiddleware({keysets, nodes});
        expect(middleware).toBeInstanceOf(Function);
        expect(i18nKey).toEqual('i18n');
        expect(tjsonKey).toEqual('tjson');
    });

    test('Патчит req полями i18n и tjson', () => {
        const {middleware} = i18nBuildMiddleware({keysets, nodes});
        const next = jest.fn();

        const req = {
            langdetect: {id: 'ru'},
            bunker: bunkerWithTankerNodes
        };

        middleware(req, {}, next);

        expect(req).toHaveProperty('tjson');
        expect(req).toHaveProperty('i18n');
        expect(next).toBeCalled();
    });

    test('Возвращается верный tjson и есть переводы', () => {
        const {middleware} = i18nBuildMiddleware({keysets, nodes});
        const next = jest.fn();

        const lang = 'ru';

        const req = {
            langdetect: {id: lang},
            bunker: bunkerWithTankerNodes
        };

        middleware(req, {}, next);

        const {tjson, i18n} = req;

        // Имеются нужные кейсеты
        expect(tjson).toHaveProperty(keysets[0]);
        expect(tjson).toHaveProperty(keysets[1]);

        expect(i18n.print('copyright')).toBe(
            bunkerWithTankerNodes[nodes[0]].keysets[keysets[0]].keys.copyright.translations[lang].form
        );
        // есть доступ до 2го кейсета
        expect(i18n.keyset(keysets[1]).print('user')).toBe(
            bunkerWithTankerNodes[nodes[1]].keysets[keysets[1]].keys.user.translations[lang].form
        );
    });

    test('Должен возвращаться дефолтный язык, если переводов нет', () => {
        const {middleware} = i18nBuildMiddleware({keysets, nodes});
        const next = jest.fn();

        const lang = 'tw';

        const req = {
            langdetect: {id: lang},
            bunker: bunkerWithTankerNodes
        };

        middleware(req, {}, next);

        const {i18n} = req;

        // для tw языка - ru + en + tw
        expect(i18n.print('copyright')).toBe(
            bunkerWithTankerNodes[nodes[0]].keysets[keysets[0]].keys.copyright.translations.en.form
        );
        expect(i18n.print('driving')).toBe(
            bunkerWithTankerNodes[nodes[0]].keysets[keysets[0]].keys.driving.translations.ru.form
        );
    });

    test('Миделвара мержит кейсеты', () => {
        const next = jest.fn();
        const {middleware} = i18nBuildMiddleware({
            keysets,
            nodes,
            keysetMergeFunc: ks => ({
                [keysets[0]]: deepMerge.all([ks[keysets[0]], ks[keysets[1]]])
            }),
            // NOTE: чтобы избежать кеширования
            namespace: '@test'
        });

        const lang = 'ru';
        const req = {
            langdetect: {id: lang},
            bunker: bunkerWithTankerNodes
        };

        middleware(req, {}, next);

        const tjson = req['@test/tjson'];
        const i18n = req['@test/i18n'];

        // Нет кейсета, который замержили
        expect(tjson).toHaveProperty(keysets[0]);
        expect(tjson).not.toHaveProperty(keysets[1]);

        // есть доступ до замерженного кекйсета кейсета
        expect(i18n.print('user')).toBe(
            bunkerWithTankerNodes[nodes[1]].keysets[keysets[1]].keys.user.translations[lang].form
        );
    });
});
