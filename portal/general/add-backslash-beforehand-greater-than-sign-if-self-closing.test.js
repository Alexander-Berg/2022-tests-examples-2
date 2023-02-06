const {addBackslashBeforeGreaterThanSignIfSelfClosing} = require('./template-to-jsx-transform');
const {assert} = require('chai');

describe('addBackslashBeforehandGreaterThanSignIfSelfClosing', () => {
    it('should do nothing if no elements', () => {
        const string = "'abacaba'";
        const modifiedString = addBackslashBeforeGreaterThanSignIfSelfClosing(string);
        assert.equal(string, modifiedString);
    });
    it('test 2', () => {
        const string = '<img>';
        const modifiedString = addBackslashBeforeGreaterThanSignIfSelfClosing(string);
        assert.equal(modifiedString, '<img/>');
    });
    it('test 3', () => {
        const string = '<img><img>';
        const modifiedString = addBackslashBeforeGreaterThanSignIfSelfClosing(string);
        assert.equal(modifiedString, '<img/><img/>');
    });
    it('test 4', () => {
        const string = '<img><input>';
        const modifiedString = addBackslashBeforeGreaterThanSignIfSelfClosing(string);
        assert.equal(modifiedString, '<img/><input/>');
    });
    it('test 5', () => {
        const string = '<img/>';
        const modifiedString = addBackslashBeforeGreaterThanSignIfSelfClosing(string);
        assert.equal(modifiedString, '<img/>');
    });
    it('test 6', () => {
        const string = "<img atr='>'/>";
        const modifiedString = addBackslashBeforeGreaterThanSignIfSelfClosing(string);
        assert.equal(modifiedString, "<img atr='>'/>");
    });
    it('test 7', () => {
        const string = '<img atr=">"/>';
        const modifiedString = addBackslashBeforeGreaterThanSignIfSelfClosing(string);
        assert.equal(modifiedString, '<img atr=">"/>');
    });
    it('tag name start with as col', () => {
        const string = '<colgroup>[% data:cols %]</colgroup>';
        const modifiedString = addBackslashBeforeGreaterThanSignIfSelfClosing(string);
        assert.equal(modifiedString, '<colgroup>[% data:cols %]</colgroup>');
    });
});