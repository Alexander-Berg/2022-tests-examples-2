var expect = require('expect.js');
var sinon = require('sinon');

var Logger = require('../../logger/Logger');
var Configurator = require('../../logger/Configurator');

describe('AbstractHandler', function() {
    beforeEach(function() {
        this.config = Configurator.instance();
        this.Handler = require('../../logger/handler/AbstractHandler');
        this.handler = new this.Handler(this.config);

        this.logId = 'gub1pee5xe8quie3uThiez2aiz4aeC4j';
        this.entry = Logger.log().logId(this.logId);

        this.sinon = sinon.sandbox.create();
        this.sinon.stub(this.handler, '_handle');
    });
    afterEach(function() {
        this.sinon.restore();
    });

    describe('constructor', function() {
        it('should throw if first argument is not an instance of Configurator', function() {
            var Handler = this.Handler;

            expect(function() {
                new Handler();
            }).to.throwError(function(err) {
                expect(err.message).to.be('Configuration should be an instance of Configurator');
            });
        });
    });

    describe('handle', function() {
        it('should throw if argument is not an instance of LogEntry', function() {
            var handler = this.handler;

            expect(function() {
                handler.handle();
            }).to.throwError(function(err) {
                expect(err.message).to.be('Entry should be a LogEntry');
            });
        });

        describe('when entry is important', function() {
            beforeEach(function() {
                this.originalMinLevel = this.config.getCurrentMinLevel();
                this.config.minLevel(Configurator.knownLevels[1]);

                this.entryLevel = Configurator.knownLevels[0];
                this.entry.level(this.entryLevel);
            });
            afterEach(function() {
                this.config.minLevel(this.originalMinLevel);
            });

            it('should throw if logId is required for the level and entry has none', function() {
                var entry = Logger.log().level(this.entryLevel);
                var handler = this.handler;

                expect(function() {
                    handler.handle(entry);
                }).to.throwError(function(err) {
                    expect(err.message).to.be('Log ID should be specified for log level ' + entry.getLevel());
                });
            });

            it('should pass entry to _handle', function() {
                this.handler.handle(this.entry);
                expect(this.handler._handle.calledOnce).to.be(true);
                expect(this.handler._handle.calledWithExactly(this.entry)).to.be(true);
            });
        });

        describe('when entry is not important enough', function() {
            beforeEach(function() {
                this.originalMinLevel = this.config.getCurrentMinLevel();
                this.config.minLevel(Configurator.knownLevels[0]);

                this.entryLevel = Configurator.knownLevels[1];
                this.entry.level(this.entryLevel);
            });
            afterEach(function() {
                this.config.minLevel(this.originalMinLevel);
            });

            it('should not call _handle', function() {
                this.handler.handle(this.entry);
                expect(this.handler._handle.called).to.be(false);
            });
        });
    });
});
