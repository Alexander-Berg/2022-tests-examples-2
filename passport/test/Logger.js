var expect = require('expect.js');
var sinon = require('sinon');

var Logger = require('../logger/Logger');
var Configurator = require('../logger/Configurator');
var Entry = require('../logger/Entry');

describe('Logger', function() {
    beforeEach(function() {
        this.config = Configurator.instance();
        this.sinon = sinon.sandbox.create();
    });
    afterEach(function() {
        this.sinon.restore();
    });

    describe('static', function() {
        describe('configure', function() {
            it('should expose Configurator.instance method', function() {
                expect(Logger.configure).to.be(Configurator.instance);
            });
        });

        describe('log', function() {
            it('should return a logEntry', function() {
                expect(Logger.log()).to.be.an(Entry);
            });

            it('should instantiate the logEntry with a formatter from config', function() {
                expect(Logger.log().getFormatter()).to.be(this.config.getFormatter());
            });

            it('should instantiate the logEntry with a handler from config', function() {
                expect(Logger.log().getHandler()).to.be(this.config.getHandler());
            });
        });

        Configurator.knownLevels.forEach(function(level) {
            describe(level, function() {
                it('should return a logEntry from Logger.log', function() {
                    var configuration = Configurator.instance();
                    var entry = new Entry(configuration.getFormatter(), configuration.getHandler());

                    this.sinon.stub(Logger, 'log').returns(entry);

                    expect(Logger[level]()).to.be(entry);
                });

                it('should set a level for the logEntry', function() {
                    expect(Logger[level]().getLevel()).to.be(level);
                });
            });
        });
    });

    describe('instance', function() {
        beforeEach(function() {
            this.logId = 'Akeich0ohsieghahtaich5laerang1ep';
            this.typeHierarchy = ['type', 'subtype', 'sub-sub'];

            this.logger = new (Logger.bind.apply(Logger, [Logger, this.logId].concat(this.typeHierarchy)))();
        });

        describe('constructor', function() {
            it('should set a logId from a first argument', function() {
                expect(this.logger.getLogId()).to.be(this.logId);
            });

            it('should set a type hierarchy from the rest of the arguments', function() {
                expect(this.logger.getType()).to.eql(this.typeHierarchy);
            });
        });

        describe('type', function() {
            it('should append the hierarchy to the current type hierarchy', function() {
                this.logger.type('additional', 'hierarchy');
                expect(this.logger.getType()).to.eql(this.typeHierarchy.concat(['additional', 'hierarchy']));
            });
        });

        Configurator.knownLevels.forEach(function(level) {
            describe(level, function() {
                beforeEach(function() {
                    var configuration = Configurator.instance();

                    this.entry = new Entry(configuration.getFormatter(), configuration.getHandler());
                });
                it('should return a logEntry from Logger.' + level, function() {
                    this.sinon.stub(Logger, level).returns(this.entry);
                    expect(this.logger[level]()).to.be(this.entry);
                });

                it('should set a type for the logEntry', function() {
                    expect(this.logger[level]().getType()).to.eql(this.typeHierarchy);
                });

                it('should set log id for the entry if it is defined', function() {
                    expect(this.logger[level]().getLogId()).to.eql(this.logId);
                });

                it('should not call entry.logId if no logId was defined', function() {
                    this.sinon.stub(this.entry, 'logId');
                    this.sinon.stub(Logger, level).returns(this.entry);

                    new Logger()[level]();
                    expect(this.entry.logId.called).to.be(false);
                });

                it("should pass arguments to entry's write if called with any", function() {
                    this.sinon.stub(this.entry, 'write');
                    this.sinon.stub(Logger, level).returns(this.entry);

                    this.logger[level]('one', 'two', 'three');
                    expect(this.entry.write.calledOnce).to.be(true);
                    expect(this.entry.write.calledWithExactly('one', 'two', 'three')).to.be(true);
                });

                it('should not call write if called with no arguments', function() {
                    this.sinon.stub(this.entry, 'write');
                    this.sinon.stub(Logger, level).returns(this.entry);

                    this.logger[level]();
                    expect(this.entry.write.called).to.be(false);
                });
            });
        });
    });
});

