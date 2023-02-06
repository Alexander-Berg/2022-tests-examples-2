const request = require('supertest');
const tld = require('@yandex-int/express-tld');
const express = require('express');
const alternateMetaLinks = require('../v2/alternateMetaLinks');

describe('yango alternateMetaLinks middleware', () => {
    const pageData = {
        meta: {
            ru: {languages: ['ru', 'en'], domain: 'ru'},
            fi: {languages: ['fi', 'en'], domain: 'fi'},
            int: {languages: ['en'], isDefault: true, domain: 'com'}
        }
    };

    it('Должен кинуть исключение если не передали путь до объекта', () => {
        const app = createApp();

        return request(app)
            .get('/')
            .expect(500);
    });

    it('Возвращает верный набор ссылок', () => {
        const app = createApp(
            {
                page: pageData
            },
            {dataPath: 'page.meta'}
        );

        return request(app)
            .get('/')
            .expect([
                {id: 'ru-ru', href: 'https://127.0.0.1/ru_ru/'},
                {id: 'en-ru', href: 'https://127.0.0.1/en_ru/'},
                {id: 'fi-fi', href: 'https://127.0.0.1/fi_fi/'},
                {id: 'en-fi', href: 'https://127.0.0.1/en_fi/'},
                {id: 'x-default', href: 'https://127.0.0.1/'},
                {id: 'en', href: 'https://127.0.0.1/en_int/'}
            ]);
    });

    it('Возвращает верный набор ссылок с учетом доменов', () => {
        const app = createApp(
            {
                page: pageData
            },
            {dataPath: 'page.meta'}
        );

        return request(app)
            .get('/')
            .set('host', 'taxi.yandex.ru')
            .expect([
                {id: 'ru-ru', href: 'https://taxi.yandex.ru/ru_ru/'},
                {id: 'en-ru', href: 'https://taxi.yandex.ru/en_ru/'},
                {id: 'fi-fi', href: 'https://taxi.yandex.fi/fi_fi/'},
                {id: 'en-fi', href: 'https://taxi.yandex.fi/en_fi/'},
                {id: 'x-default', href: 'https://taxi.yandex.com/'},
                {id: 'en', href: 'https://taxi.yandex.com/en_int/'}
            ]);
    });

    it('Возвращает верный набор ссылок для страницы', () => {
        const app = createApp(
            {
                page: pageData
            },
            {dataPath: 'page.meta'}
        );

        return request(app)
            .get('/driver')
            .expect([
                {id: 'ru-ru', href: 'https://127.0.0.1/ru_ru/driver/'},
                {id: 'en-ru', href: 'https://127.0.0.1/en_ru/driver/'},
                {id: 'fi-fi', href: 'https://127.0.0.1/fi_fi/driver/'},
                {id: 'en-fi', href: 'https://127.0.0.1/en_fi/driver/'},
                {id: 'x-default', href: 'https://127.0.0.1/driver/'},
                {id: 'en', href: 'https://127.0.0.1/en_int/driver/'}
            ]);
    });

    it('Если ничего не найдено, возвращает пустой список', () => {
        const app = createApp(
            {
                page: pageData
            },
            {dataPath: 'bad.path'}
        );

        return request(app)
            .get('/driver')
            .expect([]);
    });

    function createApp(prepareData = {}, options = {}) {
        const app = express();

        app.get(
            ['/:page?'],
            [
                tld(),
                (req, res, next) => {
                    Object.assign(req, prepareData);
                    next();
                },
                alternateMetaLinks(options.dataPath)
            ],
            (req, res) => {
                res.status(200).json(req.alternateMetaLinks);
            }
        );

        // eslint-disable-next-line handle-callback-err
        app.use((err, req, res, next) => {
            res.sendStatus(500);
        });

        return app;
    }
});
