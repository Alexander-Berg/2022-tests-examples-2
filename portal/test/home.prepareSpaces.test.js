/* eslint dot-notation: 0, no-unused-expressions: 0 */
describe('home.prepareSpaces', function () {
    it('пробел после предлога', function() {
        home.prepareSpaces('').should.equal('');
        home.prepareSpaces('   ').should.equal('   ');
        home.prepareSpaces('abc').should.equal('abc');
        home.prepareSpaces('a b').should.equal('a&nbsp;b');
        home.prepareSpaces('a Ё').should.equal('a&nbsp;Ё');
        home.prepareSpaces('Её ноутбук').should.equal('Её&nbsp;ноутбук');
        home.prepareSpaces('abc bcd').should.equal('abc bcd');
        home.prepareSpaces('a bcd').should.equal('a&nbsp;bcd');
        home.prepareSpaces('Abc something as abc a bcd').should.equal('Abc something as&nbsp;abc a&nbsp;bcd');
        home.prepareSpaces('Квартиры на ул. Мосфильмовская, 1 https://yandex.ru').should.equal('Квартиры на&nbsp;ул. Мосфильмовская, 1 https://yandex.ru');
    });
});

describe('home.prepareSpaces.digits', function() {
    it('пробел внутри числа', function() {
        home.prepareSpaces.digits('').should.equal('');
        home.prepareSpaces.digits('  ').should.equal('  ');
        home.prepareSpaces.digits('a b').should.equal('a b');
        home.prepareSpaces.digits('1 000').should.equal('1&nbsp;000');
        home.prepareSpaces.digits('21 50').should.equal('21&nbsp;50');
        home.prepareSpaces.digits('12 345 678').should.equal('12&nbsp;345&nbsp;678');
        home.prepareSpaces.digits('abc 1 234').should.equal('abc 1&nbsp;234');
        home.prepareSpaces.digits('34 56 abc 1 234 d fre').should.equal('34&nbsp;56 abc 1&nbsp;234 d fre');
    });
});

describe('home.prepareSpaces.punctuation', function() {
    it('пробел перед знаками пунктуации', function() {
        home.prepareSpaces.punctuation('').should.equal('');
        home.prepareSpaces.punctuation('  ').should.equal('  ');
        home.prepareSpaces.punctuation('a b').should.equal('a b');
        home.prepareSpaces.punctuation('ab!').should.equal('ab!');
        home.prepareSpaces.punctuation('a , ').should.equal('a&nbsp;, ');
        home.prepareSpaces.punctuation('abc ! dfgh').should.equal('abc&nbsp;! dfgh');
        home.prepareSpaces.punctuation('abc  !').should.equal('abc  !');
        home.prepareSpaces.punctuation('Abc :) deh ! 1 dfh - d fre  !').should.equal('Abc&nbsp;:) deh&nbsp;! 1 dfh&nbsp;- d fre  !');
        home.prepareSpaces.punctuation('<hl>Натяжной</hl> <hl>потолок</hl> -<hl>Звездное</hl> <hl>небо</hl>. Жми!')
            .should.equal('<hl>Натяжной</hl> <hl>потолок</hl> -<hl>Звездное</hl> <hl>небо</hl>. Жми!');
    });
});

describe('home.prepareSpaces.shortEnding', function() {
    it('пробел перед коротким словом в конце предложения', function() {
        home.prepareSpaces.shortEnding('').should.equal('');
        home.prepareSpaces.shortEnding('  ').should.equal('  ');
        home.prepareSpaces.shortEnding('a b').should.equal('a&nbsp;b');
        home.prepareSpaces.shortEnding('ab!').should.equal('ab!');
        home.prepareSpaces.shortEnding('a , ').should.equal('a , ');
        home.prepareSpaces.shortEnding('a 22').should.equal('a&nbsp;22');
        home.prepareSpaces.shortEnding('a р.').should.equal('a&nbsp;р.');
    });
});

describe('home.prepareSpaces.aroundHyphen', function() {
    it('пробел перед коротким словом в конце предложения', function() {
        home.prepareSpaces.aroundHyphen('').should.equal('');
        home.prepareSpaces.aroundHyphen('  ').should.equal('  ');
        home.prepareSpaces.aroundHyphen('a-b').should.equal('<nobr>a-b</nobr>');
        home.prepareSpaces.aroundHyphen('ab!').should.equal('ab!');
        home.prepareSpaces.aroundHyphen('a - b').should.equal('a - b');
        home.prepareSpaces.aroundHyphen('в р-не').should.equal('в <nobr>р-не</nobr>');
    });
});

describe('home.prepareSpaces.full', function() {
    it('пробелы в числах, после предлогов, перед знаками пунктуации - все вместе', function() {
        home.prepareSpaces.full('').should.equal('');
        home.prepareSpaces.full('  ').should.equal('  ');
        home.prepareSpaces.full('a b').should.equal('a&nbsp;b');
        home.prepareSpaces.full('ab!').should.equal('ab!');
        home.prepareSpaces.full('a , ').should.equal('a&nbsp;, ');
        home.prepareSpaces.full('abc ! dfgh').should.equal('abc&nbsp;! dfgh');
        home.prepareSpaces.full('Abc :) deh ! 1 345 dfh - d fre  !').should.equal('Abc&nbsp;:) deh&nbsp;! 1&nbsp;345 dfh&nbsp;- d&nbsp;fre  !');
        home.prepareSpaces.full('Abc :) deh ! 1 345 d-fh - d fre d').should.equal('Abc&nbsp;:) deh&nbsp;! 1&nbsp;345 <nobr>d-fh</nobr>&nbsp;- d&nbsp;fre&nbsp;d');
    });
});
