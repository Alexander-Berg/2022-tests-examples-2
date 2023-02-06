describe('home.template', function() {
    describe('templateRe', function() {
        it('находит теги подстановки', function() {
            var matchedRules = '<div>[% test %][% test2 %]</div>'.match(home.templateRe);
            matchedRules[0].should.equal('<div>[% test %]');
            matchedRules[1].should.equal('[% test2 %]');
        });
    });
    
    describe('getPropAccessor', function() {
        var simple = home.templateGenerator(' [% normal %][% _$_$_$$ %][% $1 %][% 12days %][% йцук %][% w@ %]'),
            jpath = home.templateGenerator(' [% normal._$_$_$$.$1.12days.йцук.w@ %]');

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

    describe('jpath', function () {
        var simple = home.templateGenerator(' [% indata %][% inreq %][% inexec %][% nowhere %]'),
            withDots = home.templateGenerator(' [% a.b.c %]'),
            short = home.templateGenerator(' [% a.b %]');
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

            var testTemplate = home.templateGenerator('<div>[% test:blah %]</div>');
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

            var tester = home.templateGenerator('[% data:a %][% req:a %][% data:notfound %][% req: b %][% req:c %]'),
                invoker = home.templateGenerator('invoke [% exec:tester %]+[% exec:notfound %]');

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

            var tester = home.templateGenerator('[% data:vars.a %][% req:vars.a %][% data:vars.notfound %][% req: vars.b %][% req:vars.c %]'),
                invoker = home.templateGenerator('invoke [% exec:tester %]+[% exec:notfound %]');

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

    describe('prefix bem classname', function() {
        var data = {mods: {e: 't'}, mix: 'qq', smth: {mods: {w: 'r'}}},
            testClassname = home.templateGenerator('[% bem:b-block.class %]'),
            testClassname2 = home.templateGenerator('[% bem:smth.b-block2.class %]');

        it('понимает название класса', function() {
            testClassname(data).should.equal('b-block qq b-block_e_t');
        });

        it('понимает указание источника свойств', function() {
            testClassname2(data).should.equal('b-block2 b-block2_w_r');
        });
    });

    describe('prefix bem js', function() {
        var data = {js: {w: 1}, smth: {q: 3}},
            testJs = home.templateGenerator('[% bem:js %]'),
            testJs2 = home.templateGenerator('[% bem:smth.js %]');

        it('работает как ожидается', function() {
            testJs(data).should.equal('{&quot;w&quot;:1}');
        });

        it('понимает указание источника свойств', function() {
            testJs2(data).should.equal('{&quot;q&quot;:3}');
        });
    });

    describe('prefix bem attrs', function() {
        var data = {attrs: {title: 'w', src: 'sdfsdf.png'}, smth: {name: 'q', value: '1'}},
            testAttrs = home.templateGenerator('[% bem:attrs %]'),
            testAttrs2 = home.templateGenerator('[% bem:smth.attrs %]');

        it('работает как ожидается', function() {
            testAttrs(data).should.equal(' title="w" src="sdfsdf.png"');
        });

        it('понимает указание источника свойств', function() {
            testAttrs2(data).should.equal(' name="q" value="1"');
        });
    });
});
