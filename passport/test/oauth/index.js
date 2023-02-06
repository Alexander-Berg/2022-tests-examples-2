var expect = require('expect.js');
var sinon = require('sinon');
var when = require('when');
var _ = require('lodash');

var validClientId = '40d046e010b26d7b76d3d1e0977a6183';
var glogoutTime = '1415374124';
var Scope = require('../../OAuth/models/Scope');
var ScopesCollection = require('../../OAuth/models/ScopesCollection');

describe('Oauth api', function() {
    beforeEach(function() {
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

        this.lang = 'tr';
        this.uid = 'ca7Tieto';
        this.consumer = 'some_yandex_service';

        this.headers = {
            'ya-consumer-ip': '127.0.0.1'
        };

        this.Api = require('../../OAuth');
        this.api = new this.Api(this.logId, this.dao, this.consumer, this.headers, this.lang, this.uid);

        this.apiErrorResponse = {
            status: 'error',
            errors: ['method.not_allowed']
        };
    });

    describe('Constructor', function() {
        beforeEach(function() {
            this.transformedHeaders = {};
            sinon.stub(this.Api, 'transformHeaders').returns(this.transformedHeaders);
            sinon.stub(this.dao, 'mixHeaders');

            new this.Api(this.logId, this.dao, this.consumer, this.headers, this.lang, this.uid);
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
        describe('getAppPasswordsSlugByClientId', function() {
            beforeEach(function() {
                this.mapping = {};
                this.clientId = '773adca0973d47e1a43c36b01ab997d4';
                this.slug = 'whatso';
                this.mapping[this.clientId] = this.slug;

                this.Api.setAppPasswordsClientIdMapping(this.mapping);
            });
            afterEach(function() {
                this.Api._resetAppPasswordsClientIdMapping();
            });
            it('should return a mapping previously defined by setAppPasswordsClientIdMapping', function() {
                expect(this.Api.getAppPasswordsSlugByClientId(this.clientId)).to.be(this.slug);
            });
        });
    });

    var generateBeforeEach = function(method, successfulResponse) {
        var extraArgs = Array.prototype.slice.call(arguments, 2);

        return function(done) {
            this.response = successfulResponse;
            this.dao.call.returns(when.resolve(_.clone(this.response, true)));

            this.result = this.api[method]
                .apply(this.api, extraArgs)
                .then(function(clients) {
                    done();
                    return clients;
                })
                .then(null, done);

            this.callData = this.dao.call.firstCall.args[2]; //3rd argument to a call
        };
    };

    var commonDaoTests = function() {
        it('should make a single call to the dao', function() {
            expect(this.dao.call.calledOnce).to.be(true);
        });

        it('should pass consumer to dao', function() {
            expect(this.callData).to.have.property('consumer', this._consumer);
        });
    };

    var passesLang = function() {
        it('should pass lang to dao', function() {
            expect(this.callData).to.have.property('language', this.lang);
        });
    };

    var passesUid = function() {
        it('should pass uid to dao', function() {
            expect(this.callData).to.have.property('uid', this.uid);
        });
    };

    var checksForUid = function(method) {
        var extraArgs = Array.prototype.slice.call(arguments, 1);

        it('should throw if uid is not set', function() {
            var api = new this.Api(this.logId, this.dao, this.consumer, this.headers, this.lang);

            expect(function() {
                api[method].apply(api, extraArgs);
            }).to.throwError(function(err) {
                expect(err.message).to.be('Uid should be set before using method "%s"'.replace('%s', method));
            });
        });
    };

    var checksGlogoutTime = function(method) {
        var extraArgs = Array.prototype.slice.call(arguments, 1);

        it('should throw if glogouttime passed as first argument is not a string', function() {
            var api = new this.Api(this.logId, this.dao, this.consumer, this.headers, this.lang);

            expect(function() {
                api[method].apply(api, [false].concat(extraArgs));
            }).to.throwError(function(err) {
                expect(err.message).to.be('Global logout time should be provided for method %s'.replace('%s', method));
            });
        });
    };

    var checksClientID = function(method) {
        var extraArgs = Array.prototype.slice.call(arguments, 1);
        var composedArgs = extraArgs
            .slice(0, 1)
            .concat(['ZaiMe9Seir'])
            .concat(extraArgs.slice(1));

        it('should throw if client id passed as a second arg is not valid', function() {
            var api = this.api;
            var Api = this.Api;

            expect(function() {
                api[method].apply(api, composedArgs);
            }).to.throwError(function(err) {
                expect(err).to.be.an(Api.ApiError);
                expect(err.contains('client.not_found')).to.be(true);
            });
        });

        it('should not call dao if client id passed as a second arg is not valid', function() {
            var callCountBefore = this.dao.call.callCount;

            try {
                this.api[method].apply(this.api, composedArgs);
            } catch (e) {
                // empty
            }

            //DAO is called once within beforeEach and should not be called again
            expect(this.dao.call.callCount).to.be(callCountBefore);
        });
    };

    var throwsApiError = function(method) {
        var extraArgs = Array.prototype.slice.call(arguments, 1);

        it('should throw an Api Error if response status was "error" and errors was an array', function(done) {
            var that = this;

            this.dao.call.returns(when.resolve(_.clone(this.apiErrorResponse)));

            this.api[method]
                .apply(this.api, extraArgs)
                .then(asyncFail(done, 'Expected the promise to be rejected'), function(error) {
                    expect(error).to.be.a(that.Api.ApiError);
                    expect(error.getResponse()).to.eql(that.apiErrorResponse);
                    done();
                })
                .then(null, done);
        });
    };

    describe('listCreatedClients', function() {
        beforeEach(
            generateBeforeEach('listCreatedClients', {
                status: 'ok',
                clients: [
                    {
                        id: '0d66fca6b5a040aa90340eabd473db19',
                        title: 'Test client',
                        description: 'Client for test',
                        icon: 'http://icon',
                        icon_id: '3374/e0778950ab864f87bc9c49b896f5d1a0-3',
                        icon_url:
                            'https://avatars.mdst.yandex.net/get-oauth/3374/e0778950ab864f87bc9c49b896f5d1a0-3/normal',
                        homepage: 'http://homepage',
                        callback: 'http://callback',
                        scopes: {
                            Test: {
                                'test:foo': {
                                    title: 'Foo',
                                    requires_approval: false,
                                    ttl: null,
                                    is_ttl_refreshable: false
                                },
                                'test:bar': {
                                    title: 'Bar',
                                    requires_approval: false,
                                    ttl: null,
                                    is_ttl_refreshable: false
                                }
                            }
                        },
                        create_time: 1407477045,
                        secret: '0d66fca6b5a040aa90340eabd473db20',
                        approval_status: 0,
                        blocked: false
                    }
                ]
            })
        );

        checksForUid('listCreatedClients');
        commonDaoTests();
        passesLang();
        passesUid();
        throwsApiError('listCreatedClients');

        it('should call dao get /2/clients/created', function() {
            expect(this.dao.call.calledWith('get', '/2/clients/created')).to.be(true);
        });

        it('should return an array of client models', function(done) {
            this.result
                .then(function(result) {
                    expect(result).to.be.an(Array);
                    expect(
                        result.every(function(client) {
                            return client instanceof require('../../OAuth/models/Client');
                        })
                    ).to.be(true);
                    done();
                }, asyncFail(done))
                .then(null, done);
        });

        it("should populate the client's scopes collection with scopes", function(done) {
            var that = this;

            this.result
                .then(function(clients) {
                    var clientScopes = clients[0].getScopes();
                    var expectedScopes = _.flatten(
                        _.map(that.response.clients[0].scopes, function(scopes) {
                            return _.map(scopes, function(scope, id) {
                                return new Scope(id, scope);
                            });
                        })
                    );

                    expect(clientScopes.length).to.be(2);
                    expect(
                        expectedScopes.every(function(scope) {
                            return clientScopes.contains(scope);
                        })
                    ).to.be(true);

                    done();
                }, asyncFail(done))
                .then(null, done);
        });
    });

    describe('revokeTokens', function() {
        beforeEach(
            generateBeforeEach(
                'revokeTokens',
                {
                    status: 'ok'
                },
                validClientId
            )
        );

        checksForUid('revokeTokens');
        checksClientID('revokeTokens');
        commonDaoTests();
        passesUid();
        throwsApiError('revokeTokens', validClientId);

        it('should call post /1/tokens/revoke', function() {
            expect(this.dao.call.calledWith('post', '/1/tokens/revoke')).to.be(true);
        });

        it('should pass client id to the dao call', function() {
            expect(this.callData).to.have.property('client_id', validClientId);
        });
    });

    describe('clientInfo', function() {
        beforeEach(
            generateBeforeEach(
                'clientInfo',
                {
                    status: 'ok',
                    client: {
                        id: '0d66fca6b5a040aa90340eabd473db19',
                        title: 'Test client',
                        description: 'Client for test',
                        icon: 'http://icon',
                        icon_id: '3374/e0778950ab864f87bc9c49b896f5d1a0-3',
                        icon_url:
                            'https://avatars.mdst.yandex.net/get-oauth/3374/e0778950ab864f87bc9c49b896f5d1a0-3/normal',
                        homepage: 'http://homepage',
                        callback: 'http://callback',
                        scopes: {
                            Test: {
                                'test:foo': {
                                    title: 'Foo',
                                    requires_approval: false,
                                    ttl: null,
                                    is_ttl_refreshable: false
                                },
                                'test:bar': {
                                    title: 'Bar',
                                    requires_approval: false,
                                    ttl: null,
                                    is_ttl_refreshable: false
                                }
                            }
                        },
                        create_time: 1407477045,
                        secret: '0d66fca6b5a040aa90340eabd473db20',
                        approval_status: 0,
                        blocked: false
                    },
                    viewed_by_owner: true
                },
                validClientId
            )
        );

        checksClientID('clientInfo');
        commonDaoTests();
        passesUid(); //If uid is defined
        passesLang();
        throwsApiError('clientInfo', validClientId);

        it('should not throw if uid is not defined', function() {
            var api = new this.Api(this.logId, this.dao, this.consumer, this.headers, this.lang);

            expect(function() {
                api.clientInfo(validClientId);
            }).to.not.throwError();
        });

        it('should not pass uid to api if it is not defined', function(done) {
            var that = this;

            this.dao.call.returns(when.resolve(_.clone(this.response, true)));
            new this.Api(this.logId, this.dao, this.consumer, this.headers, this.lang)
                .clientInfo(validClientId)
                .then(function() {
                    expect(that.dao.call.secondCall.args[2]).to.not.have.property('uid');
                    done();
                }, asyncFail(done, 'Expected the promise to be resolved'))
                .then(null, done);
        });

        it('should call get /2/client/info', function() {
            expect(this.dao.call.calledWith('get', '/2/client/info')).to.be(true);
        });

        it('should pass client id to the dao call', function() {
            expect(this.callData).to.have.property('client_id', validClientId);
        });

        it('should return a client model', function(done) {
            this.result
                .then(function(result) {
                    expect(result).to.be.a(require('../../OAuth/models/Client'));
                    done();
                }, asyncFail(done))
                .then(null, done);
        });

        it("should populate the client's scopes collection with scopes", function(done) {
            var that = this;

            this.result
                .then(function(client) {
                    var expectedScopes = _.flatten(
                        _.map(that.response.client.scopes, function(scopes) {
                            return _.map(scopes, function(scope, id) {
                                return new Scope(id, scope);
                            });
                        })
                    );

                    expect(client.getScopes().length).to.be(2);
                    expect(
                        expectedScopes.every(function(scope) {
                            return client.getScopes().contains(scope);
                        })
                    ).to.be(true);

                    done();
                }, asyncFail(done))
                .then(null, done);
        });
    });

    describe('createClient', function() {
        var title = 'My Client';
        var description = 'Once upon a time in a galaxy far far away...';
        var homepage = 'https://amazon.com';
        var redirectUrl = 'http://er.ru';
        var isUserCorporate = false;
        var isYandex = true;
        var iconId = '3374/e0778950ab864f87bc9c49b896f5d1a0-3';
        var iconFile = {
            size: 2,
            path: './test/oauth/test.png'
        };

        var scopeId = 'myScope';
        var scope = new Scope(scopeId, {
            title: 'Scope title',
            requires_approval: false,
            ttl: null,
            is_ttl_refreshable: false
        });
        var scopes = new ScopesCollection(scope);

        beforeEach(
            generateBeforeEach(
                'createClient',
                {
                    status: 'ok',
                    client_id: '0d66fca6b5a040aa90340eabd473db19'
                },
                title,
                description,
                scopes,
                homepage,
                redirectUrl,
                isUserCorporate,
                isYandex,
                iconId,
                iconFile
            )
        );

        checksForUid('createClient');
        commonDaoTests();
        passesUid();
        throwsApiError(
            'createClient',
            title,
            description,
            scopes,
            homepage,
            redirectUrl,
            isUserCorporate,
            isYandex,
            iconId,
            iconFile
        );

        it('should not pass the lang', function() {
            expect(this.callData).to.not.have.property('language');
        });

        it('should call post /1/client/create', function() {
            expect(this.dao.call.calledWith('post', '/1/client/create')).to.be(true);
        });

        it('should pass the title', function() {
            expect(this.callData).to.have.property('title', title);
        });

        it('should pass the description', function() {
            expect(this.callData).to.have.property('description', description);
        });

        it('should pass the icon_id', function() {
            expect(this.callData).to.have.property('icon_id', iconId);
        });

        it('should pass the icon_file', function() {
            expect(this.callData).to.have.property('icon_file');
        });

        it('should pass the homepage', function() {
            expect(this.callData).to.have.property('homepage', homepage);
        });

        it('should pass the redirect_uri', function() {
            expect(this.callData).to.have.property('redirect_uri', redirectUrl);
        });

        it('should pass the is_user_corporate flag', function() {
            expect(this.callData).to.have.property('is_user_corporate', isUserCorporate.toString());
        });

        it('should pass the is_yandex flag', function() {
            expect(this.callData).to.have.property('is_yandex', isYandex.toString());
        });

        it('should pass the scopes as an array of ids', function() {
            expect(this.callData.scopes).to.eql([scopeId]);
        });

        it('should resolve with a client id', function(done) {
            var that = this;

            this.result
                .then(function(result) {
                    expect(result).to.be(that.response.client_id);
                    done();
                }, asyncFail(done))
                .then(null, done);
        });
    });

    describe('editClient', function() {
        var title = 'My Client';
        var description = 'Once upon a time in a galaxy far far away...';
        var icon = 'http://google.com/logo.png';
        var homepage = 'https://amazon.com';
        var redirectUrl = 'http://er.ru';
        var isUserCorporate = true;
        var isYandex = false;
        var iconId = '3374/e0778950ab864f87bc9c49b896f5d1a0-3';
        var iconFile = {
            size: 2,
            path: './test/oauth/test.png'
        };
        var deleteIcon = false;

        var scopeId = 'myScope';
        var scope = new Scope(scopeId, {
            title: 'Scope title',
            requires_approval: false,
            ttl: null,
            is_ttl_refreshable: false
        });
        var scopes = new ScopesCollection(scope);

        beforeEach(
            generateBeforeEach(
                'editClient',
                {
                    status: 'ok'
                },
                validClientId,
                title,
                description,
                scopes,
                homepage,
                redirectUrl,
                isUserCorporate,
                isYandex,
                iconId,
                iconFile,
                deleteIcon
            )
        );

        checksForUid(
            'editClient',
            validClientId,
            title,
            description,
            scopes,
            icon,
            homepage,
            redirectUrl,
            isUserCorporate,
            isYandex
        );
        checksClientID(
            'editClient',
            title,
            description,
            scopes,
            icon,
            homepage,
            redirectUrl,
            isUserCorporate,
            isYandex
        );
        commonDaoTests();
        passesUid();
        throwsApiError(
            'editClient',
            validClientId,
            title,
            description,
            scopes,
            homepage,
            redirectUrl,
            isUserCorporate,
            isYandex,
            iconId,
            iconFile,
            deleteIcon
        );

        it('should not pass the lang', function() {
            expect(this.callData).to.not.have.property('language');
        });

        it('should call post /1/client/edit', function() {
            expect(this.dao.call.calledWith('post', '/1/client/edit')).to.be(true);
        });

        it('should pass the title', function() {
            expect(this.callData).to.have.property('title', title);
        });

        it('should pass the description', function() {
            expect(this.callData).to.have.property('description', description);
        });

        it('should pass the icon_id', function() {
            expect(this.callData).to.have.property('icon_id', iconId);
        });

        it('should pass the icon_file', function() {
            expect(this.callData).to.have.property('icon_file');
        });

        it('should pass the homepage', function() {
            expect(this.callData).to.have.property('homepage', homepage);
        });

        it('should pass the redirect_uri', function() {
            expect(this.callData).to.have.property('redirect_uri', redirectUrl);
        });

        it('should pass the is_user_corporate flag', function() {
            expect(this.callData).to.have.property('is_user_corporate', isUserCorporate.toString());
        });

        it('should pass the is_yandex flag', function() {
            expect(this.callData).to.have.property('is_yandex', isYandex.toString());
        });

        it('should pass the scopes as an array of ids', function() {
            expect(this.callData.scopes).to.eql([scopeId]);
        });
    });

    describe('deleteClient', function() {
        beforeEach(
            generateBeforeEach(
                'deleteClient',
                {
                    status: 'ok'
                },
                validClientId
            )
        );

        checksForUid('deleteClient');
        checksClientID('deleteClient');
        commonDaoTests();
        passesUid();
        throwsApiError('deleteClient', validClientId);

        it('should call post /1/client/delete', function() {
            expect(this.dao.call.calledWith('post', '/1/client/delete')).to.be(true);
        });

        it('should not pass the lang', function() {
            expect(this.callData).to.not.have.property('language');
        });

        it('should pass client id to the dao call', function() {
            expect(this.callData).to.have.property('client_id', validClientId);
        });
    });

    describe('deleteClientV2', function() {
        beforeEach(
            generateBeforeEach(
                'deleteClientV2',
                {
                    status: 'ok'
                },
                validClientId
            )
        );

        checksForUid('deleteClientV2');
        checksClientID('deleteClientV2');
        commonDaoTests();
        passesUid();
        throwsApiError('deleteClientV2', validClientId);

        it('should call post /2/client/delete', function() {
            expect(this.dao.call.calledWith('post', '/2/client/delete')).to.be(true);
        });

        it('should not pass the lang', function() {
            expect(this.callData).to.not.have.property('language');
        });

        it('should pass client id to the dao call', function() {
            expect(this.callData).to.have.property('client_id', validClientId);
        });
    });

    describe('gLogoutClient', function() {
        beforeEach(
            generateBeforeEach(
                'gLogoutClient',
                {
                    status: 'ok'
                },
                validClientId
            )
        );

        checksForUid('gLogoutClient');
        checksClientID('gLogoutClient');
        commonDaoTests();
        passesUid();
        throwsApiError('gLogoutClient', validClientId);

        it('should call post /1/client/glogout', function() {
            expect(this.dao.call.calledWith('post', '/1/client/glogout')).to.be(true);
        });

        it('should not pass the lang', function() {
            expect(this.callData).to.not.have.property('language');
        });

        it('should pass client id to the dao call', function() {
            expect(this.callData).to.have.property('client_id', validClientId);
        });
    });

    describe('newClientSecret', function() {
        beforeEach(
            generateBeforeEach(
                'newClientSecret',
                {
                    status: 'ok',
                    secret: '0d66fca6b5a040aa90340eabd473db20'
                },
                validClientId
            )
        );

        checksForUid('newClientSecret');
        checksClientID('newClientSecret');
        commonDaoTests();
        passesUid();
        throwsApiError('newClientSecret', validClientId);

        it('should call post /1/client/secret/new', function() {
            expect(this.dao.call.calledWith('post', '/1/client/secret/new')).to.be(true);
        });

        it('should not pass the lang', function() {
            expect(this.callData).to.not.have.property('language');
        });

        it('should pass client id to the dao call', function() {
            expect(this.callData).to.have.property('client_id', validClientId);
        });

        it('should resolve with a new secret', function(done) {
            var that = this;

            this.result
                .then(function(result) {
                    expect(result).to.be(that.response.secret);
                    done();
                }, asyncFail(done))
                .then(null, done);
        });
    });

    describe('newClientSecretV2', function() {
        beforeEach(
            generateBeforeEach(
                'newClientSecretV2',
                {
                    status: 'ok',
                    secret: '0d66fca6b5a040aa90340eabd473db20'
                },
                validClientId
            )
        );

        checksForUid('newClientSecretV2');
        checksClientID('newClientSecretV2');
        commonDaoTests();
        passesUid();
        throwsApiError('newClientSecretV2', validClientId);

        it('should call post /2/client/secret/new', function() {
            expect(this.dao.call.calledWith('post', '/2/client/secret/new')).to.be(true);
        });

        it('should not pass the lang', function() {
            expect(this.callData).to.not.have.property('language');
        });

        it('should pass client id to the dao call', function() {
            expect(this.callData).to.have.property('client_id', validClientId);
        });

        it('should resolve with a new secret', function(done) {
            var that = this;

            this.result
                .then(function(result) {
                    expect(result).to.be(that.response.secret);
                    done();
                }, asyncFail(done))
                .then(null, done);
        });
    });

    describe('undoNewClientSecret', function() {
        beforeEach(
            generateBeforeEach(
                'undoNewClientSecret',
                {
                    status: 'ok',
                    secret: '0d66fca6b5a040aa90340eabd473db20'
                },
                validClientId
            )
        );

        checksForUid('undoNewClientSecret');
        checksClientID('undoNewClientSecret');
        commonDaoTests();
        passesUid();
        throwsApiError('undoNewClientSecret', validClientId);

        it('should call post /1/client/secret/undo', function() {
            expect(this.dao.call.calledWith('post', '/1/client/secret/undo')).to.be(true);
        });

        it('should not pass the lang', function() {
            expect(this.callData).to.not.have.property('language');
        });

        it('should pass client id to the dao call', function() {
            expect(this.callData).to.have.property('client_id', validClientId);
        });

        it('should resolve with a new secret', function(done) {
            var that = this;

            this.result
                .then(function(result) {
                    expect(result).to.be(that.response.secret);
                    done();
                }, asyncFail(done))
                .then(null, done);
        });
    });

    describe('undoNewClientSecretV2', function() {
        beforeEach(
            generateBeforeEach(
                'undoNewClientSecretV2',
                {
                    status: 'ok',
                    secret: '0d66fca6b5a040aa90340eabd473db20'
                },
                validClientId
            )
        );

        checksForUid('undoNewClientSecretV2');
        checksClientID('undoNewClientSecretV2');
        commonDaoTests();
        passesUid();
        throwsApiError('undoNewClientSecretV2', validClientId);

        it('should call post /2/client/secret/undo', function() {
            expect(this.dao.call.calledWith('post', '/2/client/secret/undo')).to.be(true);
        });

        it('should not pass the lang', function() {
            expect(this.callData).to.not.have.property('language');
        });

        it('should pass client id to the dao call', function() {
            expect(this.callData).to.have.property('client_id', validClientId);
        });

        it('should resolve with a new secret', function(done) {
            var that = this;

            this.result
                .then(function(result) {
                    expect(result).to.be(that.response.secret);
                    done();
                }, asyncFail(done))
                .then(null, done);
        });
    });

    describe('settings', function() {
        beforeEach(
            generateBeforeEach('settings', {
                status: 'ok',
                invalidate_tokens_on_callback_change: true
            })
        );

        commonDaoTests();
        throwsApiError('settings');

        it('should call get /1/global/settings', function() {
            expect(this.dao.call.calledWith('get', '/1/global/settings')).to.be(true);
        });
    });

    describe('allScopes', function() {
        beforeEach(
            generateBeforeEach('allScopes', {
                status: 'ok',
                all_scopes: {
                    Test: {
                        'test:foo': {
                            title: 'Foo',
                            requires_approval: false,
                            ttl: null,
                            is_ttl_refreshable: false
                        },
                        'test:bar': {
                            title: 'Foo',
                            requires_approval: false,
                            ttl: 120,
                            is_ttl_refreshable: true
                        }
                    }
                }
            })
        );
        commonDaoTests();
        passesLang();
        throwsApiError('allScopes');

        it('should call get /1/scopes/all', function() {
            expect(this.dao.call.calledWith('get', '/1/scopes/all')).to.be(true);
        });

        it('should resolve with a scopes collection', function(done) {
            this.result
                .then(function(result) {
                    expect(result).to.be.a(ScopesCollection);
                    done();
                }, asyncFail(done))
                .then(null, done);
        });

        it('should populate scopes collection', function(done) {
            var that = this;

            this.result
                .then(function(result) {
                    var expectedScopes = _.flatten(
                        _.map(that.response.all_scopes, function(scopes) {
                            return _.map(scopes, function(scope, id) {
                                return new Scope(id, scope);
                            });
                        })
                    );

                    expect(result.length).to.be(2);
                    expect(
                        expectedScopes.every(function(scope) {
                            return result.contains(scope);
                        })
                    ).to.be(true);

                    done();
                }, asyncFail(done))
                .then(null, done);
        });
    });

    describe('visibleScopes', function() {
        beforeEach(
            generateBeforeEach('visibleScopes', {
                status: 'ok',
                visible_scopes: {
                    Test: {
                        'test:foo': {
                            title: 'Foo',
                            requires_approval: false,
                            ttl: null,
                            is_ttl_refreshable: false
                        },
                        'test:bar': {
                            title: 'Foo',
                            requires_approval: false,
                            ttl: 120,
                            is_ttl_refreshable: true
                        }
                    }
                }
            })
        );

        checksForUid('visibleScopes');
        commonDaoTests();
        passesUid();
        passesLang();
        throwsApiError('visibleScopes');

        it('should call get /1/scopes/visible', function() {
            expect(this.dao.call.calledWith('get', '/1/scopes/visible')).to.be(true);
        });

        it('should resolve with a scopes collection', function(done) {
            this.result
                .then(function(result) {
                    expect(result).to.be.a(ScopesCollection);
                    done();
                }, asyncFail(done))
                .then(null, done);
        });

        it('should populate scopes collection', function(done) {
            var that = this;

            this.result
                .then(function(result) {
                    var expectedScopes = _.flatten(
                        _.map(that.response.visible_scopes, function(scopes) {
                            return _.map(scopes, function(scope, id) {
                                return new Scope(id, scope);
                            });
                        })
                    );

                    expect(result.length).to.be(2);
                    expect(
                        expectedScopes.every(function(scope) {
                            return result.contains(scope);
                        })
                    ).to.be(true);

                    done();
                }, asyncFail(done))
                .then(null, done);
        });
    });

    describe('userInfo', function() {
        beforeEach(
            generateBeforeEach(
                'userInfo',
                {
                    status: 'ok',
                    visible_scopes: {
                        Test: {
                            'test:foo': {
                                title: 'Foo',
                                requires_approval: false,
                                ttl: null,
                                is_ttl_refreshable: false
                            },
                            'test:bar': {
                                title: 'Foo',
                                requires_approval: false,
                                ttl: 120,
                                is_ttl_refreshable: true
                            }
                        }
                    },
                    is_ip_internal: true,
                    allow_register_yandex_clients: true
                },
                true
            )
        );

        checksForUid('userInfo', true);
        commonDaoTests();
        passesUid();
        passesLang();
        throwsApiError('userInfo', true);

        it('should call get /1/user/info', function() {
            expect(this.dao.call.calledWith('get', '/1/user/info')).to.be(true);
        });

        it('should throw if isCorporate flag is not given', function() {
            var that = this;

            expect(function() {
                that.api.userInfo();
            }).to.throwError(function(err) {
                expect(err.message).to.be('isCorporate flag should be a boolean');
            });
        });

        it('should resolve with a hash containing scopes collection', function(done) {
            this.result
                .then(function(result) {
                    expect(result.scopes).to.be.a(ScopesCollection);
                    done();
                }, asyncFail(done))
                .then(null, done);
        });

        it('should populate scopes collection', function(done) {
            var that = this;

            this.result
                .then(function(result) {
                    var expectedScopes = _.flatten(
                        _.map(that.response.visible_scopes, function(scopes) {
                            return _.map(scopes, function(scope, id) {
                                return new Scope(id, scope);
                            });
                        })
                    );

                    expect(result.scopes.length).to.be(2);
                    expect(
                        expectedScopes.every(function(scope) {
                            return result.scopes.contains(scope);
                        })
                    ).to.be(true);

                    done();
                }, asyncFail(done))
                .then(null, done);
        });

        it('should populate ipInternal and allowRegisteringYandexClients keys', function(done) {
            var that = this;

            this.result
                .then(function(result) {
                    expect(result).to.have.property('ipInternal', that.response.is_ip_internal);
                    expect(result).to.have.property(
                        'allowRegisteringYandexClients',
                        that.response.allow_register_yandex_clients
                    );

                    done();
                }, asyncFail(done))
                .then(null, done);
        });
    });

    describe('userInfoV2', function() {
        beforeEach(
            generateBeforeEach(
                'userInfoV2',
                {
                    status: 'ok',
                    visible_scopes: {
                        Test: {
                            'test:foo': {
                                title: 'Foo',
                                requires_approval: false,
                                ttl: null,
                                is_ttl_refreshable: false
                            },
                            'test:bar': {
                                title: 'Foo',
                                requires_approval: false,
                                ttl: 120,
                                is_ttl_refreshable: true
                            }
                        }
                    },
                    is_ip_internal: true,
                    allow_register_yandex_clients: true
                },
                true
            )
        );

        checksForUid('userInfo', true);
        commonDaoTests();
        passesUid();
        passesLang();
        throwsApiError('userInfo', true);

        it('should call get /2/user/info', function() {
            expect(this.dao.call.calledWith('get', '/2/user/info')).to.be(true);
        });

        it('should resolve with a hash containing scopes collection', function(done) {
            this.result
                .then(function(result) {
                    expect(result.scopes).to.be.a(ScopesCollection);
                    done();
                }, asyncFail(done))
                .then(null, done);
        });

        it('should populate scopes collection', function(done) {
            var that = this;

            this.result
                .then(function(result) {
                    var expectedScopes = _.flatten(
                        _.map(that.response.visible_scopes, function(scopes) {
                            return _.map(scopes, function(scope, id) {
                                return new Scope(id, scope);
                            });
                        })
                    );

                    expect(result.scopes.length).to.be(2);
                    expect(
                        expectedScopes.every(function(scope) {
                            return result.scopes.contains(scope);
                        })
                    ).to.be(true);

                    done();
                }, asyncFail(done))
                .then(null, done);
        });

        it('should populate ipInternal and allowRegisteringYandexClients keys', function(done) {
            var that = this;

            this.result
                .then(function(result) {
                    expect(result).to.have.property('ipInternal', that.response.is_ip_internal);
                    expect(result).to.have.property(
                        'allowRegisteringYandexClients',
                        that.response.allow_register_yandex_clients
                    );

                    done();
                }, asyncFail(done))
                .then(null, done);
        });
    });

    describe('authorizeSubmit', function() {
        var userIp = '127.0.0.0.1';
        var responseType = 'token';
        var redirectUrl = 'tor://silkroad.onion';
        var state = 'All your base';
        var deviceId = 'deadbeef';
        var deviceName = 'Toaster in bathroom';
        var tokensRevokeTime = '00';
        var appPasswordsRevokeTime = '00';
        var webSessionsRevokeTime = '00';

        beforeEach(
            generateBeforeEach(
                'authorizeSubmit',
                {
                    status: 'ok',
                    request_id: '1d66fca6b5a040aa90340eabd473db19',
                    require_user_confirm: true,
                    requested_scopes: {
                        Test: {
                            'test:foo': {
                                title: 'Foo',
                                requires_approval: false,
                                ttl: null,
                                is_ttl_refreshable: false
                            },
                            'test:bar': {
                                title: 'Foo',
                                requires_approval: false,
                                ttl: 120,
                                is_ttl_refreshable: true
                            }
                        }
                    }
                },
                glogoutTime,
                validClientId,
                userIp,
                responseType,
                redirectUrl,
                state,
                deviceId,
                deviceName,
                tokensRevokeTime,
                appPasswordsRevokeTime,
                webSessionsRevokeTime
            )
        );

        checksForUid(
            'authorizeSubmit',
            glogoutTime,
            validClientId,
            userIp,
            responseType,
            redirectUrl,
            state,
            deviceId,
            deviceName,
            tokensRevokeTime,
            appPasswordsRevokeTime,
            webSessionsRevokeTime
        );
        checksGlogoutTime(
            'authorizeSubmit',
            validClientId,
            userIp,
            responseType,
            redirectUrl,
            state,
            deviceId,
            deviceName,
            tokensRevokeTime,
            appPasswordsRevokeTime,
            webSessionsRevokeTime
        );
        checksClientID(
            'authorizeSubmit',
            glogoutTime,
            userIp,
            responseType,
            redirectUrl,
            state,
            deviceId,
            deviceName,
            tokensRevokeTime,
            appPasswordsRevokeTime,
            webSessionsRevokeTime
        );
        commonDaoTests();
        passesUid();
        passesLang();
        throwsApiError(
            'authorizeSubmit',
            glogoutTime,
            validClientId,
            userIp,
            responseType,
            redirectUrl,
            state,
            deviceId,
            deviceName,
            tokensRevokeTime,
            appPasswordsRevokeTime,
            webSessionsRevokeTime
        );

        it('should call post /2/authorize/submit', function() {
            expect(this.dao.call.calledWith('post', '/2/authorize/submit')).to.be(true);
        });

        it('should pass glogout time to the dao call', function() {
            expect(this.callData).to.have.property('user_glogout_time', glogoutTime);
        });

        it('should pass the client id', function() {
            expect(this.callData).to.have.property('client_id', validClientId);
        });

        it('should pass the user ip', function() {
            expect(this.callData).to.have.property('user_ip', userIp);
        });

        it('should pass response type to dao call', function() {
            expect(this.callData).to.have.property('response_type', responseType);
        });

        it('should pass redirectUrl to dao call', function() {
            expect(this.callData).to.have.property('redirect_uri', redirectUrl);
        });

        it('should pass state to dao call', function() {
            expect(this.callData).to.have.property('state', state);
        });

        it('should pass deviceId to dao call', function() {
            expect(this.callData).to.have.property('device_id', deviceId);
        });

        it('should pass deviceName to dao call', function() {
            expect(this.callData).to.have.property('device_name', deviceName);
        });

        it('should pass user_tokens_revoke_time to dao call', function() {
            expect(this.callData).to.have.property('user_tokens_revoke_time', tokensRevokeTime);
        });

        it('should pass user_app_passwords_revoke_time to dao call', function() {
            expect(this.callData).to.have.property('user_app_passwords_revoke_time', appPasswordsRevokeTime);
        });

        it('should pass user_web_sessions_revoke_time to dao call', function() {
            expect(this.callData).to.have.property('user_web_sessions_revoke_time', webSessionsRevokeTime);
        });

        it('should return a ScopesCollection as requested_scopes', function(done) {
            this.result
                .then(function(response) {
                    expect(response.requested_scopes).to.be.a(ScopesCollection);

                    done();
                }, asyncFail(done))
                .then(null, done);
        });

        it('should populate the scopesCollection with the scopes', function(done) {
            var expectedScopes = _.flatten(
                _.map(this.response.requested_scopes, function(scopes) {
                    return _.map(scopes, function(scope, id) {
                        return new Scope(id, scope);
                    });
                })
            );

            this.result
                .then(function(response) {
                    var actualScopes = response.requested_scopes;

                    expect(actualScopes.length).to.be(2);
                    expect(
                        expectedScopes.every(function(scope) {
                            return actualScopes.contains(scope);
                        })
                    ).to.be(true);

                    done();
                }, asyncFail(done))
                .then(null, done);
        });
    });

    describe('authorizeCommit', function() {
        var userIp = '127.0.0.0.1';
        var requestId = 'd3adb33f';
        var tokensRevokeTime = '00';
        var appPasswordsRevokeTime = '00';
        var webSessionsRevokeTime = '00';

        beforeEach(
            generateBeforeEach(
                'authorizeCommit',
                {
                    status: 'ok',
                    request_id: '1d66fca6b5a040aa90340eabd473db19',
                    require_user_confirm: true,
                    requested_scopes: {
                        'test:foo': 'Foo',
                        'test:bar': 'Bar'
                    }
                },
                glogoutTime,
                userIp,
                requestId,
                tokensRevokeTime,
                appPasswordsRevokeTime,
                webSessionsRevokeTime
            )
        );
        checksForUid(
            'authorizeCommit',
            glogoutTime,
            userIp,
            requestId,
            tokensRevokeTime,
            appPasswordsRevokeTime,
            webSessionsRevokeTime
        );
        checksGlogoutTime(
            'authorizeCommit',
            userIp,
            requestId,
            tokensRevokeTime,
            appPasswordsRevokeTime,
            webSessionsRevokeTime
        );
        commonDaoTests();
        passesUid();
        throwsApiError(
            'authorizeCommit',
            glogoutTime,
            userIp,
            requestId,
            tokensRevokeTime,
            appPasswordsRevokeTime,
            webSessionsRevokeTime
        );

        it('should call post /1/authorize/commit', function() {
            expect(this.dao.call.calledWith('post', '/1/authorize/commit')).to.be(true);
        });

        it('should pass glogout time to the dao call', function() {
            expect(this.callData).to.have.property('user_glogout_time', glogoutTime);
        });

        it('should not pass the lang to dao call', function() {
            expect(this.callData).to.not.have.property('language');
        });

        it('should pass the user ip', function() {
            expect(this.callData).to.have.property('user_ip', userIp);
        });

        it('should pass the request id', function() {
            expect(this.callData).to.have.property('request_id', requestId);
        });

        it('should pass user_tokens_revoke_time to dao call', function() {
            expect(this.callData).to.have.property('user_tokens_revoke_time', tokensRevokeTime);
        });

        it('should pass user_app_passwords_revoke_time to dao call', function() {
            expect(this.callData).to.have.property('user_app_passwords_revoke_time', appPasswordsRevokeTime);
        });

        it('should pass user_web_sessions_revoke_time to dao call', function() {
            expect(this.callData).to.have.property('user_web_sessions_revoke_time', webSessionsRevokeTime);
        });

        it('should reject with an ApiError if there was a retry error due to request.not_found', function(done) {
            this.dao.call.returns(
                when.reject(new (require('../../error/RetryError'))('Message', this.response, 'request.not_found'))
            );

            var that = this;

            this.api
                .authorizeCommit(
                    glogoutTime,
                    userIp,
                    requestId,
                    tokensRevokeTime,
                    appPasswordsRevokeTime,
                    webSessionsRevokeTime
                )
                .then(asyncFail(done, 'Expected the promise to be rejected'), function(error) {
                    expect(error).to.be.a(that.Api.ApiError);
                    expect(error.getResponse()).to.eql(that.response);
                    done();
                })
                .then(null, done);
        });
    });

    describe('authorizeGetState', function() {
        var userIp = '127.0.0.0.1';
        var requestId = 'd3adb33f';
        var tokensRevokeTime = '00';
        var appPasswordsRevokeTime = '00';
        var webSessionsRevokeTime = '00';

        beforeEach(
            generateBeforeEach(
                'authorizeGetState',
                {
                    status: 'ok',
                    request_id: '1d66fca6b5a040aa90340eabd473db19',
                    require_user_confirm: true,
                    requested_scopes: {
                        'test:foo': 'Foo',
                        'test:bar': 'Bar'
                    }
                },
                glogoutTime,
                userIp,
                requestId,
                tokensRevokeTime,
                appPasswordsRevokeTime,
                webSessionsRevokeTime
            )
        );
        checksForUid(
            'authorizeGetState',
            glogoutTime,
            userIp,
            requestId,
            tokensRevokeTime,
            appPasswordsRevokeTime,
            webSessionsRevokeTime
        );
        checksGlogoutTime(
            'authorizeGetState',
            userIp,
            requestId,
            tokensRevokeTime,
            appPasswordsRevokeTime,
            webSessionsRevokeTime
        );
        commonDaoTests();
        passesUid();
        throwsApiError(
            'authorizeGetState',
            glogoutTime,
            userIp,
            requestId,
            tokensRevokeTime,
            appPasswordsRevokeTime,
            webSessionsRevokeTime
        );

        it('should call post /1/authorize/get_state', function() {
            expect(this.dao.call.calledWith('post', '/1/authorize/get_state')).to.be(true);
        });

        it('should pass glogout time to the dao call', function() {
            expect(this.callData).to.have.property('user_glogout_time', glogoutTime);
        });

        it('should not pass the lang to dao call', function() {
            expect(this.callData).to.not.have.property('language');
        });

        it('should pass the user ip', function() {
            expect(this.callData).to.have.property('user_ip', userIp);
        });

        it('should pass the request id', function() {
            expect(this.callData).to.have.property('request_id', requestId);
        });

        it('should pass user_tokens_revoke_time to dao call', function() {
            expect(this.callData).to.have.property('user_tokens_revoke_time', tokensRevokeTime);
        });

        it('should pass user_app_passwords_revoke_time to dao call', function() {
            expect(this.callData).to.have.property('user_app_passwords_revoke_time', appPasswordsRevokeTime);
        });

        it('should pass user_web_sessions_revoke_time to dao call', function() {
            expect(this.callData).to.have.property('user_web_sessions_revoke_time', webSessionsRevokeTime);
        });

        it('should reject with an ApiError if there was a retry error due to request.not_found', function(done) {
            this.dao.call.returns(
                when.reject(new (require('../../error/RetryError'))('Message', this.response, 'request.not_found'))
            );

            var that = this;

            this.api
                .authorizeGetState(
                    glogoutTime,
                    userIp,
                    requestId,
                    tokensRevokeTime,
                    appPasswordsRevokeTime,
                    webSessionsRevokeTime
                )
                .then(asyncFail(done, 'Expected the promise to be rejected'), function(error) {
                    expect(error).to.be.a(that.Api.ApiError);
                    expect(error.getResponse()).to.eql(that.response);
                    done();
                })
                .then(null, done);
        });
    });

    describe('ApiError', function() {
        beforeEach(function() {
            this.Error = this.Api.ApiError;
            this.error = new this.Error(this.apiErrorResponse.errors, this.apiErrorResponse);
        });

        describe('contains', function() {
            it('should return true if the code is among the errors', function() {
                expect(this.error.contains('method.not_allowed')).to.be(true);
            });

            it('should return false if an unknown code given', function() {
                expect(this.error.contains('something absolutely irrelevant')).to.be(false);
            });
        });

        describe('getResponse', function() {
            it('should return a response error was created with', function() {
                expect(this.error.getResponse()).to.be(this.apiErrorResponse);
            });
        });
    });
});
