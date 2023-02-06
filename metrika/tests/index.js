'use strict';
/* eslint-env mocha */
const request = require('supertest');
const app = require('../server/app');

it('templating works', done => {
    request(app)
        .get('/')
        .set('Host', 'yandex.ru')
        .expect(/Hello Project Stub/, done);
});

it('static works', done => {
    request(app)
        .get('/static/desktop.bundles/index/_index.css')
        .expect('Cache-Control', /max-age=31536000/) // 365 days in secs
        .expect(200, done);
});
