var expect = require('expect.js');

describe('Api retry condition', function() {
    beforeEach(function() {
        var logger = new (require('plog'))('logId');

        this.retryCodes = ['whatever'];
        this.retryCondition = require('../../OAuth/retryCondition')(this.retryCodes).bind(null, logger);
    });

    it('should return undefined when given a valid response', function() {
        expect(
            this.retryCondition(
                {
                    statusCode: 200
                },
                {
                    status: 'ok'
                }
            )
        ).to.be.an('undefined');
    });

    it('should return an error if response status code was not 200', function() {
        var error = this.retryCondition({statusCode: 500}, {});

        expect(error).to.be.an(Error);
        expect(error.message).to.be('Server response status was not 200 OK');
    });

    it('should return an error if response has a retry code in an array of errors', function() {
        var error = this.retryCondition(
            {
                statusCode: 200
            },
            {
                status: 'error',
                errors: this.retryCodes
            }
        );

        expect(error).to.be.an(Error);
        expect(error.message).to.be('Api returned an error code from retryCodes list');
    });
});
