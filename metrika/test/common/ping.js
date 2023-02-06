/*global describe, before, after, it, afterEach, beforeEach, require */
var request = require('supertest');

describe('GET /ping', function () {
    before(function () {

    });

    after(function () {

    });

    beforeEach(function () {

    });

    afterEach(function () {

    });

    it('respond with OK', function (done) {
        request(require('../../app'))
            .get('/ping')
            .expect(200, done);
    });
});
