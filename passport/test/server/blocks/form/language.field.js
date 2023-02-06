var expect = require('expect.js');
var LangField = require('../../../../blocks/form/language.field');

describe('Language Field', function() {
    beforeEach(function() {
        this.field = new LangField();
    });

    describe('compile', function() {
        it('should return a value matching the input', function() {
            var field = this.field;

            ['ru', 'en', 'uk', 'tr'].forEach(function(lang) {
                expect(field.compile(lang).value).to.be(lang);
            });
        });
    });
});
