var expect = require('expect.js');
var utils = require('../utils');

describe('flatten object', function() {
    it('Should return empty object if called without arguments', function() {
        expect(utils.flattenObject()).to.eql({});
    });

    it('Should return the same object if argument is not nested object', function() {
        var testObj = {
            foo: 'foo',
            bar: 1,
            buz: undefined,
            doubles: null
        };

        expect(utils.flattenObject(testObj)).to.eql(testObj);
    });

    it('Should return flattened object if argument is nested object', function() {
        var testObj = {
            foo: {
                foo: 'foo'
            },
            bar: {
                bar: {
                    bar: 'bar'
                }
            },
            baz: 'baz'
        };
        var expectedObj = {
            baz: 'baz',
            'foo.foo': 'foo',
            'bar.bar.bar': 'bar'
        };

        expect(utils.flattenObject(testObj)).to.eql(expectedObj);
    });

    it('Should not flatten array', function() {
        var testObj = {
            foo: [1, 2, 3]
        };

        expect(utils.flattenObject(testObj)).to.eql(testObj);
    });
});