describe('Entry', function() {
    beforeEach(function() {
        this.formatter = Configurator.instance().getFormatter();
        this.handler = Configurator.instance().getHandler();
        this.entry = new Entry(this.formatter, this.handler);

        this.sinon = sinon.sandbox.create();
        this.sinon.stub(this.handler, 'handle');
    });
    afterEach(function() {
        this.sinon.restore();
    });

    describe('constructor', function() {
        it('should throw if formatter is not a LogFormatter', function() {
            var that = this;

            expect(function() {
                new Entry('nope', that.handler);
            }).to.throwError(function(err) {
                expect(err.message).to.be('Formatter should be a LogFormatter');
            });
        });

        it('should throw if handler is not a LogHandler', function() {
            var that = this;

            expect(function() {
                new Entry(that.formatter, 'nope');
            }).to.throwError(function(err) {
                expect(err.message).to.be('Handler should be a LogHandler');
            });
        });
    });

    describe('level', function() {
        beforeEach(function() {
            this.level = Configurator.knownLevels[0];
        });

        it('should set level', function() {
            expect(this.entry.level(this.level).getLevel()).to.be(this.level);
        });

        it('should throw if given an unkonwn level', function() {
            var entry = this.entry;

            expect(function() {
                entry.level('unknown');
            }).to.throwError(function(err) {
                expect(err.message).to.be(
                    'Level should be one of: %s'.replace('%s', Configurator.knownLevels.join(', '))
                );
            });
        });
    });

    describe('type', function() {
        it('should throw if any type from hierarchy is not a string', function() {
            var entry = this.entry;

            expect(function() {
                entry.type('one', {}, 'three');
            }).to.throwError(function(err) {
                expect(err.message).to.be('Type should be a string');
            });
        });

        it('should set a type hierarchy on an entry', function() {
            expect(this.entry.type('one', 'two', 'three').getType()).to.eql(['one', 'two', 'three']);
        });

        it('should extend a type hierarchy on an entry if there already is one', function() {
            expect(
                this.entry
                    .type('one')
                    .type('two', 'three')
                    .getType()
            ).to.eql(['one', 'two', 'three']);
        });
    });

    describe('logId', function() {
        beforeEach(function() {
            this.logId = 'Quae7deeV8chiu8eigh7oobaebae6kie';
        });

        it('should throw if argument given is not a string', function() {
            var entry = this.entry;

            expect(function() {
                entry.logId(false);
            }).to.throwError(function(err) {
                expect(err.message).to.be('Log ID should be a string');
            });
        });

        it('should set logId', function() {
            expect(this.entry.logId(this.logId).getLogId()).to.be(this.logId);
        });
    });

    describe('write', function() {
        beforeEach(function() {
            this.level = Configurator.knownLevels[Configurator.knownLevels.length - 1];
            this.entry.level(this.level);
        });

        it('should throw if level is not specified', function() {
            var entry = new Entry(this.formatter, this.handler);

            expect(function() {
                entry.write();
            }).to.throwError(function(err) {
                expect(err.message).to.be('Level should be specified');
            });
        });

        it('should throw if attempting to write twice', function() {
            var entry = this.entry;

            entry.write();

            expect(function() {
                entry.write();
            }).to.throwError(function(err) {
                expect(err.message).to.be('Message has already been written once');
            });
        });

        it('should define a timestamp', function() {
            var now = Date.now();

            this.clock = this.sinon.useFakeTimers(now);
            this.entry.write();

            expect(this.entry.getTimestamp()).to.be(now);
        });

        it('should define a message', function() {
            var message = 'heyhey, I am a message';

            this.entry.write(message);
            expect(this.entry.getMessage()).to.be(message);
        });

        it('should expand Error instances with a trace', function() {
            var error = new Error('I am an Error');

            error.stack = error.name + ': stack';

            this.entry.write(error);
            expect(this.entry.getMessage()).to.be(error.stack);
        });

        it('should concatenate multiple arguments into a single string', function() {
            this.entry.write('one', 'two', 'three');
            expect(this.entry.getMessage()).to.be('one two three');
        });

        it('should substitute format placeholders', function() {
            this.entry.write('%s %j', 'whatso', {ever: 'never'});
            expect(this.entry.getMessage()).to.be('whatso {"ever":"never"}');
        });

        it('should pass itself to a handler', function() {
            this.entry.write();
            expect(this.handler.handle.calledOnce).to.be(true);
            expect(this.handler.handle.calledWithExactly(this.entry)).to.be(true);
        });
    });

    describe('getFormatted', function() {
        beforeEach(function() {
            this.formatted = 'EeR1ohghu9quahpee5AX4yongeepophi';
            this.sinon.stub(this.formatter, 'format').returns(this.formatted);
        });
        it('should pass itself to formatter', function() {
            this.entry.getFormatted();
            expect(this.formatter.format.calledOnce).to.be(true);
            expect(this.formatter.format.calledWithExactly(this.entry)).to.be(true);
        });

        it('should return the result of formatting the entry', function() {
            expect(this.entry.getFormatted()).to.be(this.formatted);
        });
    });

    describe('getFormatter', function() {
        it('should return the formatter entry was created with', function() {
            expect(this.entry.getFormatter()).to.be(this.formatter);
        });
    });

    describe('getHandler', function() {
        it('should return the handler entry was created with', function() {
            expect(this.entry.getHandler()).to.be(this.handler);
        });
    });
});
