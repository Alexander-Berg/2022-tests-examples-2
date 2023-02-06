'use strict';

/*global require */
const mockery = require('mockery');

function testRender(req, res, next) {
    res.bundleRender = function (bundleName, data) {
        res.json(data);
    };
    next();
}

module.exports = {
    before: function () {
        // Отключаем рендеринг
        mockery.registerMock('../middleware/express-bundle-response', () => testRender);
        mockery.registerMock('express-uatraits', () => (req, res, next) => next());
        mockery.registerMock('express-yandexuid', () => (req, res, next) => next());
        mockery.registerMock('./express-bunker', () => {
            var bunker = require('../mock/bunker.json');

            return function (req, res, next) {
                req.bunker = bunker;
                next();
            };
        });
        mockery.registerMock('express-secretkey', () => {
            return function (req, res, next) {
                next();
            };
        });
        mockery.enable({
            warnOnReplace: false,
            warnOnUnregistered: false,
            useCleanCache: true
        });
    },
    after: function () {
        mockery.disable();
    }
};
