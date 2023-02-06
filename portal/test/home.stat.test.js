/* eslint dot-notation: 1, no-unused-expressions: 0 */
describe('home.stat', function() {
    var setCounterCallCount = 0,
        setCounterShowCallCount = 0,
        fakeSetCounterOur = function (path, url, opts = {}) {
            var {noBlockDisplay} = opts;

            ++setCounterCallCount;
            if (!noBlockDisplay) {
                ++setCounterShowCallCount;
            }

            var res = {};
            if (path) {
                res.id = 'root.' + path;
            }
            res.our = 1;
            if (url) {
                res.url = url;
            }
            return res;
        },
        fakeSetCounterOther = function (path, url, opts = {}) {
            var {noBlockDisplay} = opts;
            ++setCounterCallCount;
            if (!noBlockDisplay) {
                ++setCounterShowCallCount;
            }

            var res = {};
            if (path) {
                res.id = 'root.' + path;
            }
            if (url) {
                res.our = 0;
                res.url = '//other/' + url;
            } else {
                res.our = 1;
            }
            return res;
        },
        log = [],
        fakeSetCounterLog = function (path) {
            log.push(path);
        },
        customParamsLog = [],
        fakeSetCounterCustomParams = function (path, url, opts = {}) {
            var {customParams} = opts;
            customParamsLog.push(customParams);
            return fakeSetCounterOur.apply(this, arguments);
        },
        fakeGetRoot = function () {
            return 'root';
        },
        fakeHashOur = {
            setCounter: fakeSetCounterOur,
            LiveCartridge: true,
            ShowID: '1.2.3.4',
            StatLogGetRoot: fakeGetRoot
        },
        fakeHashOther = {
            setCounter: fakeSetCounterOther,
            LiveCartridge: true,
            ShowID: '1.2.3.4',
            StatLogGetRoot: fakeGetRoot
        },
        fakeHashLog = {
            setCounter: fakeSetCounterLog,
            LiveCartridge: true,
            ShowID: '1.2.3.4',
            StatLogGetRoot: fakeGetRoot
        },
        fakeHashCustomParams = {
            setCounter: fakeSetCounterCustomParams,
            LiveCartridge: true
        };

    beforeEach(function () {
        setCounterCallCount = 0;
        setCounterShowCallCount = 0;
    });

    describe('off', function() {
        var fakeHashOff = {
                setCounter: fakeSetCounterOur,
                LiveCartridge: false
            },
            stat;

        beforeEach(function () {
            stat = home.Stat(fakeHashOff);
        });

        it('не включается с пустым хэшом', function() {
            var fakeHashEmpty = {};

            home.Stat(fakeHashEmpty).on.should.be.false;

            setCounterCallCount.should.be.equal(0);
        });

        it('не включается с выключенным хэшом', function() {
            stat.on.should.be.false;
        });

        it('не возвращает рут', function() {
            stat.getRoot().should.equal('');
        });

        it('не генерирует path', function() {
            stat.getPath('str').should.equal('');

            setCounterCallCount.should.be.equal(0);
        });

        it('не изменяет url', function() {
            stat.getUrl('str', 'ya.ru').should.equal('ya.ru');

            setCounterCallCount.should.be.equal(0);
        });

        it('не генерирует аттрибуты', function() {
            stat.getAttr('str').should.equal('');
            stat.getAttr('str', 'ya.ru').should.equal('');
            stat.getAttr('str', 'ya.ru', {isRedirect: false}).should.equal('');

            setCounterCallCount.should.be.equal(0);
        });

        it('не генерирует аттрибуты адаптичных счетчиков', function() {
            stat.getAdaptiveCounter('path').should.equal('');

            setCounterCallCount.should.be.equal(0);
        });

        it('не генерирует клиентские счётчики', function () {
            stat.getClientCounter('path').should.equal('');

            setCounterCallCount.should.be.equal(0);
        });
    });

    describe('on (our urls)', function() {
        var stat;

        beforeEach(function () {
            stat = home.Stat(fakeHashOur);
        });

        it('включается', function() {
            stat.on.should.be.true;
        });

        it('возвращает рут', function() {
            stat.getRoot().should.equal('root');
        });

        it('генерирует path', function() {
            stat.getPath('str').should.equal('root.str');

            setCounterCallCount.should.be.equal(1);
            setCounterShowCallCount.should.be.equal(1);
        });

        it('не изменяет url', function() {
            stat.getUrl('str', 'ya.ru').should.equal('ya.ru');
            stat.getUrl('str', 'ya.ru', {logShow: false}).should.equal('ya.ru');

            setCounterCallCount.should.be.equal(2);
            setCounterShowCallCount.should.be.equal(1);
        });

        it('работает с дополнительными параметрами', function () {
            var stat2 = home.Stat({
                setCounter: function (path, url, opts) {
                    opts.customParams.should.deep.equal({index: 123});
                    opts.additionalParams.should.deep.equal({index: 123});

                    return {
                        id: path,
                        url: url,
                        our: 1
                    };
                },
                LiveCartridge: true,
                ShowID: '1.2.3.4',
                StatLogGetRoot: fakeGetRoot
            });

            stat2.getUrl('str', 'ya.ru', {customParams: {index: 123}});

            var stat3 = home.Stat({
                setCounter: function (path, url, opts) {
                    opts.additionalParams.should.deep.equal({index: 123});
                    return {
                        id: path,
                        url: url,
                        our: 1
                    };
                },
                LiveCartridge: true,
                ShowID: '1.2.3.4',
                StatLogGetRoot: fakeGetRoot
            });

            stat3.addCustomPageParams({index: 123});
            stat3.getUrl('str', 'ya.ru');
        });

        it('генерирует аттрибуты', function() {
            stat.getAttr('str0').should.equal(' data-statlog="str0" data-statlog-showed="1"');
            stat.getAttr('str1', '', {isRedirect: false}).should.equal(' data-statlog="str1" data-statlog-showed="1" data-statlog-redir="0"');
            stat.getAttr('str2', 'ya.ru').should.equal(' data-statlog="str2" data-statlog-showed="1"');
            stat.getAttr('str3', 'ya.ru', {isRedirect: false}).should.equal(' data-statlog="str3" data-statlog-showed="1" data-statlog-redir="0"');
            stat.getAttr('str4', 'ya.ru', {logShow: false, precise: true}).should.equal(' data-statlog="str4" data-statlog-precise="1"');

            setCounterCallCount.should.be.equal(5);
            setCounterShowCallCount.should.be.equal(4);
        });

        it('генерирует атрибуты адаптивных счетчиков', function() {
            stat.getAdaptiveCounter('path').should.equal(' data-statlog="path" data-statlog-autoshow="1"');
            stat.getAttr('path', null, {adaptive: true}).should.equal(' data-statlog="path" data-statlog-autoshow="1"');
            stat.getAttr('path', null, {adaptive: true, logShow: false}).should.equal(' data-statlog="path" data-statlog-autoshow="1"');
            stat.getAttr('path', null, {adaptive: true, logShow: true}).should.equal(' data-statlog="path" data-statlog-autoshow="1"');

            setCounterCallCount.should.be.equal(0);
            setCounterShowCallCount.should.be.equal(0);
        });

        it('генерирует атрибуты клиентских счётчиков', function () {
            stat.getClientCounter('path').should.equal(' data-statlog="path"');
            stat.getClientCounter('path', true).should.equal(' data-statlog="path" data-statlog-redir="0"');

            setCounterCallCount.should.be.equal(0);
            setCounterShowCallCount.should.be.equal(0);
        });

        it('пишет показы переданных счётчиков и возвращает пути без корня', function () {
            stat.logShow('header').should.equal('header');

            setCounterCallCount.should.be.equal(1);
            setCounterShowCallCount.should.be.equal(1);
        });

        it('не пишет показы, если передать параметр в getAttr', function () {
            stat.getAttr('str0', null, {logShow: false}).should.equal(' data-statlog="str0"');
            stat.getAttr('str0', 'ya.ru', {logShow: false}).should.equal(' data-statlog="str0"');

            setCounterCallCount.should.be.equal(1);
            setCounterShowCallCount.should.be.equal(0);
        });

        it('не делает ничего, если путь не передали', function () {
            stat.getAttr(undefined, 'ya.ru', {logShow: false}).should.equal('');
            stat.getAdaptiveCounter(null).should.equal('');
            stat.getClientCounter('').should.equal('');

            setCounterCallCount.should.be.equal(0);
            setCounterShowCallCount.should.be.equal(0);
        });
    });

    describe('on (other urls)', function() {
        var stat;

        beforeEach(function () {
            stat = home.Stat(fakeHashOther);
        });

        it('включается', function() {
            stat.on.should.be.true;
        });

        it('генерирует path', function() {
            stat.getPath('str').should.equal('root.str');

            setCounterCallCount.should.be.equal(1);
            setCounterShowCallCount.should.be.equal(1);
        });

        it('подписывает url', function() {
            stat.getUrl('str', 'ya.ru').should.equal('//other/ya.ru');

            setCounterCallCount.should.be.equal(1);
            setCounterShowCallCount.should.be.equal(1);
        });

        it('генерирует аттрибуты', function() {
            stat.getAttr('str0').should.equal(' data-statlog="str0" data-statlog-showed="1"');
            stat.getAttr('str1', '', {isRedirect: false}).should.equal(' data-statlog="str1" data-statlog-showed="1" data-statlog-redir="0"');
            stat.getAttr('str2', 'ya.ru').should.equal(' data-statlog="str2" data-statlog-showed="1" data-statlog-url="//other/ya.ru"');
            stat.getAttr('str3', 'ya.ru', {isRedirect: false}).should.equal(' data-statlog="str3" data-statlog-showed="1" data-statlog-redir="0"');

            setCounterCallCount.should.be.equal(4);
            setCounterShowCallCount.should.be.equal(4);
        });
    });

    describe('custom params', function() {
        var stat = home.Stat(fakeHashCustomParams);

        it('передаёт дополнительные параметры', function() {
            stat.getAttr('path', 'url', {customParams: 123});
            stat.getUrl('path', 'url', {customParams: {a: 'b'}});
            stat.getPath('path', 4);
            stat.logShow('path', 5);

            customParamsLog.should.deep.equal([123, {a: 'b'}, 4, 5]);

            setCounterCallCount.should.equal(4);
        });

        it('добавляет дополнительные параметры в путь для логгирования на клиенте', function () {
            stat.getAttr('path', null, {
                logShow: false,
                customParams: 42
            }).should.equal(' data-statlog="path(id=42)"');

            stat.getAttr('path', null, {
                logShow: false,
                customParams: {
                    foo: 42,
                    bar: 'baz'
                }
            }).should.equal(' data-statlog="path(foo=42;bar=baz)"');
        });

        it('энкодит дополнительные параметры', function () {
            stat.getAttr('path', null, {
                logShow: false,
                customParams: {
                    pi: '3,14',
                    place: '31,46;42,36'
                }
            }).should.equal(' data-statlog="path(pi=3%2C14;place=31%2C46%3B42%2C36)"');
        });

        it('не логируется undefined', function () {
            stat.getAttr('path', null, {
                logShow: false,
                customParams: {
                    pi: '3,14',
                    place: undefined
                }
            }).should.equal(' data-statlog="path(pi=3%2C14)"');
        });

        describe('_stringifyCustomParams', function () {
            it('получает кастомные параметры из объекта', function () {
                stat._stringifyCustomParams({
                    pi: '3,14',
                    place: '31,46;42,36'
                }).should.equal('(pi=3%2C14;place=31%2C46%3B42%2C36)');
            });

            it('не логируется undefined', function () {
                stat._stringifyCustomParams({
                    pi: '3,14',
                    place: undefined
                }).should.equal('(pi=3%2C14)');
            });

            it('пустая строка, если в объекте толкьо undefined value', function () {
                stat._stringifyCustomParams({
                    place: undefined
                }).should.equal('');
            });
            it('пустая строка из пустого объекта', function () {
                stat._stringifyCustomParams({})
                    .should.equal('');
            });
        });
    });

    describe('logShow', function() {
        var stat = home.Stat(fakeHashLog);

        it('возвращает значение', function() {
            stat.logShow('path0').should.equal('path0', 'logShow return value');
        });

        it('вызывает setCounter', function() {
            stat.logShow('path1');
            log.should.deep.equal(['path0', 'path1']);
        });
    });

    describe('getShows', function () {
        var fakeHashOff = {
                setCounter: fakeSetCounterOur,
                LiveCartridge: false
            },
            offStat = home.Stat(fakeHashOff);

        it('возвращает пустой массив с выключенной статистикой', function() {
            offStat.getShows().should.deep.equal([]);
            offStat.logShow('abcde');
            offStat.getShows().should.deep.equal([]);
        });

        it('возвращает пустой массив с включённой статистикой и выключенным collect\'ом', function() {
            var stat = home.Stat(fakeHashOur, {collect: false});
            stat.getShows().should.deep.equal([]);
            stat.getAttr('abcde', null, {logShow: false});
            stat.getShows().should.deep.equal([]);
            stat.getAttr('abcde', null, {logShow: true});
            stat.getShows().should.deep.equal([]);
            stat.logShow('abcde2');
            stat.getShows().should.deep.equal([]);
        });

        it('возвращает массив с включенной статистикой и включённым collect\'ом', function() {
            var stat = home.Stat(fakeHashOur, {collect: true});
            stat.getShows().should.deep.equal([]);
            stat.getAttr('abcde', null, {logShow: false});
            stat.getShows().should.deep.equal([]);
            stat.getAttr('abcde', null, {logShow: true});
            stat.getShows().should.deep.equal(['abcde']);
            stat.logShow('abcde2');
            stat.getShows().should.deep.equal(['abcde', 'abcde2']);
        });
    });

    describe('apphost root', function () {
        it('В аппхосте тоже работает рут', function () {
            var stat = home.Stat({
                statRoot: 'v14',
                setCounter: fakeSetCounterOur,
                LiveCartridge: true,
                ShowID: '1.2.3.4'
            });

            stat.getRoot().should.equal('v14');

            stat = home.Stat({
                statRoot: 'v14',
                setCounter: fakeSetCounterOur,
                LiveCartridge: false,
                ShowID: '1.2.3.4'
            });

            stat.getRoot().should.equal('');
        });
    });
});
