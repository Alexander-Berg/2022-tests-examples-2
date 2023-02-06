var expect = require('expect.js');
var sinon = require('sinon');
var when = require('when');

describe('Yasms API', function() {
    beforeEach(function() {
        this.Api = require('../../../../lib/yasms/api').Api;
    });

    describe('Retry condition', function() {
        beforeEach(function() {
            this.condition = this.Api.retryCondition;
            this.logger = new (require('plog'))('123');
        });

        it('should return a RetryReason if response status is not 200', function() {
            expect(this.condition(this.logger, {statusCode: 403})).to.be.a(this.condition.Reason);
        });

        require('../../../../configs/current').api.yasms.dao.retryCodes.forEach(function(retryCode) {
            it('should return a RetryReason if response has errorocode from retryCodes config', function() {
                expect(this.condition(this.logger, {statusCode: 200}, {doc: {errorocode: retryCode}})).to.be.a(
                    this.condition.Reason
                );
            });
        });

        it('should return undefined if there is no reason to retry', function() {
            expect(this.condition(this.logger, {statusCode: 200}, {})).to.be(undefined);
        });
    });

    describe('Methods', function() {
        beforeEach(function() {
            this.sender = 'passport-frontend';

            this.Dao = require('pdao/Http');
            this.dao = new this.Dao('123', '/path', 1, 100, 10, 1000);
            sinon.stub(this.dao, 'call').returns(when.resolve());

            this.api = new this.Api(this.dao);
        });

        describe('sendToUid', function() {
            beforeEach(function() {
                this.uid = '123415';
                this.text = 'Hey there, handsome!';
            });

            it('should call dao to get:/sendsms', function() {
                this.api.sendToUid(this.uid, this.text);
                expect(this.dao.call.calledOnce).to.be(true);
                expect(this.dao.call.calledWith('get', '/sendsms')).to.be(true);
            });

            it('should pass uid and text to dao', function() {
                this.api.sendToUid(this.uid, this.text);
                expect(this.dao.call.firstCall.args[2]).to.have.property('text', this.text);
                expect(this.dao.call.firstCall.args[2]).to.have.property('uid', this.uid);
            });

            it('should set up utf8 and sender properties', function() {
                this.api.sendToUid(this.uid, this.text);
                expect(this.dao.call.firstCall.args[2]).to.have.property('utf8', 1);
                expect(this.dao.call.firstCall.args[2]).to.have.property('sender', this.sender);
            });

            it('should reject with an error if dao responded with an errorcode', function(done) {
                this.dao.call.returns(
                    when.resolve({
                        doc: {
                            errorcode: 'Something'
                        }
                    })
                );

                var that = this;

                this.api
                    .sendToUid(this.uid, this.text)
                    .then(asyncFail(done, 'Expected the promise to be rejected'), function(err) {
                        expect(err).to.be.a(that.Api.ApiError);
                        done();
                    })
                    .then(null, done);
            });

            it('should resolve with a positive response', function(done) {
                var response = {};

                this.dao.call.returns(when.resolve(response));

                this.api
                    .sendToUid(this.uid, this.text)
                    .then(function(actualResponse) {
                        expect(actualResponse).to.be(response);
                        done();
                    }, asyncFail(done))
                    .then(null, done);
            });
        });
    });
});
