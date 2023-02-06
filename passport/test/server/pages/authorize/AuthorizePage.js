var expect = require('expect.js');
var sinon = require('sinon');
var when = require('when');
var _ = require('lodash');

var AuthorizePage = require('../../../../pages/authorize/AuthorizePage');
var MockController = require('../../../util/MockController');
var MockApi = require('../../../util/MockApi');

describe('Authorize Page', function() {
    beforeEach(function() {
        this.controller = new MockController();
        this.api = new MockApi();
        this.page = new AuthorizePage(this.controller, this.api);

        this.gLogoutTime = Date.now().toString();
        this.tokensRevokeTime = Date.now().toString();
        this.appPasswordsRevokeTime = Date.now().toString();
        this.webSessionsRevokeTime = Date.now().toString();

        this.auth = {
            isAutologged: sinon.stub(),
            isLoggedIn: sinon.stub(),
            authorize: sinon.stub(),
            lightauth2full: sinon.stub(),
            getGLogoutTime: sinon.stub().returns(this.gLogoutTime),
            getTokensRevokeTime: sinon.stub().returns(this.tokensRevokeTime),
            getAppPasswordsRevokeTime: sinon.stub().returns(this.tokensRevokeTime),
            getWebSessionsRevokeTime: sinon.stub().returns(this.tokensRevokeTime)
        };
        sinon.stub(this.controller, 'getAuth').returns(this.auth);
        sinon.stub(this.controller, 'getUrl').returns(require('url').parse('https://oauth.yandex.ru/authorize'));
    });

    it('should be a Page', function() {
        expect(this.page).to.be.a(require('../../../../pages/AbstractPage'));
    });

    describe('open', function() {
        beforeEach(function() {
            var page = this.page;
            this.entryMethods = ['_allow', '_deny', '_submit'];
            this.entryMethods.forEach(function(method) {
                sinon.stub(page, method);
            });
        });

        describe('when user is not logged in', function() {
            beforeEach(function() {
                this.auth.isLoggedIn.returns(false);
            });

            it('should authorize the user', function() {
                this.page.open();
                expect(this.auth.authorize.calledOnce).to.be(true);
            });

            it('should not call _allow, _deny or _submit', function() {
                var page = this.page;
                page.open();
                this.entryMethods.forEach(function(method) {
                    expect(page[method].called).to.be(false);
                });
            });
        });

        describe('when user is autologged', function() {
            beforeEach(function() {
                this.auth.isLoggedIn.returns(true);
                this.auth.isAutologged.returns(true);
                this.page.open();
            });

            afterEach(function() {
                this.auth.isAutologged.returns(false);
            });

            it('should call lightauth2full for autologged user', function() {
                expect(this.auth.lightauth2full.calledOnce).to.be(true);
            });

            it('should not call _allow, _deny or _submit', function() {
                this.entryMethods.forEach(function(method) {
                    expect(this.page[method].called).to.be(false);
                }, this);
            });
        });

        describe('when user is logged in', function() {
            beforeEach(function() {
                this.auth.isLoggedIn.returns(true);
            });

            it('should not call for authorization', function() {
                this.page.open();
                expect(this.auth.authorize.called).to.be(false);
            });
        });
    });

    describe('_submit', function() {
        describe('when user confirmation required', function() {
            beforeEach(function(done) {
                this.apiResponse = {
                    "status": "ok",
                    "request_id": "1d66fca6b5a040aa90340eabd473db19",
                    "redirect_uri": "ya.ru",
                    "require_user_confirm": true,
                    "requested_scopes": new (require('papi/OAuth/models/ScopesCollection'))()
                };

                sinon.stub(this.api, 'authorizeSubmitV2').returns(when.resolve(this.apiResponse));
                sinon.stub(this.controller, 'getRequestParam');

                sinon.stub(this.page, '_render');
                sinon.stub(this.page, '_commit');

                var that = this;
                this.requestParams = {
                    'response_type': 'token',
                    'client_id': '0d66fca6b5a040aa90340eabd473db19',
                    'redirect_uri': 'https://google.com',
                    'state': "Then I'll huff, and I'll puff, and I'll blow your fucking head in.",
                    'display': 'popup'
                };
                _.each(this.requestParams, function(value, key) {
                    that.controller.getRequestParam.withArgs(key).returns(value);
                });

                this.page._submit().then(function() {
                    that.renderArgs = that.page._render.firstCall.args;
                    done();
                }, asyncFail(done, 'Expected the promise to resolve')).then(null, done);
            });

            it('should render the page', function() {
                expect(this.page._render.calledOnce).to.be(true);
                expect(this.page._commit.called).to.be(false);
            });

            var responseArgs = [
                'request_id',
                'requested_scopes',
                'redirect_uri'
            ];
            _.each(responseArgs, function(responseKey, asArgIndex) {
                it('should pass ' + responseKey + ' from response to render', function() {
                    expect(this.renderArgs[asArgIndex]).to.be(this.apiResponse[responseKey]);
                });
            });

            var requestArgs = [
                'response_type',
                'state'
            ];
            _.each(requestArgs, function(requestKey, asArgIndex) {
                asArgIndex = asArgIndex + responseArgs.length; //Offset for the request params
                it('should pass ' + requestKey + ' from request to render', function() {
                    expect(this.renderArgs[asArgIndex]).to.be(this.requestParams[requestKey]);
                });
            });

            it('should render the popup if requested with display=popup', function() {
                expect(this.renderArgs[5]).to.be(true);
            });

            it('should render the full page if requested without display=popup', function(done) {
                var that = this;
                this.controller.getRequestParam.withArgs('display').returns(undefined);
                this.page._submit().then(function() {
                    expect(that.page._render.secondCall.args[5]).to.be(false);
                    done();
                }, asyncFail(done, 'Expected the promise to resolve')).then(null, done);
            });
        });

    });

    describe('_commit', function() {
        beforeEach(function() {
            this.requestId = 'CheePae5aelud4ag';
            this.grantedScopes = ['scope'];
            this.responseType = 'token';
            this.ip = '192.168.0.256';

            sinon.stub(this.api, 'authorizeCommitV2').returns(when.resolve({code: '1234567'}));
            sinon.stub(this.controller, 'getIp').returns(this.ip);
            sinon.stub(this.controller, 'redirect');
            sinon.stub(this.page, '_errorHandler');
        });

        it('should call api.authorizeCommitV2 once', function() {
            this.page._commit(this.requestId, this.responseType, []);
            expect(this.api.authorizeCommitV2.calledOnce).to.be(true);
        });

        it('should call api with the given request_id', function() {
            this.page._commit(this.requestId, this.responseType, []);
            expect(this.api.authorizeCommitV2.firstCall.args[0]).to.be(this.requestId);
        });

        it('should call api with the given grantedScopes', function() {
            this.page._commit(this.requestId, this.responseType, this.grantedScopes);
            expect(this.api.authorizeCommitV2.firstCall.args[1]).to.be(this.grantedScopes);
        });

        describe('when api rejects', function() {
            beforeEach(function(done) {
                this.error = {};
                this.api.authorizeCommitV2.returns(when.reject(this.error));

                this.page._commit(this.requestId, this.responseType, []).then(done, done);
            });

            it('should call _errorHandler once', function() {
                expect(this.page._errorHandler.calledOnce).to.be(true);
            });

            it('should call _errorHandler inside the context of the page', function() {
                expect(this.page._errorHandler.alwaysCalledOn(this.page)).to.be(true);
            });

            it('should call _errorHandler with the given responseType', function() {
                expect(this.page._errorHandler.firstCall.args[0]).to.be(this.responseType);
            });

            it('should call _errorHandler with an error api rejected with', function() {
                expect(this.page._errorHandler.firstCall.args[1]).to.be(this.error);
            });
        });

        var apiResponseHandling = function(response) {
            beforeEach(function(done) {
                this.response = response;
                this.api.authorizeCommitV2.returns(when.resolve(this.response));

                this.composedUrl = {};
                sinon.stub(this.page, 'appendQuery').returns(this.composedUrl);

                this.page._commit(this.requestId, this.responseType, []).then(done, done);
            });

            it('should call appendQuery once', function() {
                expect(this.page.appendQuery.calledOnce).to.be(true);
            });

            it('should call appendQuery with redirect uri from respone', function() {
                expect(this.page.appendQuery.calledWith(this.response.redirect_uri)).to.be(true);
            });

            it('should call controller.redirect once', function() {
                expect(this.controller.redirect.calledOnce).to.be(true);
            });

            it('should call controller.redirect with the result of appendQuery', function() {
                expect(this.controller.redirect.calledWithExactly(this.composedUrl)).to.be(true);
            });
        };

        describe('when api responds with code', function() {
            apiResponseHandling({
                "status": "ok",
                "state": "hey-hey",
                "code": "1234567",
                "redirect_uri": "ya.ru"
            });

            it('should call appendQuery with ? as appendAfterSymbol', function() {
                expect(this.page.appendQuery.firstCall.args[2]).to.be('?');
            });

            it('should call appendQuery with code from response', function() {
                expect(this.page.appendQuery.firstCall.args[1])
                    .to.have.property('code', this.response.code);
            });

            it('should call appendQuery with state from response', function() {
                expect(this.page.appendQuery.firstCall.args[1])
                    .to.have.property('state', this.response.state);
            });
        });

        describe('when api responds with token', function() {
            apiResponseHandling({
                "status": "ok",
                "state": "waka-waka",
                "access_token": "6ee35d55a3004268a7b6497cc4949f1e",
                "token_type": "bearer",
                "expires_in": null,
                "redirect_uri": "ya.ru"
            });

            it('should call appendQuery with # as appendAfterSymbol', function() {
                expect(this.page.appendQuery.firstCall.args[2]).to.be('#');
            });

            it('should call appendQuery with access_token from response', function() {
                expect(this.page.appendQuery.firstCall.args[1])
                    .to.have.property('access_token', this.response.access_token);
            });

            it('should call appendQuery with token_type from response', function() {
                expect(this.page.appendQuery.firstCall.args[1])
                    .to.have.property('token_type', this.response.token_type);
            });

            it('should call appendQuery with expires_in from response', function() {
                expect(this.page.appendQuery.firstCall.args[1])
                    .to.have.property('expires_in', this.response.expires_in);
            });

            it('should call appendQuery with state from response', function() {
                expect(this.page.appendQuery.firstCall.args[1])
                    .to.have.property('state', this.response.state);
            });
        });
    });

    describe('_deny', function() {
        beforeEach(function() {
            this.ip = '192.168.0.256';
            this.request_id = 'ololo';
            this.state = 'aephosi4Ieweij2uo9iekeem2Iem6aif';
            this.redirect_uri = 'ya.ru';
            this.apiResponse = {
                "status": "ok",
                "request_id": this.request_id,
                "redirect_uri": this.redirect_uri
            };

            sinon.stub(this.api, 'authorizeGetStateV2').returns(when.resolve(this.apiResponse));

            sinon.stub(this.controller, 'isCsrfTokenValidV2').returns(when.resolve(true));
            sinon.stub(this.controller, 'redirect');
            sinon.stub(this.controller, 'getIp').returns(this.ip);

            this.alteredUrl = 'http://au9phauB4ephuughotheijiNoh3vaiKi';

            sinon.stub(this.page, 'appendQuery').returns(this.alteredUrl);

            sinon.stub(this.controller, 'getRequestParam')
                .withArgs('request_id').returns(this.request_id)
                .withArgs('state').returns(this.state);

            sinon.stub(require('putils'), 'i18n');

            this.accessDeniedMessage = 'Пользователь запретил доступ приложения к данным';
            require('putils').i18n.withArgs('ru', 'authorize.errors.denied').returns(this.accessDeniedMessage);
        });

        it('should call authorizeGetStateV2 with request_id', function(done) {
            var that = this;
            this.page._deny()
                .then(function() {
                    expect(that.api.authorizeGetStateV2.firstCall.args[0]).to.be(that.request_id);
                    done();
                })
                .then(null, done);
        });

        it('should redirect to index if csrf token is not valid', function(done) {
            sinon.stub(this.controller, 'redirectToIndex');
            this.controller.isCsrfTokenValidV2.returns(when.resolve(false));

            var that = this;
            this.page._deny()
                .then(function() {
                    expect(that.controller.redirectToIndex.calledOnce).to.be(true);
                    expect(that.controller.redirect.called).to.be(false); //Does not gets called directly

                    done();
                })
                .then(null, done);
        });

        var appendQueryData = function(appendAfterSymbol) {
            it('should call appendQuery once', function() {
                expect(this.page.appendQuery.calledOnce).to.be(true);
            });

            it('should call appendQuery with "' + appendAfterSymbol + '" as an appendAfterSymbol', function() {
                expect(this.page.appendQuery.firstCall.args[2]).to.be(appendAfterSymbol);
            });

            it('should call appendQuery with callback_url as an url', function() {
                expect(this.page.appendQuery.firstCall.args[0]).to.be(this.redirect_uri);
            });

            it('should call appendQuery with error: access_denied', function() {
                expect(this.page.appendQuery.firstCall.args[1])
                    .to.have.property('error', 'access_denied');
            });

            it('should call appendQuery with appropriate error_description', function() {
                expect(this.page.appendQuery.firstCall.args[1])
                    .to.have.property('error_description', this.accessDeniedMessage);
            });

            it('should call appendQuery with state: state', function() {
                expect(this.page.appendQuery.firstCall.args[1])
                    .to.have.property('state', this.state);
            });

            it('should redirect to the result of appendQuery', function() {
                expect(this.controller.redirect.calledOnce).to.be(true);
                expect(this.controller.redirect.calledWithExactly(this.alteredUrl)).to.be(true);
            });
        };

        describe('with response_type=code', function() {
            beforeEach(function(done) {
                this.controller.getRequestParam.withArgs('response_type').returns('code');

                this.page._deny()
                    .then(done)
                    .catch(done);
            });

            appendQueryData('?');
        });

        describe('with response_type=token', function() {
            beforeEach(function(done) {
                this.controller.getRequestParam.withArgs('response_type').returns('token');

                this.page._deny()
                    .then(done)
                    .catch(done);
            });

            appendQueryData('#');
        });
    });

    describe('appendQuery', function() {
        beforeEach(function() {
            this.appendAfterSymbol = '#';
            this.url = 'magnet://tpb.com/eeLiequoosoh9fei';
            this.query = {
                'whatso': 'ever',
                'key': 'value',
                'one': 1,
                'two': 2
            };
            this.stringifiedQuery = 'whatso=ever&key=value&one=1&two=2';
        });

        it('should throw if url is not a string', function() {
            var that = this;
            expect(function() {
                that.page.appendQuery({}, that.query);
            }).to.throwError(function(err) {
                expect(err.message).to.be('URL should be a string');
            });
        });

        it('should throw if query is not a plain object', function() {
            var that = this;
            expect(function() {
                that.page.appendQuery(that.url, 'nope');
            }).to.throwError(function(err) {
                expect(err.message).to.be('Query should be a plain hash');
            });
        });

        it('should throw if appendAfterSymbol is not a string', function() {
            var that = this;
            expect(function() {
                that.page.appendQuery(that.url, that.query, 1);
            }).to.throwError(function(err) {
                expect(err.message).to.be('Symbol to append after should be a char');
            });
        });

        it('should throw if appendAfterSymbol is not one-symbol long', function() {
            var that = this;
            expect(function() {
                that.page.appendQuery(that.url, that.query, 'two');
            }).to.throwError(function(err) {
                expect(err.message).to.be('Symbol to append after should be a char');
            });
        });

        it('should append the query to the url after the appendAfterSymbol', function() {
            expect(this.page.appendQuery(this.url, this.query, this.appendAfterSymbol))
                .to.be(this.url + this.appendAfterSymbol + this.stringifiedQuery);
        });

        it('should append the query to the url using ? if no appendAfterSymbol is given', function() {
            expect(this.page.appendQuery(this.url, this.query))
                .to.be(this.url + '?' + this.stringifiedQuery);
        });

        it('should append the query after & if url already contains the appendAfterSymbol', function() {
            this.url = this.url + this.appendAfterSymbol + 'vasya=durak';
            expect(this.page.appendQuery(this.url, this.query, this.appendAfterSymbol))
                .to.be(this.url + '&' + this.stringifiedQuery);
        });
    });
});
