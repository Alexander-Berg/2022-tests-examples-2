var expect = require('expect.js');
var sinon = require('sinon');
var when = require('when');
var _ = require('lodash');

var Controller = require('../../../controller/Controller');
var FakeController = require('../../util/MockController');

describe('Oauth controller', function() {
    beforeEach(function() {
        this.req = FakeController.getReq();
        this.res = FakeController.getRes();
        this.logId = 'Ii8ieK1aik3Eizalee3aish5nooSh1Ah';

        this.controller = new Controller(this.req, this.res, this.logId);
    });

    describe('constructor', function() {
        it('should throw if no logId is given', function() {
            var that = this;
            expect(function() {
                new Controller(that.req, that.res);
            }).to.throwError(function(err) {
                expect(err.message).to.be('LogID should be defined');
            });
        });
    });

    describe('getLang', function() {
        _.each({
            'en': 'com',
            'tr': 'com.tr',
            'ru': 'ru'
        }, function(domain, lang) {
            it('should return ' + lang + 'for domain ' + domain, function() {
                sinon.stub(this.controller, 'getTld').returns(domain);
                expect(this.controller.getLang()).to.be(lang);
            });
        });

        it('should return "ru" for an unknonwn domain', function() {
            sinon.stub(this.controller, 'getTld').returns('aero');
            expect(this.controller.getLang()).to.be('ru');
        });
    });

    describe('isCsrfTokenValidV2', function() {
        beforeEach(function() {
            this.csrf = 'Aibiteengolepojetho0eish5qui5mae';
            sinon.stub(this.controller, 'getCsrfToken').returns(when.resolve(this.csrf));
        });

        it('should return false if given token does not equals generated one', function(done) {
            sinon.stub(this.controller, 'checkCsrfToken').returns(when.resolve(false));
            this.controller.isCsrfTokenValidV2('invalid')
                .then(function(valid) {
                    expect(valid).to.be(false);
                    done();
                })
                .then(null, done);
        });

        it('should return true if given token equals generated one', function(done) {
            sinon.stub(this.controller, 'checkCsrfToken').returns(when.resolve(true));
            this.controller.isCsrfTokenValidV2(this.csrf)
                .then(function(valid) {
                    expect(valid).to.be(true);
                    done();
                })
                .then(null, done);
        });

        describe('without args', function() {
            beforeEach(function() {
                sinon.stub(this.controller, 'getRequestParam').withArgs('csrf').returns(this.csrf);
            });

            it('should return true if request param "csrf" matches the generated token', function(done) {
                sinon.stub(this.controller, 'checkCsrfToken').returns(when.resolve(true));
                this.controller.isCsrfTokenValidV2()
                    .then(function(valid) {
                        expect(valid).to.be(true);
                        done();
                    })
                    .then(null, done);
            });

            it('should return false if request param "csrf" does not matches the generated token', function(done) {
                this.controller.getRequestParam.withArgs('csrf').returns('nope');
                sinon.stub(this.controller, 'checkCsrfToken').returns(when.resolve(false));
                this.controller.isCsrfTokenValidV2()
                    .then(function(valid) {
                        expect(valid).to.be(false);
                        done();
                    })
                    .then(null, done);
            });
        });
    });

    describe('redirects', function() {
        beforeEach(function() {
            sinon.stub(this.controller, 'redirect');
            this.clientId = '0d66fca6b5a040aa90340eabd473db19';
        });

        describe('redirectToClientPage', function() {
            it('should throw if client id is not a 32-char long hex', function() {
                var controller = this.controller;
                expect(function() {
                    controller.redirectToClientPage('not a client id');
                }).to.throwError(function(err) {
                        expect(err.message).to.be('Client ID should be a 32char long hex');
                    });
            });

            it('should redirect to client page', function() {
                this.controller.redirectToClientPage(this.clientId);
                expect(this.controller.redirect.calledOnce).to.be(true);
                expect(this.controller.redirect.calledWithExactly('/client/' + this.clientId));
            });
        });

        describe('redirectToClientAndShowSecretUndo', function() {
            it('should throw if client id is not a 32-char long hex', function() {
                var controller = this.controller;
                expect(function() {
                    controller.redirectToClientAndShowSecretUndo('not a client id');
                }).to.throwError(function(err) {
                        expect(err.message).to.be('Client ID should be a 32char long hex');
                    });
            });

            it('should redirect to client page', function() {
                this.controller.redirectToClientAndShowSecretUndo(this.clientId);
                expect(this.controller.redirect.calledOnce).to.be(true);
                expect(this.controller.redirect.calledWithExactly('/client/' + this.clientId + '/undosecret'));
            });
        });

        describe('redirectToClientAndShowSecretUndone', function() {
            it('should throw if client id is not a 32-char long hex', function() {
                var controller = this.controller;
                expect(function() {
                    controller.redirectToClientAndShowSecretUndone('not a client id');
                }).to.throwError(function(err) {
                        expect(err.message).to.be('Client ID should be a 32char long hex');
                    });
            });

            it('should redirect to client page', function() {
                this.controller.redirectToClientAndShowSecretUndone(this.clientId);
                expect(this.controller.redirect.calledOnce).to.be(true);
                expect(this.controller.redirect.calledWithExactly('/client/' + this.clientId + '/secretundone'));
            });
        });
    });
});
