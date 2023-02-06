require('should');
const strToFunction = require('../../view-transforms/str-to-function');


describe('str-to-function', () => {

    it('should work', () => {
        strToFunction('fileName.js', 'views("a", function() {var a = 1;})', {})
            .should.equal('views("a", function() {var a = 1;})');
    });

    it('should work with arguments', () => {
        strToFunction('fileName.js', 'views("a", function() {var a = arguments;})', {})
            .should.equal('views("a", function() {var a = arguments;})');
    });

    it('should catch invalid assignment', () => {
        try {
            strToFunction('fileName.js', 'views("a", function() {var a = b;})', {});
            throw new Error('NoError');
        } catch (err) {
            err.message.should.equal('In file (fileName.js): invalid value of a');
        }

    });

});
