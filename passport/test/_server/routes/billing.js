var expect = require('expect.js');
var sinon = require('sinon');
var when = require('when');
var _ = require('lodash');

describe('Billing', function() {
    beforeEach(function() {
        this.billing = require('../../../routes/billing');
    });

    describe('XMLRPC Client', function() {
        beforeEach(function() {
            this.host = '127.0.0.1';
            this.port = '1337';
            this.path = '/some/path';

            this.logger = new (require('plog'))('I am a log id, WOW');

            this.client = new this.billing.XMLRPCClient(this.logger, this.host, this.port, this.path);

            sinon.stub(this.client, 'getConnection').returns({
                methodCall: sinon.stub()
            });
        });

        describe('Constructor', function() {
            _.each(
                {
                    'a number': 1,
                    'an object': {},
                    'a boolean': true,
                    undefined: undefined,
                    null: null,
                    'an empty string': ''
                },
                function(value, description) {
                    it(`should throw if host is ${description}`, function() {
                        var that = this;
                        var XMLRPCClient = this.billing.XMLRPCClient;

                        expect(function() {
                            new XMLRPCClient(that.logger, value, that.port, that.path);
                        }).to.throwError(function(e) {
                            expect(e.message).to.be('Host string required');
                        });
                    });

                    it(`should throw if port is ${description}`, function() {
                        var that = this;
                        var XMLRPCClient = this.billing.XMLRPCClient;

                        expect(function() {
                            new XMLRPCClient(that.logger, that.host, value, that.path);
                        }).to.throwError(function(e) {
                            expect(e.message).to.be('Port string required');
                        });
                    });

                    it(`should throw if path is ${description}`, function() {
                        var that = this;
                        var XMLRPCClient = this.billing.XMLRPCClient;

                        expect(function() {
                            new XMLRPCClient(that.logger, that.host, that.port, value);
                        }).to.throwError(function(e) {
                            expect(e.message).to.be('Path string required');
                        });
                    });
                }
            );

            it('should call xmlrpc.createClient with provided host, port and path', function() {
                var xmlrpcModule = require('xmlrpc');

                sinon.stub(xmlrpcModule, 'createClient');

                var expectedConfig = {
                    host: this.host,
                    port: this.port,
                    path: this.path
                };

                new this.billing.XMLRPCClient(this.logger, this.host, this.port, this.path);
                expect(xmlrpcModule.createClient.firstCall.args[0]).to.eql(expectedConfig);

                xmlrpcModule.createClient.restore();
            });
        });

        describe('Call', function() {
            beforeEach(function() {
                this.method = 'someAwkwardXMLRPCMethod';
                this.params = ['first', 'second', {thi: 'rd'}];
            });
            it('should return a promise', function() {
                expect(when.isPromiseLike(this.client.call())).to.be(true);
            });

            it('should call methodCall with provided method and params', function() {
                this.client.call(this.method, this.params);
                expect(this.client.getConnection().methodCall.firstCall.args[0]).to.be(this.method);
                expect(this.client.getConnection().methodCall.firstCall.args[1]).to.eql(this.params);
            });

            it('should resolve the deferred with the method call response if there were no errors', function(done) {
                var originalResponse = 'heyheyhey';

                this.client
                    .call(this.method, this.params)
                    .then(function(response) {
                        expect(response).to.be(originalResponse);
                        done();
                    })
                    .then(null, done);

                this.client.getConnection().methodCall.callArgWith(2, null, originalResponse);
            });

            it('should reject the deferred with the method call errors if there were any', function(done) {
                var originalError = 'oh noes!';

                this.client
                    .call(this.method, this.params)
                    .then(asyncFail(done, 'Expected the promise to be rejected'))
                    .then(null, function(error) {
                        expect(error).to.be(originalError);
                        done();
                    })
                    .then(null, done);

                this.client.getConnection().methodCall.callArgWith(2, originalError, null);
            });
        });
    });

    describe('Billing Service', function() {
        beforeEach(function() {
            var daoCallStub = sinon.stub().returns(when.defer().promise);

            this.daoCallStub = daoCallStub;
            this.dao = {
                call: function(method, params) {
                    return daoCallStub(method, params);
                }
            };

            this.namespace = 'whatsoEver';
            this.token = 'yandex-passport-oteo5miz0IeGhi8Umee9ideed0guKieveePaeCohph0Tuiwohx9HiPet7Ainie8a';
            this.billingService = new this.billing.BillingService(this.dao, this.token, this.namespace);
        });

        describe('Constructor', function() {
            _.each(
                {
                    'a number': 1,
                    'a boolean': true,
                    undefined: undefined,
                    null: null,
                    'a string': 'asdfasdf',
                    'a plain object': {}
                },
                function(value, description) {
                    it(`should throw if dao is ${description}`, function() {
                        var that = this;
                        var BillingService = this.billing.BillingService;

                        expect(function() {
                            new BillingService(value, that.token, that.namespace);
                        }).to.throwError(function(e) {
                            expect(e.message).to.be('DAO should comply with billing service dao interface');
                        });
                    });
                }
            );

            _.each(
                {
                    'a number': 1,
                    'an object': {},
                    'a boolean': true,
                    undefined: undefined,
                    null: null,
                    'an empty string': ''
                },
                function(value, description) {
                    it(`should throw if token is ${description}`, function() {
                        var that = this;
                        var BillingService = this.billing.BillingService;

                        expect(function() {
                            new BillingService(that.dao, value, that.namespace);
                        }).to.throwError(function(e) {
                            expect(e.message).to.be('Token string required');
                        });
                    });

                    it(`should throw if namespace is ${description}`, function() {
                        var that = this;
                        var BillingService = this.billing.BillingService;

                        expect(function() {
                            new BillingService(that.dao, that.token, value);
                        }).to.throwError(function(e) {
                            expect(e.message).to.be('Namespace string required');
                        });
                    });
                }
            );
        });

        describe('listPaymentMethods', function() {
            beforeEach(function() {
                this.uid = '12345';
                this.ip = '192.168.0.6';
            });
            it('should call dao for method ListPaymentMethods', function() {
                this.billingService.listPaymentMethods(this.uid, this.ip);
                expect(this.daoCallStub.calledOnce).to.be(true);
                expect(this.daoCallStub.firstCall.args[0]).to.be(`${this.namespace}.ListPaymentMethods`);
            });

            it('should call dao with token as a first positional arg', function() {
                this.billingService.listPaymentMethods(this.uid, this.ip);
                expect(this.daoCallStub.firstCall.args[1][0]).to.be(this.token);
            });

            it('should call dao with userIP and uid in a hash as a second positional arg', function() {
                this.billingService.listPaymentMethods(this.uid, this.ip);
                expect(this.daoCallStub.firstCall.args[1][1]).to.eql({
                    user_ip: this.ip,
                    uid: this.uid
                });
            });

            it('should return a promise', function() {
                expect(require('when').isPromiseLike(this.billingService.listPaymentMethods(this.uid, this.ip))).to.be(
                    true
                );
            });

            it('should resolve with what dao resolves with', function(done) {
                var daoCallDeferred = when.defer();
                var daoResponse = {whatso: 'ever'};

                daoCallDeferred.resolve(daoResponse);

                this.daoCallStub.returns(daoCallDeferred.promise);
                this.billingService
                    .listPaymentMethods(this.uid, this.ip)
                    .then(function(response) {
                        expect(response).to.be(daoResponse);
                        done();
                    })
                    .then(null, done);
            });

            it('should reject if xmlrpc responded with an exception', function(done) {
                var daoCallDeferred = when.defer();
                var daoResponse = {status: 'error', payload: 'irrelevant'};

                daoCallDeferred.resolve(daoResponse);
                this.daoCallStub.returns(daoCallDeferred.promise);

                this.billingService
                    .listPaymentMethods(this.uid, this.ip)
                    .then(asyncFail(done, 'Expected the promise to be rejected'))
                    .then(null, function(error) {
                        expect(error).to.be.a(Error);
                        expect(error.message).to.contain('DAO responded with "status: error"');
                        done();
                    })
                    .then(null, done);
            });
        });
    });

    describe('listPaymentMethodsAdapter', function() {
        beforeEach(function() {
            this.adapter = this.billing.listPaymentMethodsAdapter;

            this.methods = {
                yamoney: {
                    auth_type: 'token',
                    region_id: '225',
                    number: '41003323614990',
                    currency: 'RUB',
                    balance: '0.00',
                    type: 'yandex_money',
                    id: '41003323614990'
                },

                card: {
                    auth_type: 'token',
                    region_id: 225,
                    mru: 1,
                    system: 'MasterCard',
                    number: '5555****4444',
                    currency: 'RUB',
                    type: 'card',
                    id: '86475080',
                    name: null
                },

                phone: {
                    auth_type: 'token',
                    secure: '1',
                    payment_confirm: 'none',
                    number: '+79262001422',
                    currency: 'RUB',
                    payment_timeout: 20,
                    operator: 'megafon',
                    type: 'phone',
                    id: '2',
                    region_id: '225'
                }
            };
        });

        describe('when parsing type', function() {
            _.each(
                {
                    //MethodKey: expectedType
                    yamoney: 'yamoney',
                    card: 'card',
                    phone: 'phone'
                },
                function(expectedType, methodKey) {
                    it(`should return ${expectedType} for type ${methodKey}`, function() {
                        expect(this.adapter(this.methods[methodKey]).type).to.be(expectedType);
                    });
                }
            );

            it('should return null if it encounters an unknown type', function() {
                this.methods.phone.type = 'someUnknownType';
                expect(this.adapter(this.methods.phone)).to.be(null);
            });
        });

        describe('when parsing name', function() {
            it('should return name if it exists', function() {
                var name = 'My beloved card';

                this.methods.card.name = name;

                expect(this.adapter(this.methods.card).name).to.be(name);
            });

            it('should return Яндекс.Деньги for type yamoney', function() {
                expect(this.adapter(this.methods.yamoney).name).to.be('Яндекс.Деньги');
            });

            ['megafon', 'beeline', 'mts', 'rostelecom', 'tele2'].forEach(function(phoneOperator) {
                it(`should return "Телефон" for operator ${phoneOperator}`, function() {
                    this.methods.phone.operator = phoneOperator;
                    expect(this.adapter(this.methods.phone).name).to.be('Телефон');
                });
            });

            it('should return Телефон for an unknown operator', function() {
                this.methods.phone.operator = 'obscure';
                expect(this.adapter(this.methods.phone).name).to.be('Телефон');
            });

            it('should return system for type card', function() {
                expect(this.adapter(this.methods.card).name).to.be(this.methods.card.system);
            });

            it('should return Банковская карта for a card without a system specified', function() {
                delete this.methods.card.system;
                expect(this.adapter(this.methods.card).name).to.be('Банковская карта');
            });
        });

        describe('when parsing details', function() {
            it('should return account number from the response as method details', function() {
                var adapter = this.adapter;

                _(this.methods)
                    .omit('card')
                    .each(function(method) {
                        expect(adapter(method).details).to.be(method.number);
                    });
            });

            describe('for type card', function() {
                _.each(
                    {
                        '1*1': '1xxx xxxx xxxx xxx1',
                        '12*1': '12xx xxxx xxxx xxx1',
                        '123*1': '123x xxxx xxxx xxx1',
                        '1234*5678': '1234 xxxx xxxx 5678',
                        '123456****4242': '1234 56xx xxxx 4242',
                        '123*45678': '123x xxxx xxx4 5678'
                    },
                    function(expected, input) {
                        it(`should return ${expected} when given ${input} as an input`, function() {
                            this.methods.card.number = input;
                            expect(this.adapter(this.methods.card).details).to.be(expected);
                        });
                    }
                );
            });
        });

        describe('when assigning a link', function() {
            it('should return https://money.yandex.ru/ for type yamoney', function() {
                expect(this.adapter(this.methods.yamoney).link).to.be('https://money.yandex.ru/');
            });

            it('should return http://phone-passport.yandex.ru/phones for type phone', function() {
                expect(this.adapter(this.methods.phone).link).to.be('http://phone-passport.yandex.ru/phones');
            });

            it('should not return a link for type card', function() {
                expect(this.adapter(this.methods.card).link).to.be(undefined);
            });
        });
    });
});
