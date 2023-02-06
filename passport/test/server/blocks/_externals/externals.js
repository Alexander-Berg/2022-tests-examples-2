var expect = require('expect.js');
var sinon = require('sinon');
var when = require('when');
var _ = require('lodash');

var yr = {externals: {}};
require('../../../../blocks/_externals/externals.js')(yr);

describe('Yate externals', function() {
    describe('format', function() {
        beforeEach(function() {
            this.format = yr.externals.format;
        });
        it('should format the strings with given args', function() {
            expect(this.format('I can\'t %s my %s', 'get', 'satisfaction'))
                .to.be('I can\'t get my satisfaction');
        });
    });
});
