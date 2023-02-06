describe('home.util', function() {
    describe('capitalize', function() {
        it('не изменяет пустую строку', function() {
            home.capitalize('').should.equal('');
        });

        it('работает на одной букве', function() {
            home.capitalize('a').should.equal('A');
        });

        it('работает на английской строке', function() {
            home.capitalize('abc').should.equal('Abc');
        });

        it('работает на русской строке', function() {
            home.capitalize('петя').should.equal('Петя');
        });
    });

    describe('ltgtFilter', function() {
        it('не изменяет пустую строку', function() {
            home.ltgtFilter('').should.equal('');
        });

        it('не изменяет текст', function() {
            home.ltgtFilter('text').should.equal('text');
        });

        it('преобразует спецсимволы', function() {
            home.ltgtFilter('<div>').should.equal('&lt;div&gt;');
            home.ltgtFilter('<div data-url="yandex/?text=123&abc">')
                .should.equal('&lt;div data-url="yandex/?text=123&abc"&gt;');
        });
    });

    describe('encodeParams', function() {
        it('работает с пустым объектом', function() {
            home.encodeParams({}).should.equal('{}');
        });
        it('работает с не пустым объектом', function() {
            home.encodeParams({a: 3}).should.equal("{'a':3}");
            home.encodeParams({
                a: 'abc',
                b: undefined,
                c: '456'
            }).should.equal("{'a':'abc','c':'456'}");
        });
    });

    describe('getJPathValue', function() {
        var egDATA = {
            a: {
                c: 1,
                x: 234,
                y: {
                    m: 'w'
                }
            },
            b: 'hello world',
            'e:g': 'omg'
        };

        it('понимает простые конструкции', function() {
            home.getJPathValue(egDATA, 'a.c').should.equal(1);
            home.getJPathValue(egDATA, 'a.x').should.equal(234);
            home.getJPathValue(egDATA, 'a.y.m').should.equal('w');
            home.getJPathValue(egDATA, 'b').should.equal('hello world');
            home.getJPathValue(egDATA, 'e:g').should.equal('omg');
        });
    });

    describe('formatNumber', function() {
        it('should format', function () {
            home.formatNumber(1).should.equal('1');
            home.formatNumber(1.23).should.equal('1,23');
            home.formatNumber(1.23456789).should.equal('1,23456789');
            home.formatNumber(1000).should.equal('1&nbsp;000');
            home.formatNumber(10000).should.equal('10&nbsp;000');
            home.formatNumber(123456).should.equal('123&nbsp;456');
            home.formatNumber(1234567).should.equal('1&nbsp;234&nbsp;567');
            home.formatNumber(12345678).should.equal('12&nbsp;345&nbsp;678');
            home.formatNumber(12345678.12345678).should.equal('12&nbsp;345&nbsp;678,12345678');
        });

        it('should format with delimiter', function () {
            home.formatNumber(18, ':').should.equal('18');
            home.formatNumber(18.30, ':').should.equal('18:3');
        });

        it('should format with thousands delimiter', function () {
            home.formatNumber(123456, undefined, '_').should.equal('123_456');
        });
    });

    describe('deepExtend', function() {
        it('should extend', function () {
            home.deepExtend({}, {abc: 123}).should.deep.equal({abc: 123});
        });

        it('should return base', function () {
            var base = {};
            home.deepExtend(base, {abc: 123}).should.equal(base);
        });

        it('should override props', function () {
            var base = {
                abc: 456
            };
            home.deepExtend(base, {abc: 123, def: true}).should.deep.equal({abc: 123, def: true});
        });

        it('should extend inner arrays', function () {
            home.deepExtend({}, {a: [1, 2, 3]}).should.deep.equal({a: [1, 2, 3]});

            var base = {a: [4, 5, 6], b: 7};
            var extender = {a: [1, 2, 3]};
            home.deepExtend(base, extender).should.deep.equal({b: 7, a: [1, 2, 3]});
            home.deepExtend(base, extender).a.should.deep.equal(extender.a);
            home.deepExtend(base, extender).a.should.not.equal(extender.a);

            home.deepExtend({a: [1, 2, 3]}, {a: [4]}).should.deep.equal({a: [4, 2, 3]});
            home.deepExtend({a: [1, 2, 3]}, {a: [{b: 7}]}).should.deep.equal({a: [{b: 7}, 2, 3]});
            home.deepExtend({a: [{b: 4, c: 5}, 2, 3]}, {a: [{b: 7, d: 8}]}).should.deep.equal({a: [{b: 7, c: 5, d: 8}, 2, 3]});
        });

        it('should extend inner objects', function () {
            var extender = {
                a: {
                    b: true
                }
            };
            var res = home.deepExtend({}, extender);
            res.should.deep.equal({a: {b: true}});
            res.a.should.not.equal(extender.a);
            res.a.should.deep.equal(extender.a);
        });

        it('should extend inner dates and functions', function () {
            var base = {
                a: {
                    c: 123
                }
            };
            var extender = {
                a: {
                    b: true
                },
                d: new Date(),
                e: function () {}
            };
            var res = home.deepExtend(base, extender);
            res.should.deep.equal({
                a: {
                    b: true,
                    c: 123
                },
                d: extender.d,
                e: extender.e
            });
        });

        it('should extend with null', function () {
            var base = {
                abc: 123,
                def: 456
            };

            home.deepExtend(base, {abc: null});

            base.should.deep.equal({
                abc: null,
                def: 456
            });
        });

        it('should not process __proto__', function () {
            var base = {
                abc: 123,
                def: 456
            };

            var extended = Object.create(base);

            extended.foo = 789;

            home.deepExtend(extended, JSON.parse('{"__proto__": {"extra": "new"}}'));

            base.should.deep.equal({
                abc: 123,
                def: 456
            });
        });
    });

    describe('rnd', function() {
        var orig;

        beforeEach(function () {
            orig = Math.random;

            var i = 0,
                arr = [
                    0.1,
                    0.123456789,
                    0.23456789,
                    0.3456789
                ];

            Math.random = function () {
                var res = arr[i++];
                i = i % arr.length;
                return res;
            };
        });

        afterEach(function () {
            Math.random = orig;
        });

        it('should return rnd id', function () {
            home.rnd().should.equal('1');
            home.rnd().should.equal('123456789');
            home.rnd().should.equal('23456789');
            home.rnd().should.equal('3456789');
            home.rnd().should.equal('1');
        });
    });

    describe('randomInteger', function() {
        var orig;

        beforeEach(function () {
            orig = Math.random;

            var i = 0,
                arr = [
                    0.1,
                    0.123456789,
                    0.23456789,
                    0.3456789,
                    0,
                    0.9999999999999
                ];

            Math.random = function () {
                var res = arr[i++];
                i = i % arr.length;
                return res;
            };
        });

        afterEach(function () {
            Math.random = orig;
        });

        it('should return random int', function () {
            home.randomInteger(0, 1).should.equal(0);
            home.randomInteger(0, 2).should.equal(0);
            home.randomInteger(0, 10).should.equal(2);
            home.randomInteger(0, 10).should.equal(3);
            home.randomInteger(0, 100).should.equal(0);
            home.randomInteger(0, 100).should.equal(100);
        });
    });
});

