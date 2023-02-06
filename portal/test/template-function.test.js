/* eslint-env es6 */
require('should');
var transform = require('../lib/template-function');

describe('template-function', function() {
    global.home = {
        parseRules: {}
    };
    describe('getPropAccessor', function() {
        var simple = transform(' [% normal %][% _$_$_$$ %][% $1 %][% 12days %][% йцук %][% w@ %]'),
            jpath = transform(' [% normal._$_$_$$.$1.12days.йцук.w@ %]');

        it('works as expected ', function () {
            simple({
                normal: '+',
                _$_$_$$: '+',
                $1: '+',
                '12days': '+',
                'йцук': '+',
                'w@': '+'
            }).should.equal(' ++++++');
        });

        it('works as expected with jpath', function () {
            jpath({
                normal: {
                    _$_$_$$: {
                        $1: {
                            '12days': {
                                'йцук': {
                                    'w@': '+'
                                }
                            }
                        }
                    }
                }
            }).should.equal(' +');
        });
    });

    describe('подстановка', function () {
        it('не игнорирует пустую строку в данных', function() {
            var usage = transform('nothing[% smth %]between');

            usage({
                smth: ''
            }, {}, () => 'template').should.equal('nothingbetween');
        });

        it('Допускает falsy значения как результат шаблона', function () {
            var say = transform('There are [% exec:unicorns %] prefixed unicorns'),
                say2 = transform('There are [% unicorns %] unicorns');

            say({}, {}, () => 0).should.equal('There are 0 prefixed unicorns');
            say2({}, {}, () => 0).should.equal('There are 0 unicorns');
        });


        it('Заменяет undefined значения', function () {
            var say = transform('prefixed:<[% exec:void %]>'),
                say2 = transform('<[% void %]>');

            say({}, {}, () => {}).should.equal('prefixed:<>');
            say2({}, {}, () => {}).should.equal('<>');
        });

        it('Использует req', function () {
            var say = transform('[% req-seeker-func %] [% first %] [% second %]');

            say({first: 'foo'}, {second: 'bar'}, () => 'exec').should.equal('exec foo bar');
        });
    });

    describe('jpath', function () {
        var simple = transform(' [% indata %][% inreq %][% inexec %][% nowhere %]'),
            withDots = transform(' [% a.b.c %]'),
            short = transform(' [% a.b %]');
        it('ищет ключи без точки в data, req и execView', function() {
            simple({
                indata: '+'
            }, {
                indata: '-',
                inreq: '+'
            }, function (key) {
                return key === 'inexec' ? '+' : key === 'nowhere' ? undefined : '-';
            }).should.equal(' +++');
        });

        describe('ключи с точкой', function () {
            it('ищет только в data', function() {
                withDots({
                    a: {
                        b: {
                            c: '+'
                        }
                    }
                }, {
                    a: {
                        b: {
                            c: '1'
                        }
                    }
                }).should.equal(' +');

                withDots({}, {
                    a: {
                        b: {
                            c: '2'
                        }
                    }
                }).should.equal(' ');
            });

            it('не ломается на отсутствии свойств', function() {
                withDots({
                    x: {
                        b: {
                            c: '+'
                        }
                    }
                }, {}).should.equal(' ');

                withDots({
                    a: {
                        x: {
                            c: '+'
                        }
                    }
                }, {}).should.equal(' ');

                withDots({
                    a: {
                        b: {
                            x: '+'
                        }
                    }
                }, {}).should.equal(' ');
            });

            it('не ломается на коротких строках', function() {
                short({
                    a: {
                        b: '+'
                    }
                }, {}).should.equal(' +');
            });

            it('может вернуть falsy значения', function () {
                withDots({
                    a: {
                        b: {
                            c: 0
                        }
                    }
                }).should.equal(' 0');
            });
        });
    });

    describe('custom prefix', function() {
        it('выполняет функции префиксов', function() {
            home.parseRules.test = function (data, req, key) {
                return key + ' is ok';
            };

            var testTemplate = transform('<div>[% test:blah %]</div>');
            testTemplate().should.equal('<div>blah is ok</div>');
        });
    });

    describe('builtin prefix', function() {
        describe('без вложенности', function() {
            var data = {
                a: 42,
                b: true,
                c: false
            };

            var tester = transform('[% data:a %][% req:a %][% data:notfound %][% req: b %][% req:c %]'),
                invoker = transform('invoke [% exec:tester %]+[% exec:notfound %]');

            it('exec вызывает шаблоны', function () {
                invoker(data, data, function(key) {
                    return 'invoked:' + key;
                }).should.equal('invoke invoked:tester+invoked:notfound');
            });

            it('exec не выводит undefined', function () {
                invoker(data, data, function() {}).should.equal('invoke +');
            });

            it('data и req работают', function() {
                tester({
                    a: 'bla'
                }, data).should.equal('bla42truefalse');
            });
        });

        describe('с вложенными объектами', function() {
            var data = {
                vars: {
                    a: 42,
                    b: true,
                    c: false
                }
            };

            var tester = transform('[% data:vars.a %][% req:vars.a %][% data:vars.notfound %][% req: vars.b %][% req:vars.c %]'),
                invoker = transform('invoke [% exec:tester %]+[% exec:notfound %]');

            it('exec вызывает шаблоны', function () {
                invoker(data, data, function(key) {
                    return 'invoked:' + key;
                }).should.equal('invoke invoked:tester+invoked:notfound');
            });

            it('exec не выводит undefined', function () {
                invoker(data, data, function() {}).should.equal('invoke +');
            });

            it('data и req работают', function() {
                tester({
                    vars: {
                        a: 'bla'
                    }
                }, data).should.equal('bla42truefalse');
            });
        });
    });
});
