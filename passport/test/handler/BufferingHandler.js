var expect = require('expect.js');
var sinon = require('sinon');

var Logger = require('../../logger/Logger');
var Configurator = require('../../logger/Configurator');

describe('Buffer', function() {
    beforeEach(function() {
        this.Buffer = require('../../logger/handler/BufferingHandler').Buffer;
        this.buffer = new this.Buffer();

        this.data = 'Lorem Ipsum Dolor Sit Amet';
    });

    describe('write', function() {
        it(
            'should return the written data when flushing with newline so that ' +
                'consecutive logs are on separate lines',
            function() {
                expect(this.buffer.write(this.data).flush()).to.be(this.data + '\n');
            }
        );

        it('should return multiple writes concatenated with \\n', function() {
            expect(
                this.buffer
                    .write(this.data)
                    .write(this.data)
                    .write(this.data)
                    .flush()
            ).to.be([this.data, this.data, this.data].join('\n') + '\n');
        });

        it('should return empty string after flushing twice', function() {
            this.buffer.write(this.data).flush();
            expect(this.buffer.flush()).to.be('');
        });
    });

    describe('isEmpty', function() {
        it('should return true if nothing was written', function() {
            expect(this.buffer.isEmpty()).to.be(true);
        });

        it('should return true after flushing', function() {
            this.buffer.write(this.data).flush();
            expect(this.buffer.isEmpty()).to.be(true);
        });

        it('should return false after writing', function() {
            expect(this.buffer.write(this.data).isEmpty()).to.be(false);
        });
    });
});

describe('BufferingHandler', function() {
    beforeEach(function() {
        this.sinon = sinon.sandbox.create();
        this.clock = this.sinon.useFakeTimers();

        this.logId = 'gub1pee5xe8quie3uThiez2aiz4aeC4j';
        this.formattedEntry = 'ahChieziChuKie1heechooj4phoh0cheipau3xu4aech1aiqueeLah6UteiShuch';
        this.entry = Logger.log().logId(this.logId);
        this.sinon.stub(this.entry, 'getFormatted').returns(this.formattedEntry);

        this.Handler = require('../../logger/handler/BufferingHandler');

        this.bufferContents = 'aodairu9seenieZ7ies9ieb3pheez1Ei\nfa4Ogh5IeD4thoo2ieKu5eD5oothicai';

        this.buffer = new this.Handler.Buffer();
        this.sinon.stub(this.buffer, 'flush').returns(this.bufferContents);
        this.sinon.stub(this.buffer, 'isEmpty').returns(false);
        this.sinon.stub(this.buffer, 'write').returns(this.buffer);
        this.sinon.stub(this.Handler, 'getBuffer').returns(this.buffer);

        this.stdout = {
            write: sinon.stub()
        };
        this.sinon.stub(this.Handler, 'getStream').returns(this.stdout);

        this.config = Configurator.instance();
        this.handler = new this.Handler(this.config);
    });
    afterEach(function() {
        this.sinon.restore();
    });

    describe('Constructor', function() {
        it('should call static getBuffer', function() {
            expect(this.Handler.getBuffer.calledOnce).to.be(true);
        });

        it('should call static getStream', function() {
            expect(this.Handler.getStream.calledOnce).to.be(true);
        });

        it('should flush the buffer every second', function() {
            var initialCallcount = this.buffer.flush.callCount;

            for (var callNum = 1; callNum < 10; callNum++) {
                this.clock.tick(1000);
                expect(this.buffer.flush.callCount).to.be(initialCallcount + callNum);
            }
        });

        it('should not flush the buffer if it is empty', function() {
            this.buffer.isEmpty.returns(true);
            var initialCallcount = this.buffer.flush.callCount;

            for (var callNum = 1; callNum < 10; callNum++) {
                this.clock.tick(1005);
                expect(this.buffer.flush.callCount).to.be(initialCallcount);
            }
        });

        it('should write the flushed buffer contents to the stream every second', function() {
            var initialCallcount = this.stdout.write.callCount;

            for (var callNum = 1; callNum < 10; callNum++) {
                this.clock.tick(1005);
                expect(this.stdout.write.callCount).to.be(initialCallcount + callNum);
                expect(this.stdout.write.lastCall.args[0]).to.be(this.bufferContents);
            }
        });
    });

    describe('_handle', function() {
        it('should write to buffer', function() {
            this.handler._handle(this.entry);
            expect(this.buffer.write.calledOnce).to.be(true);
            expect(this.buffer.write.calledWithExactly(this.formattedEntry));
        });
    });
});
