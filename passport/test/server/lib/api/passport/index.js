var expect = require('expect.js');
var _ = require('lodash');

describe('Passport Api', function() {
    beforeEach(function() {
        this.Api = require('../../../../../lib/api/passport');
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
                    it(`should transform ${original} to ${transformed} if given`, function() {
                        this.headers[original] = this.value;

                        var newHeaders = this.Api.transformHeaders(this.headers);

                        expect(newHeaders).to.not.have.property(original);
                        expect(newHeaders).to.have.property(transformed, this.value);
                    });
                }
            );

            ['cookie', 'user-agent'].forEach(function(nulled) {
                it(`should set ${nulled} to an empty string if none given`, function() {
                    var transformed = this.Api.transformHeaders(this.headers);

                    expect(transformed).to.have.property(this.prefix + nulled, '');
                    expect(transformed).to.not.have.property(nulled);
                });

                it(`should leave ${nulled} as is if any given`, function() {
                    this.headers[nulled] = this.value;
                    var transformed = this.Api.transformHeaders(this.headers);

                    expect(transformed).to.have.property(this.prefix + nulled, this.value);
                    expect(transformed).to.not.have.property(nulled);
                });
            });
        });
    });
});
