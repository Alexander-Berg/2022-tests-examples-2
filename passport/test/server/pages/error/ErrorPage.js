var expect = require('expect.js');
var sinon = require('sinon');
var when = require('when');
var _ = require('lodash');

var ErrorPage = require('../../../../pages/error/ErrorPage');
var MockController = require('../../../util/MockController');
var MockApi = require('../../../util/MockApi');

describe('Error Page', function() {
    beforeEach(function() {
        this.controller = new MockController();
        this.api = new MockApi();
        this.page = new ErrorPage(this.controller, this.api);

        this.layout = new (require('inherit')(require('pview/CompositeView'), {
            name: 'testing'
        }))();
        sinon.stub(this.layout, 'render').returns(when.resolve('html here'));
        sinon.stub(this.page, '_getLayout').returns(this.layout);
    });

    describe('open', function() {
        beforeEach(function() {
            sinon.stub(this.controller, 'sendPage');
        });

        it('should send an HTTPException with its code', function(done) {
            var controller = this.controller;
            var HTTPError = require('../../../../lib/exceptions/http/HTTPException');

            var code = 123;
            this.page
                .setError(new HTTPError(code))
                .open()
                .then(function() {
                    expect(controller.sendPage.calledOnce).to.be(true);
                    expect(controller.sendPage.firstCall.args[1]).to.be(code);
                    done()
                }, asyncFail(done, 'Expected the deferred to be resolved')).then(null, done);
        });

        it('should send a generic error with code 500', function(done) {
            var controller = this.controller;
            this.page
                .setError(new Error())
                .open()
                .then(function() {
                    expect(controller.sendPage.calledOnce).to.be(true);
                    expect(controller.sendPage.firstCall.args[1]).to.be(500);
                    done()
                }, asyncFail(done, 'Expected the deferred to be resolved')).then(null, done);
        });
    });

});
