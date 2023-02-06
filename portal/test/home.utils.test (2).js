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
    describe('htmlFilter', function() {
        it('не изменяет пустую строку', function() {
            home.htmlFilter('').should.equal('');
        });

        it('не изменяет текст', function() {
            home.htmlFilter('text').should.equal('text');
        });

        it('преобразует спецсимволы', function() {
            home.htmlFilter('<div>').should.equal('&lt;div&gt;');
            home.htmlFilter('<div data-url="yandex/?text=123&abc">')
                .should.equal('&lt;div data-url=&quot;yandex/?text=123&amp;abc&quot;&gt;');
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

    describe('urlFilter', function() {
        it('нужны тесты');
    });

    describe('decline', function() {
        it('нужны тесты');
    });
    describe('getBEMParams', function() {
        it('нужны тесты');
    });
    describe('getBEMClassname', function() {
        it('нужны тесты');
    });
    describe('getAttributes', function() {
        it('нужны тесты');
    });
    describe('deepExtend', function() {
        it('нужны тесты');
    });
    describe('rnd', function() {
        it('нужны тесты');
    });
    describe('randomInteger', function() {
        it('нужны тесты');
    });

});

