'use strict';

const {guessPageLang} = require('../yaOpenMorda');
const getUrl = require('../util/getUrl');

describe('hermione.yaOpenMorda', () => {
    describe('Генерирует правильный урл', () => {
        it('Поддерживает префиксы', () => {
            getUrl({mode: 'dev', prefix: 'v1d1.wdevx'}).should.equal('https://v1d1.wdevx.yandex.ru/');
            getUrl({mode: 'beta', prefix: 'morda-pr-123.hometest'}).should.equal('https://morda-pr-123.hometest.yandex.ru/');
            getUrl({mode: 'testing', prefix: 'rtxz'}).should.equal('https://rtxz.yandex.ru/');
            getUrl({mode: 'prod', prefix: 'old'}).should.equal('https://old.yandex.ru/');
        });

        it('Поддерживает режимы', () => {
            getUrl({mode: 'dev', prefix: 'v0d0.wdevx'}).should.equal('https://v0d0.wdevx.yandex.ru/');
            getUrl({prefix: 'rc'}).should.equal('https://rc.yandex.ru/');
            getUrl({mode: 'prod'}).should.equal('https://yandex.ru/');

            getUrl({mode: 'dev', prefix: 'v0d0.wdevx'}, {yaru: true}).should.equal('https://v0d0.wdevx.ya.ru/');
            getUrl({prefix: 'rc'}, {yaru: true}).should.equal('https://rc.ya.ru/');
            getUrl({mode: 'prod'}, {yaru: true}).should.equal('https://ya.ru/');
        });

        it('Поддерживает www', () => {
            getUrl({mode: 'dev', prefix: 'v0d0.wdevx'}, {www: true}).should.equal('https://www-v0d0.wdevx.yandex.ru/');
            getUrl({prefix: 'rc'}, {www: true}).should.equal('https://www-rc.yandex.ru/');
            getUrl({mode: 'prod'}, {www: true}).should.equal('https://www.yandex.ru/');

            getUrl({mode: 'dev', prefix: 'v0d0.wdevx'}, {www: true, yaru: true}).should.equal('https://www-v0d0.wdevx.ya.ru/');
            getUrl({prefix: 'rc'}, {www: true, yaru: true}).should.equal('https://www-rc.ya.ru/');
            getUrl({mode: 'prod'}, {www: true, yaru: true}).should.equal('https://www.ya.ru/');
        });

        it('Поддерживает zone', () => {
            getUrl({mode: 'dev', prefix: 'v0d0.wdevx'}, {zone: 'by'}).should.equal('https://v0d0.wdevx.yandex.by/');
            getUrl({prefix: 'rc'}, {zone: 'by'}).should.equal('https://rc.yandex.by/');
            getUrl({mode: 'prod'}, {zone: 'by'}).should.equal('https://yandex.by/');

            expect(() => getUrl({mode: 'dev', prefix: 'v0d0.wdevx'}, {zone: 'by', yaru: true})).to.throw();
            expect(() => getUrl({mode: 'rc'}, {zone: 'by', yaru: true})).to.throw();
            expect(() => getUrl({mode: 'prod'}, {zone: 'by', yaru: true})).to.throw();
        });

        it('Поддерживает протокол', () => {
            getUrl({mode: 'prod'}, {https: false}).should.equal('http://yandex.ru/');
        });

        it('Поддерживает параметры', () => {
            getUrl({mode: 'prod'}, {edit: true}).should.equal('https://yandex.ru/?edit=1');
            getUrl({mode: 'prod'}, {clid: 123}).should.equal('https://yandex.ru/?clid=123');
            getUrl({mode: 'prod'}, {exp: 'direct'}).should.equal('https://yandex.ru/?exp=direct');
            getUrl({mode: 'prod'}, {exp: 'direct', getParams: {win: 123}}).should.equal('https://yandex.ru/?win=123&exp=direct');
            getUrl({prefix: 'rc'}, {exp: 'direct', dump: true}).should.equal('https://rc.yandex.ru/?exp=direct&savevars=1');
            getUrl({mode: 'prod'}, {exp: 'direct', dump: true}).should.equal('https://yandex.ru/?exp=direct');
            getUrl({mode: 'prod'}, {exp: 'direct', dumponly: true}).should.equal('https://yandex.ru/?exp=direct&cleanvars=1');
            getUrl({mode: 'prod'}, {usemock: '123'}).should.equal('https://yandex.ru/?usemock=123');
        });

        it('Поддерживает мобильные урлы', () => {
            getUrl({mode: 'prod'}, {mobile: 'm-path'}).should.equal('https://yandex.ru/m/');
            getUrl({mode: 'prod'}, {mobile: 'm-subdomain', clid: 456}).should.equal('https://m.yandex.ru/?clid=456');
            getUrl({mode: 'prod'}, {mobile: 'tel-subdomain'}).should.equal('https://tel.yandex.ru/');
        });

        it('Поддерживает path', () => {
            getUrl({mode: 'prod'}, {path: '/portal/tvstream'}).should.equal('https://yandex.ru/portal/tvstream');
            getUrl({mode: 'prod'}, {path: '/portal/tvstream', getParams: {channel_id: 146}}).should.equal('https://yandex.ru/portal/tvstream?channel_id=146');
            getUrl({mode: 'prod'}, {path: 'i-social__closer.html'}).should.equal('https://yandex.ru/i-social__closer.html');
        });
    });

    it('Пытается предугадать язык страницы', function () {
        guessPageLang().should.equal('ru');

        guessPageLang('ru').should.equal('ru');
        guessPageLang('ua').should.equal('ru');
        guessPageLang('com.tr').should.equal('tr');
        guessPageLang('com').should.equal('en');

        guessPageLang('ru', 'uk').should.equal('uk');
        guessPageLang('com', 'uk').should.equal('en');
    });
});
