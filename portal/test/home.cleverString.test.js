/* globals should */

describe('home.cleverString', function() {
    describe('length', function() {
        it('выполняет граничные условия', function() {
            home.cleverString.length('').should.equal(0);

            home.cleverString.length(null).should.equal(0);

            home.cleverString.length().should.equal(0);
        });

        it('вычисляет длину простой строки', function() {
            home.cleverString.length('aSdFgH').should.equal(6);

            home.cleverString.length('   ').should.equal(3);
        });

        it('вычисляет длину строки с сурогатными парами', function() {
            home.cleverString.length('💩').should.equal(1);

            home.cleverString.length('💩💩💩💩💩').should.equal(5);

            home.cleverString.length('a💩b💩c💩d💩e💩f').should.equal(11);

            home.cleverString.length('💩 : 💩').should.equal(5);

            home.cleverString.length('abc💩def').should.equal(7);

            home.cleverString.length('Iñtërnâtiônàlizætiøn☃💩ab').should.equal(24);
        });
    });

    describe('substring', function() {
        it('выполняет граничные условия', function() {
            should.not.exist(home.cleverString.substring(null, 1, 1));

            should.not.exist(home.cleverString.substring(null));

            home.cleverString.substring('', 0).should.equal('');
        });

        it('работает на простых строках', function() {
            home.cleverString.substring('abcdef', 0).should.equal('abcdef');

            home.cleverString.substring('abcdefg', 3).should.equal('defg');

            home.cleverString.substring('abcdefg', 0, 2).should.equal('ab');

            home.cleverString.substring('abcdefg', 2, 7).should.equal('cdefg');
        });

        it('работает на строках с сурогатными парами', function() {
            home.cleverString.substring('💩-💩-💩', 0).should.equal('💩-💩-💩');

            home.cleverString.substring('💩-💩-💩', 3).should.equal('-💩');

            home.cleverString.substring('💩-💩-💩', 0, 2).should.equal('💩-');

            home.cleverString.substring('💩-💩-💩', 2, 7).should.equal('💩-💩');

            home.cleverString.substring('Iñtërnâtiônàlizætiøn☃💩ab', 20, 3).should.equal('☃💩a');
        });
    });

    describe('cutMiddleOfString', function() {
        it('выполняет граничные условия', function() {
            should.not.exist(home.cleverString.cutMiddleOfString(null, 1));

            should.not.exist(home.cleverString.cutMiddleOfString());

            home.cleverString.cutMiddleOfString('', 0, 0).should.equal('');

            home.cleverString.cutMiddleOfString('', 1, 1).should.equal('');
        });

        it('работает на простых строках', function() {
            home.cleverString.cutMiddleOfString('простая string', 7, 6).should.equal('простая string');

            home.cleverString.cutMiddleOfString('простая что-то между string', 7, 6).should.equal('простая…string');

            home.cleverString.cutMiddleOfString('простая string', 5, 0).should.equal('прост…');

            home.cleverString.cutMiddleOfString('простая string', 10, 10).should.equal('простая string');
        });

        it('работает на строках с сурогатными парами', function() {
            home.cleverString.cutMiddleOfString('💩-💩-💩', 0, 0).should.equal('…');

            home.cleverString.cutMiddleOfString('💩-💩-💩', 1, 1).should.equal('💩…💩');

            home.cleverString.cutMiddleOfString('💩-💩-💩', 0, 2).should.equal('…-💩');

            home.cleverString.cutMiddleOfString('💩-💩-💩', 3, 2).should.equal('💩-💩-💩');

            home.cleverString.cutMiddleOfString('Iñtërnâtiônàlizætiøn☃💩ab', 4, 4).should.equal('Iñtë…☃💩ab');
        });
    });

    describe('cutEndOfString', function() {
        it('выполняет граничные условия', function() {
            should.not.exist(home.cleverString.cutEndOfString(null, 1));

            should.not.exist(home.cleverString.cutEndOfString());

            home.cleverString.cutEndOfString('', 0).should.equal('');

            home.cleverString.cutEndOfString('', 1).should.equal('');
        });

        it('работает на простых строках', function() {
            home.cleverString.cutEndOfString('простая string', 10).should.equal('простая s…');

            home.cleverString.cutEndOfString('простая string', 13).should.equal('простая stri…');

            home.cleverString.cutEndOfString('простая string', 14).should.equal('простая string');

            home.cleverString.cutEndOfString('простая string', 15).should.equal('простая string');
        });

        it('работает на строках с сурогатными парами', function() {
            home.cleverString.cutEndOfString('💩-💩-💩', 0).should.equal('');

            home.cleverString.cutEndOfString('💩-💩-💩', 1).should.equal('…');

            home.cleverString.cutEndOfString('💩-💩-💩', 3).should.equal('💩-…');

            home.cleverString.cutEndOfString('💩-💩-💩', 4).should.equal('💩-💩…');

            home.cleverString.cutEndOfString('💩-💩-💩', 5).should.equal('💩-💩-💩');

            home.cleverString.cutEndOfString('💩-💩-💩', 6).should.equal('💩-💩-💩');

            home.cleverString.cutEndOfString('Iñtërnâtiônàlizætiøn☃💩ab', 23).should.equal('Iñtërnâtiônàlizætiøn☃💩…');
        });
    });

    describe('cutStartOfString', function() {
        it('выполняет граничные условия', function() {
            should.not.exist(home.cleverString.cutStartOfString(null, 1));

            should.not.exist(home.cleverString.cutStartOfString());

            home.cleverString.cutStartOfString('', 0).should.equal('');

            home.cleverString.cutStartOfString('', 1).should.equal('');
        });

        it('работает на простых строках', function() {
            home.cleverString.cutStartOfString('простая string', 10).should.equal('…ая string');

            home.cleverString.cutStartOfString('простая string', 14).should.equal('простая string');
        });

        it('работает на строках с сурогатными парами', function() {
            home.cleverString.cutStartOfString('💩-💩-💩', 0).should.equal('');

            home.cleverString.cutStartOfString('💩-💩-💩', 1).should.equal('…');

            home.cleverString.cutStartOfString('💩-💩-💩', 4).should.equal('…💩-💩');

            home.cleverString.cutStartOfString('💩-💩-💩', 5).should.equal('💩-💩-💩');

            home.cleverString.cutStartOfString('Iñtërnâtiônàlizætiøn☃💩ab', 23).should.equal('…tërnâtiônàlizætiøn☃💩ab');
        });
    });
});
