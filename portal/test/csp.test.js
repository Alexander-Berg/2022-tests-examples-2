const {
    cspV1,
    cspV2
} = require('../lib/csp');

describe('csp', () => {
    const allFields = {
        'default-src': ["'none'", "'self'"],
        'script-src': ['aaa.be', "'unsafe-inline'", "'unsafe-eval'"],
        'style-src': ['http://qwe.rty'],
        'connect-src': ['https://asd.fe'],
        'report-uri': ['https://xyz.me/some/path?qwe=rty'],
        'child-src': ['child.src'],
        'frame-src': ['frame.src'],
        'media-src': ['media.src'],
        'object-src': ['object.src'],
        'font-src': ['font.src'],
        'image-src': ['image.src']
    };

    describe('v1', () => {
        it('игнорирует undefined и null', () => {
            cspV1({'default-src': ['qwe.rty', undefined, null]})
                .should.equal('default-src https://qwe.rty');
        });

        it('добавляет https для значений без схемы', () => {
            cspV1({'default-src': ['qwe.rty']}).should.equal('default-src https://qwe.rty');
            cspV1({'default-src': ['qwe.rty:4040']}).should.equal('default-src https://qwe.rty:4040');
        });

        it('добавляет хост без схемы для урлов на http страниц', () => {
            cspV1({'default-src': ['qwe.rty']}, {isHttp: true}).should.equal('default-src https://qwe.rty qwe.rty');
            cspV1({'default-src': ['qwe.rty:4040']}, {isHttp: true}).should.equal('default-src https://qwe.rty:4040 qwe.rty:4040');
        });

        it('не меняет схему для http урлов', () => {
            cspV1({'default-src': ['http://qwe.rty']}).should.equal('default-src http://qwe.rty');
            cspV1({'default-src': ['http://qwe.rty:4040']}).should.equal('default-src http://qwe.rty:4040');
        });

        it('убирает схему для http урлов на http страницах', () => {
            cspV1({'default-src': ['http://qwe.rty']}, {isHttp: true}).should.equal('default-src qwe.rty');
            cspV1({'default-src': ['http://qwe.rty:4040']}, {isHttp: true}).should.equal('default-src qwe.rty:4040');
        });

        it('не меняет схему для https урлов', () => {
            cspV1({'default-src': ['https://qwe.rty']}).should.equal('default-src https://qwe.rty');
            cspV1({'default-src': ['https://qwe.rty:4040']}).should.equal('default-src https://qwe.rty:4040');
        });

        it('не меняет кастомную схему', () => {
            cspV1({'default-src': ['bro-crazy://qwe.rty']}).should.equal('default-src bro-crazy://qwe.rty');
            cspV1({'default-src': ['bro-crazy://qwe.rty:4040']}).should.equal('default-src bro-crazy://qwe.rty:4040');
        });

        it('не меняет схему без хоста', () => {
            cspV1({'default-src': ['bro-crazy:', 'http:', 'https:']}).should.equal('default-src bro-crazy: http: https:');
        });

        it('удаляет дубликаты', () => {
            cspV1({'default-src': ['qwe.rty', 'http://qwe.rty', 'https://qwe.rty']})
                .should.equal('default-src https://qwe.rty http://qwe.rty');

            cspV1({'default-src': ['qwe.rty', 'http://qwe.rty', 'https://qwe.rty']}, {isHttp: true})
                .should.equal('default-src https://qwe.rty qwe.rty');
        });

        it('не меняет спецзначения', () => {
            const special = [
                "'self'",
                "'unsafe-inline'",
                "'unsafe-eval'",
                "'nonce-deadbeef'",
                "'sha256-deadbeef'",
                "'sha384-deadbeef'",
                "'sha512-deadbeef'"
            ];
            cspV1({'default-src': ["'none'"], 'style-src': special})
                .should.equal('default-src \'none\';style-src ' + special.join(' '));
        });

        it('объединяет директивы при переименовании', () => {
            cspV1({'child-src': ['one'], 'frame-src': ['two']})
                .should.equal('frame-src https://one https://two');
        });

        it('обрезает path, query и fragment', () => {
            cspV1({'default-src': [
                'qwe.rty/path',
                'https://asd.fgh/path',
                'cut.qwery?a=b',
                'ws://cut.qwery?x=b',
                'cut.frag#qqq',
                'mailto://cut.frag#qqq',
                'cut.all/path/to?q=1#qq'
            ]}).should.equal('default-src' +
                ' https://qwe.rty' +
                ' https://asd.fgh' +
                ' https://cut.qwery' +
                ' ws://cut.qwery' +
                ' https://cut.frag' +
                ' mailto://cut.frag' +
                ' https://cut.all');
        });

        it('возвращает значение заголовка', () => {
            cspV1(allFields).should.equal('default-src \'self\';' +
                'script-src https://aaa.be \'unsafe-inline\' \'unsafe-eval\';' +
                'style-src http://qwe.rty;' +
                'connect-src https://asd.fe;' +
                'report-uri https://xyz.me/some/path?qwe=rty;' +
                'frame-src https://child.src https://frame.src;' +
                'media-src https://media.src;' +
                'object-src https://object.src;' +
                'font-src https://font.src;' +
                'image-src https://image.src');
        });
    });

    describe('v2', () => {
        it('игнорирует undefined и null', () => {
            cspV1({'default-src': ['qwe.rty', undefined, null]})
                .should.equal('default-src https://qwe.rty');
        });

        it('не добавляет схему для значений без схемы', () => {
            cspV2({'default-src': ['qwe.rty']}).should.equal('default-src qwe.rty');
            cspV2({'default-src': ['qwe.rty:4040']}).should.equal('default-src qwe.rty:4040');
        });

        it('убирает схему для http урлов', () => {
            cspV2({'default-src': ['http://qwe.rty']}).should.equal('default-src qwe.rty');
            cspV2({'default-src': ['http://qwe.rty:4040']}).should.equal('default-src qwe.rty:4040');
        });

        it('убирает схему для https урлов', () => {
            cspV2({'default-src': ['https://qwe.rty']}).should.equal('default-src qwe.rty');
            cspV2({'default-src': ['https://qwe.rty:4040']}).should.equal('default-src qwe.rty:4040');
        });

        it('не меняет кастомную схему', () => {
            cspV2({'default-src': ['bro-crazy://qwe.rty']}).should.equal('default-src bro-crazy://qwe.rty');
            cspV2({'default-src': ['bro-crazy://qwe.rty:4040']}).should.equal('default-src bro-crazy://qwe.rty:4040');
        });

        it('не меняет схему без хоста', () => {
            cspV2({'default-src': ['bro-crazy:', 'http:', 'https:']}).should.equal('default-src bro-crazy: http: https:');
        });

        it('удаляет дубликаты', () => {
            cspV2({'default-src': ['qwe.rty', 'http://qwe.rty', 'https://qwe.rty']})
                .should.equal('default-src qwe.rty');

        });

        it('не меняет спецзначения', () => {
            const special = [
                "'self'",
                "'unsafe-inline'",
                "'unsafe-eval'",
                "'nonce-deadbeef'",
                "'sha256-deadbeef'",
                "'sha384-deadbeef'",
                "'sha512-deadbeef'"
            ];
            cspV2({'default-src': ["'none'"], 'style-src': special})
                .should.equal('default-src \'none\';style-src ' + special.join(' '));
        });

        it('объединяет директивы при переименовании', () => {
            cspV2({'child-src': ['one'], 'frame-src': ['two']})
                .should.equal('child-src one two');
        });

        it('возвращает значение заголовка', () => {
            cspV2(allFields).should.equal('default-src \'self\';' +
                'script-src aaa.be \'unsafe-inline\' \'unsafe-eval\';' +
                'style-src qwe.rty;' +
                'connect-src asd.fe;' +
                'report-uri https://xyz.me/some/path?qwe=rty;' +
                'child-src child.src frame.src;' +
                'media-src media.src;' +
                'object-src object.src;' +
                'font-src font.src;' +
                'image-src image.src');
        });
    });
});