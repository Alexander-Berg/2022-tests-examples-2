/* eslint dot-notation: 0, no-unused-expressions: 0 */
describe('home.removeTag', function () {
    it('Removing tag from text', function() {
        home.removeTag('span', '<span>Hello</span> world!').should.equal('Hello world!');
        home.removeTag('a', '<aside><a href="http://www.moscow.ru" style="color: red;">Moscow</a> is the capital of <a href="http://www.ru">Russia!</a></aside>')
            .should.equal('<aside>Moscow is the capital of Russia!</aside>');
    });
});
