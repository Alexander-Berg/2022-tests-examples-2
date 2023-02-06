const {getUrl} = require('../src/handlers');
const chai = require('chai');

chai.should();

describe('getUrl', function () {

    describe('выбор хоста', () => {
        it('выбирает корректный tld', () => {
            [
                'yandex.ru',
                'yandex.by',
                'yandex.ua',
                'yandex.kz',
                'yandex.com',
                'yandex.com.tr'
            ].forEach(host => {
                getUrl(`tune.${host}`)
                    .should.have.property('host')
                    .which.equals(host);
            });
        });

        it('некорректные хосты приводит в yandex.ru', () => {
            [
                'tune.yandex.az',
                'qweyandex.by',
                'tune.yandex.by.evil.ru'
            ].forEach(host => {
                getUrl(host)
                    .should.have.property('host')
                    .which.equals('yandex.ru', host);
            });
        });
    });
});
