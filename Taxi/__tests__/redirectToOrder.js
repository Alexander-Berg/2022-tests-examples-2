const request = require('supertest');
const express = require('express');
const redirectToOrder = require('../redirectToOrder');

describe('yango redirectToOrder middleware', () => {
    it('Должен редиректить на order если есть параметры и запрошен корень', () => {
        const app = createApp();

        return request(app)
            .get('/')
            .query({
                gfrom: 'Moscow'
            })
            .expect(302, 'Found. Redirecting to https://127.0.0.1/order/?gfrom=Moscow');
    });

    it('Мобилку Должен редиректить на / если есть параметры и запрошен корень', () => {
        const app = createApp({uatraits: {isMobile: true, isTablet: false}});

        return request(app)
            .get('/')
            .query({
                gfrom: 'Moscow'
            })
            .expect(302, 'Found. Redirecting to https://m.127.0.0.1/?gfrom=Moscow');
    });

    it('Должен игнорировать остальные параметры', () => {
        const app = createApp();

        return request(app)
            .get('/')
            .query({
                from: 'Moscow'
            })
            .expect(200);
    });

    it('Не должен редиректить если пришли не на корень', () => {
        const app = createApp();

        return request(app)
            .get('/test')
            .query({
                gfrom: 'Moscow'
            })
            .expect(200);
    });

    it('Не должен редиректить если пришли на корень без параметра', () => {
        const app = createApp();

        return request(app)
            .get('/')
            .query({})
            .expect(200);
    });
});

function createApp(initData = {uatraits: {}}) {
    const app = express();

    app.get(
        '*',
        [
            (req, res, next) => {
                Object.assign(req, initData);
                next();
            },
            redirectToOrder
        ],
        (req, res) => {
            res.status(200).json({});
        }
    );

    // eslint-disable-next-line handle-callback-err
    app.use((err, req, res, next) => {
        res.sendStatus(500);
    });

    return app;
}
