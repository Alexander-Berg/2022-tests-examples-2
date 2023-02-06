const request = require('supertest');
const express = require('express');

const buildRetpath = require('../buildRetpath');

describe('server middleware: buildRetpath', () => {
    it('Устанавливает верный retPath без учета baseUrl', () => {
        let app = createApp();

        return request(app)
            .get('/v2/order/?q=1')
            .set('host', 'test.yandex.com')
            .expect(200)
            .expect('https://test.yandex.com/order/?q=1');
    });

    function createApp() {
        const app = express();

        app.use(buildRetpath);

        const order = express.Router();
        order.get('/order', function (req, res) {
            res.send(req.buildRetpath(req));
        });

        app.use('/v2', order);
        app.use((err, req, res) => {
            // eslint-disable-next-line no-console
            console.error(err);
            res.sendStatus(500);
        });

        return app;
    }
});
