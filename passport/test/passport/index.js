var expect = require('expect.js');
var sinon = require('sinon');
var _ = require('lodash');

describe('Passport Api', function() {
    beforeEach(function() {
        this.Api = require('../../Passport');

        this.logId = 'zae4eo8ohtheeshee7oFaiJuacha4oht';

        this.dao = new (require('pdao/Http'))(
            'logId',
            'baseUrl',
            10, //Max retries
            100, //Retry after
            100, //Max connections
            3000 //Timeout after
        );
        sinon.stub(this.dao, 'call');

        this.headers = {
            'ya-consumer-ip': '127.0.0.1'
        };

        this.consumer = 'some_yandex_service';
    });

    describe('Constructor', function() {
        beforeEach(function() {
            this.transformedHeaders = {};
            sinon.stub(this.Api, 'transformHeaders').returns(this.transformedHeaders);
            sinon.stub(this.dao, 'mixHeaders');

            new this.Api(this.logId, this.dao, this.headers, this.consumer);
        });
        afterEach(function() {
            this.Api.transformHeaders.restore();
        });

        it('should call transformHeaders on the rawHeaders received', function() {
            expect(this.Api.transformHeaders.calledOnce).to.be(true);
            expect(this.Api.transformHeaders.calledWithExactly(this.headers)).to.be(true);
        });

        it('should mix transformed headers into dao', function() {
            expect(this.dao.mixHeaders.calledOnce).to.be(true);
            expect(this.dao.mixHeaders.calledWithExactly(this.transformedHeaders)).to.be(true);
        });
    });

    describe('Static', function() {
        describe('transformHeaders', function() {
            beforeEach(function() {
                this.prefix = 'ya-client-';
                this.value = 'blahblah';

                this.header = 'arbitrary';
                this.headers = {};
                this.headers[this.header] = this.value;
            });

            it('should prepend a prefix to an arbitrary header', function() {
                var transformed = this.Api.transformHeaders(this.headers);

                expect(transformed).to.have.property(this.prefix + this.header, this.value);
                expect(transformed).to.not.have.property(this.header);
            });

            it('should leave the passed argument as is', function() {
                this.Api.transformHeaders(this.headers);
                expect(this.headers).to.have.property(this.header, this.value);
                expect(this.headers).to.not.have.property(this.prefix + this.header);
            });

            it('should leave passed headers object as is', function() {
                var cloned = require('lodash').clone(this.headers);

                this.Api.transformHeaders(this.headers);
                expect(this.headers).to.eql(cloned);
            });

            it('should not prefix headres that are already prefixed', function() {
                this.headers[this.prefix + this.header] = this.value;
                expect(this.Api.transformHeaders(this.headers)).to.not.have.property(
                    this.prefix + this.prefix + this.header
                );
            });

            it('should not leave initial headers in the result', function() {
                expect(this.Api.transformHeaders(this.headers)).to.not.have.property(this.header);
            });

            it('should have same results on successive transformations', function() {
                expect(this.Api.transformHeaders(this.headers)).to.eql(this.Api.transformHeaders(this.headers));
            });

            _.each(
                {
                    'x-real-ip': 'ya-consumer-client-ip',
                    authorization: 'ya-consumer-authorization',
                    'x-real-scheme': 'ya-consumer-client-scheme'
                },
                function(transformed, original) {
                    it('should transform ' + original + ' to ' + transformed + ' if given', function() {
                        this.headers[original] = this.value;

                        var newHeaders = this.Api.transformHeaders(this.headers);

                        expect(newHeaders).to.not.have.property(original);
                        expect(newHeaders).to.have.property(transformed, this.value);
                    });
                }
            );

            ['cookie', 'user-agent'].forEach(function(nulled) {
                it('should set ' + nulled + ' to an empty string if none given', function() {
                    var transformed = this.Api.transformHeaders(this.headers);

                    expect(transformed).to.have.property(this.prefix + nulled, '');
                    expect(transformed).to.not.have.property(nulled);
                });

                it('should leave ' + nulled + ' as is if any given', function() {
                    this.headers[nulled] = this.value;
                    var transformed = this.Api.transformHeaders(this.headers);

                    expect(transformed).to.have.property(this.prefix + nulled, this.value);
                    expect(transformed).to.not.have.property(nulled);
                });
            });
        });
    });
});
