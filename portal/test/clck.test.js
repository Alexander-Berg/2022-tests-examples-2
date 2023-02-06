const filePath = process.argv.includes('--newFile') ? process.argv[process.argv.indexOf('--newFile') + 1] : '../auto/clck';
const clck = require(filePath);

describe('clck', function () {
    it('ok', function () {
        const ok = [
            'yandex.ru',
            '//yandex.ru',
            'http://yandex.ru',
            'https://yandex.ru',
            'ftp://yandex.ru',
            'https://some.yandex.ru',
            'https://some.stuff.yandex.ru',
            'https://so-me.st-uff.yandex.ru',
            'https://so-me.st-uff123.yandex.ru',
            'https://some.yandex.com',
            'https://some.yandex.com/',
            'https://some.yandex.com/index.html',
            'https://some.yandex.com',
            'yandex.com.ge',
            'yandex.uz',
            'awaps.yandex.net'
        ];

        for (const test of ok) {
            clck.test(test).should.equal(true, `${test} is yandex domain`);
        }
    });

    it('not ok', function () {
        const notOk = [
            'yandex.ru.hacker.net',
            'yandex.ru\nyandex.com',
            'yandexXru',
            '.yandex.ru',
            ' yandex.ru',
            'https:yandex.ru'
        ];
        for (const test of notOk) {
            clck.test(test).should.equal(false, `${test} is not yandex domain`);
        }
    });
});
