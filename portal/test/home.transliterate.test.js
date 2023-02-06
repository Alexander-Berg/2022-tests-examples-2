/* eslint no-unused-expressions: 0 */
describe('home.transliterate', function() {
    it('should transliterate', function () {
        home.transliterate('Человеко-месяц').should.equal('CHeloveko-mesyac');
        home.transliterate('Популярное').should.equal('Populyarnoe');
        home.transliterate('Для детей').should.equal('Dlya detey');
        home.transliterate('Найдётся всё').should.equal('Naydetsya vse');
    });
});
