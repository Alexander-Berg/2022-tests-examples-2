var expect = require('expect.js');
var sinon = require('sinon');
var when = require('when');
var _ = require('lodash');

var ResetPasswordPage = require('../../../../pages/client/ResetPasswordPage');
var MockController = require('../../../util/MockController');
var MockApi = require('../../../util/MockApi');

describe('ResetPassword Page', function() {
    beforeEach(function() {
        this.controller = new MockController();
        this.api = new MockApi();
        this.page = new ResetPasswordPage(this.controller, this.api);

        this.clientId = '0d66fca6b5a040aa90340eabd473db19';
        this.url = {};
        sinon.stub(this.controller, 'getUrl').returns(this.url);
        sinon.stub(this.controller, 'isCsrfTokenValidV2').returns(when.resolve(true));
    });

    describe('open', function() {
        beforeEach(function() {
            var page = this.page;
            this.entryMethods = ['reset', 'undo'];
            this.entryMethods.forEach(function(method) {
                sinon.stub(page, method);
            });
        });

        it('should reset the password if opened for /client/password/reset/<client_id>', function(done) {
            this.url.pathname = '/client/password/reset/' + this.clientId;

            var that = this;
            this.page.open()
                .then(function() {
                    expect(that.page.reset.calledOnce).to.be(true);
                    expect(that.page.undo.called).to.be(false);

                    done();
                })
                .catch(done);
        });

        it('should undo the password reset if opened for /client/password/reset/undo/<client_id>', function(done) {
            this.url.pathname = '/client/password/reset/undo/' + this.clientId;

            var that = this;
            this.page.open()
                .then(function() {
                    expect(that.page.undo.calledOnce).to.be(true);
                    expect(that.page.reset.called).to.be(false);

                    done();
                })
                .catch(done);
        });
    });

    describe('reset', function() {
        beforeEach(function() {
            sinon.stub(this.api, 'newClientSecretV2').returns(when.resolve());
            sinon.stub(this.controller, 'redirectToClientAndShowSecretUndo');
        });

        it('should call api.newClientSecretV2', function() {
            this.page.reset(this.clientId);
            expect(this.api.newClientSecretV2.calledOnce).to.be(true);
            expect(this.api.newClientSecretV2.calledWithExactly(this.clientId)).to.be(true);
        });

        it('should redirect to client page and show the message', function(done) {
            var that = this;
            this.page.reset(this.clientId).then(function() {
                expect(that.controller.redirectToClientAndShowSecretUndo.calledOnce).to.be(true);
                expect(that.controller.redirectToClientAndShowSecretUndo.calledWithExactly(that.clientId)).to.be(true);
                done();
            }, asyncFail(done)).then(null, done);
        });
    });

    describe('undo', function() {
        beforeEach(function() {
            sinon.stub(this.api, 'undoNewClientSecretV2').returns(when.resolve());
            sinon.stub(this.controller, 'redirectToClientAndShowSecretUndone');
        });

        it('should call api.undoNewClientSecretV2', function() {
            this.page.undo(this.clientId);
            expect(this.api.undoNewClientSecretV2.calledOnce).to.be(true);
            expect(this.api.undoNewClientSecretV2.calledWithExactly(this.clientId)).to.be(true);
        });

        it('should redirect to client page and show the message', function(done) {
            var that = this;
            this.page.undo(this.clientId).then(function() {
                expect(that.controller.redirectToClientAndShowSecretUndone.calledOnce).to.be(true);
                expect(that.controller.redirectToClientAndShowSecretUndone.calledWithExactly(that.clientId)).to.be(true);
                done();
            }, asyncFail(done)).then(null, done);
        });
    });
});
