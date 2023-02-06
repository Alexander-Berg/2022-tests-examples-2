'use strict';

const {checkConditions} = require('../yaWaitUrl');

describe('hermione.yaWaitUrl', () => {
    it('Проверяет полное соответствие', function () {
        checkConditions('https://yandex.ru/', 'https://yandex.ru/').should.equal(true);
        checkConditions('https://yandex.ru/?clid=123', 'https://yandex.ru/').should.equal(false);
    });

    it('Проверяет по регэкспу', function () {
        checkConditions('https://yandex.ru/', /yandex\..*/).should.equal(true);
        checkConditions('https://yandex.ru/?clid=123', /yandex\.com\..*/).should.equal(false);
    });

    it('Проверяет по объекту с and и or', function () {
        checkConditions('https://yandex.ru/', {and: [/yandex/, /\.ru/]}).should.equal(true);
        checkConditions('https://yandex.ru/', {and: ['yandex', /\.ru/]}).should.equal(false);
        checkConditions('https://yandex.ru/', {or: ['yandex', /\.ru/]}).should.equal(true);
    });

    it('Проверяет по объекту с составляющими урла', function () {
        checkConditions('https://yandex.ru/', {protocol: 'https:'}).should.equal(true);
        checkConditions('http://yandex.ru/', {protocol: 'https:'}).should.equal(false);
        checkConditions('http://yandex.ru/', {host: 'yandex.ru'}).should.equal(true);
        checkConditions('http://yandex.ru/', {path: '/'}).should.equal(true);
        checkConditions('http://yandex.ru/?clid=123', {query: {clid: 124}}).should.equal(false);
        checkConditions('http://yandex.ru/?clid=123', {query: {clid: 123}}).should.equal(true);
    });

    it('Проверяет по сложному объекту', function () {
        checkConditions('https://yandex.ru/?clid=123', {or: [{protocol: 'http:'}, {host: 'ya.ru'}]}).should.equal(false);
        checkConditions('http://yandex.ru/?clid=123', {or: [{protocol: 'http:'}, {host: 'ya.ru'}]}).should.equal(true);
        checkConditions('http://yandex.ru/?clid=123', {and: [{protocol: 'http:'}, {host: 'ya.ru'}]}).should.equal(false);
        checkConditions('http://yandex.ru/?clid=123', {and: [{protocol: 'http:'}, {query: {clid: /^\d+$/}}]}).should.equal(true);
    });
});
