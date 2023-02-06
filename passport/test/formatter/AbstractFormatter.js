var expect = require('expect.js');
var sinon = require('sinon');

var Logger = require('../../logger/Logger');
var Configurator = require('../../logger/Configurator');

describe('AbstractFormatter', function() {
    beforeEach(function() {
        this.config = Configurator.instance();
        this.Formatter = require('../../logger/formatter/AbstractFormatter');
        this.formatter = new this.Formatter(this.config);

        this.entry = Logger.log();

        this.sinon = sinon.sandbox.create();
        this.sinon.stub(this.formatter, '_format');
    });
    afterEach(function() {
        this.sinon.restore();
    });

    describe('constructor', function() {
        it('should throw if first argument is not an instance of Configurator', function() {
            var Formatter = this.Formatter;

            expect(function() {
                new Formatter();
            }).to.throwError(function(err) {
                expect(err.message).to.be('Configuration should be an instance of Configurator');
            });
        });
    });

    describe('format', function() {
        it('should throw if argument is not an instance of LogEntry', function() {
            var formatter = this.formatter;

            expect(function() {
                formatter.format();
            }).to.throwError(function(err) {
                expect(err.message).to.be('Entry should be a LogEntry');
            });
        });

        it('should pass logEntry to _format', function() {
            this.formatter.format(this.entry);
            expect(this.formatter._format.calledOnce).to.be(true);
            expect(this.formatter._format.calledWithExactly(this.entry));
        });
    });
});
