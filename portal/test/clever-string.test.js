import * as cleverString from '../clever-string';

describe('cleverString', function() {
    describe('length', function() {
        it('выполняет граничные условия', function() {
            cleverString.length('').should.equal(0);

            cleverString.length(null).should.equal(0);

            cleverString.length().should.equal(0);
        });

        it('вычисляет длину простой строки', function() {
            cleverString.length('aSdFgH').should.equal(6);

            cleverString.length('   ').should.equal(3);
        });

        it('вычисляет длину строки с сурогатными парами', function() {
            cleverString.length('💩').should.equal(1);

            cleverString.length('💩💩💩💩💩').should.equal(5);

            cleverString.length('a💩b💩c💩d💩e💩f').should.equal(11);

            cleverString.length('💩 : 💩').should.equal(5);

            cleverString.length('abc💩def').should.equal(7);

            cleverString.length('Iñtërnâtiônàlizætiøn☃💩ab').should.equal(24);
        });
    });

    describe('substring', function() {
        it('выполняет граничные условия', function() {
            should.not.exist(cleverString.substring(null, 1, 1));

            should.not.exist(cleverString.substring(null));

            cleverString.substring('', 0).should.equal('');
        });

        it('работает на простых строках', function() {
            cleverString.substring('abcdef', 0).should.equal('abcdef');

            cleverString.substring('abcdefg', 3).should.equal('defg');

            cleverString.substring('abcdefg', 0, 2).should.equal('ab');

            cleverString.substring('abcdefg', 2, 7).should.equal('cdefg');
        });

        it('работает на строках с сурогатными парами', function() {
            cleverString.substring('💩-💩-💩', 0).should.equal('💩-💩-💩');

            cleverString.substring('💩-💩-💩', 3).should.equal('-💩');

            cleverString.substring('💩-💩-💩', 0, 2).should.equal('💩-');

            cleverString.substring('💩-💩-💩', 2, 7).should.equal('💩-💩');

            cleverString.substring('Iñtërnâtiônàlizætiøn☃💩ab', 20, 3).should.equal('☃💩a');
        });
    });

    describe('cutMiddleOfString', function() {
        it('выполняет граничные условия', function() {
            should.not.exist(cleverString.cutMiddleOfString(null, 1));

            should.not.exist(cleverString.cutMiddleOfString());

            cleverString.cutMiddleOfString('', 0, 0).should.equal('');

            cleverString.cutMiddleOfString('', 1, 1).should.equal('');
        });

        it('работает на простых строках', function() {
            cleverString.cutMiddleOfString('простая string', 7, 6).should.equal('простая…string');

            cleverString.cutMiddleOfString('простая string', 5, 0).should.equal('прост…');

            cleverString.cutMiddleOfString('простая string', 10, 10).should.equal('простая string');
        });

        it('работает на строках с сурогатными парами', function() {
            cleverString.cutMiddleOfString('💩-💩-💩', 0, 0).should.equal('…');

            cleverString.cutMiddleOfString('💩-💩-💩', 1, 1).should.equal('💩…💩');

            cleverString.cutMiddleOfString('💩-💩-💩', 0, 2).should.equal('…-💩');

            cleverString.cutMiddleOfString('💩-💩-💩', 3, 2).should.equal('💩-💩-💩');

            cleverString.cutMiddleOfString('Iñtërnâtiônàlizætiøn☃💩ab', 4, 4).should.equal('Iñtë…☃💩ab');
        });
    });

    describe('cutEndOfString', function() {
        it('выполняет граничные условия', function() {
            should.not.exist(cleverString.cutEndOfString(null, 1));

            should.not.exist(cleverString.cutEndOfString());

            cleverString.cutEndOfString('', 0).should.equal('');

            cleverString.cutEndOfString('', 1).should.equal('');
        });

        it('работает на простых строках', function() {
            cleverString.cutEndOfString('простая string', 10).should.equal('простая s…');

            cleverString.cutEndOfString('простая string', 14).should.equal('простая strin…');

            cleverString.cutEndOfString('простая string', 15).should.equal('простая string');
        });

        it('работает на строках с сурогатными парами', function() {
            cleverString.cutEndOfString('💩-💩-💩', 0).should.equal('');

            cleverString.cutEndOfString('💩-💩-💩', 1).should.equal('…');

            cleverString.cutEndOfString('💩-💩-💩', 4).should.equal('💩-💩…');

            cleverString.cutEndOfString('💩-💩-💩', 5).should.equal('💩-💩-…');

            cleverString.cutEndOfString('💩-💩-💩', 6).should.equal('💩-💩-💩');

            cleverString.cutEndOfString('Iñtërnâtiônàlizætiøn☃💩ab', 23).should.equal('Iñtërnâtiônàlizætiøn☃💩…');
        });
    });

    describe('cutStartOfString', function() {
        it('выполняет граничные условия', function() {
            should.not.exist(cleverString.cutStartOfString(null, 1));

            should.not.exist(cleverString.cutStartOfString());

            cleverString.cutStartOfString('', 0).should.equal('');

            cleverString.cutStartOfString('', 1).should.equal('');
        });

        it('работает на простых строках', function() {
            cleverString.cutStartOfString('простая string', 10).should.equal('…ая string');

            cleverString.cutStartOfString('простая string', 14).should.equal('…ростая string');

            cleverString.cutStartOfString('простая string', 15).should.equal('простая string');
        });

        it('работает на строках с сурогатными парами', function() {
            cleverString.cutStartOfString('💩-💩-💩', 0).should.equal('');

            cleverString.cutStartOfString('💩-💩-💩', 1).should.equal('…');

            cleverString.cutStartOfString('💩-💩-💩', 4).should.equal('…💩-💩');

            cleverString.cutStartOfString('💩-💩-💩', 5).should.equal('…-💩-💩');

            cleverString.cutStartOfString('💩-💩-💩', 6).should.equal('💩-💩-💩');

            cleverString.cutStartOfString('Iñtërnâtiônàlizætiøn☃💩ab', 23).should.equal('…tërnâtiônàlizætiøn☃💩ab');
        });
    });
});
