var expect = require('expect.js');
var sinon = require('sinon');

var Logger = require('../../logger/Logger');
var Configurator = require('../../logger/Configurator');

describe('ProductionFormatter', function() {
    beforeEach(function() {
        this.sinon = sinon.sandbox.create();

        this.config = Configurator.instance();
        this.Formatter = require('../../logger/formatter/ProductionFormatter');
        this.formatter = new this.Formatter(this.config);

        this.entry = Logger.log();
    });
    afterEach(function() {
        this.sinon.restore();
    });

    describe('_format', function() {
        beforeEach(function() {
            this.tsRe = /\[\[.+?]]/;
            this.levelRe = /]].*?:/;
        });

        it('should format time', function() {
            this.sinon.stub(this.entry, 'getTimestamp').returns(0);

            // I've been lazy writing this test.
            // If you ever run this in a UTC-X timezone (with negative offset) —
            // do rewrite the test
            var expected = new Date(0);

            expect(this.formatter._format(this.entry).match(this.tsRe)[0]).to.be(
                '[[01-01T' + require('lodash').padStart(expected.getHours(), 2, '0') + ':00:00.000]]'
            );
        });

        it('should output time to a uniform length', function() {
            this.sinon
                .stub(this.entry, 'getTimestamp')
                .onFirstCall()
                .returns(0)
                .onSecondCall()
                .returns(new Date().getTime());

            var first = this.formatter._format(this.entry).match(this.tsRe)[0];
            var second = this.formatter._format(this.entry).match(this.tsRe)[0];

            expect(first.length).to.be(second.length);
        });

        it('should output the loglevel padded to the biggest known level length', function() {
            var maxLength = require('lodash').max(this.config.getKnownLevels(), function(level) {
                return level.length;
            }).length;

            this.sinon.stub(this.entry, 'getLevel').returns('a');
            var expected = new Array(maxLength).join(' ') + 'A'; //Padded + uppercase

            //Matching artifacts added
            expect(this.formatter._format(this.entry).match(this.levelRe)[0]).to.be(']] ' + expected + ':');
        });
    });
});
