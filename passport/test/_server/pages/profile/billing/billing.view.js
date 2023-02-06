var expect = require('expect.js');
var sinon = require('sinon');
var _ = require('lodash');

var PaymentMethodsView = require('../../../../../pages/profile/billing/billing.view');

describe('Billing Views', function() {
    beforeEach(function() {
        this.Method = PaymentMethodsView.PaymentMethodsGroup.PaymentMethod;
        this.Group = PaymentMethodsView.PaymentMethodsGroup;
        this.Page = PaymentMethodsView;

        this.method = new this.Method('name', 'details');
        this.group = new this.Group('type');
    });
    describe('Payment Method', function() {
        beforeEach(function() {
            this.name = 'Яндекс.Деньги';
            this.details = '41001243572010';
            this.link = 'https://money.yandex.ru';
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
                    it(`should throw if name is ${description}`, function() {
                        var that = this;
                        var Method = this.Method;

                        expect(function() {
                            new Method(value, that.details);
                        }).to.throwError(function(e) {
                            expect(e.message).to.be('Name string required');
                        });
                    });

                    it(`should throw if details are ${description}`, function() {
                        var that = this;
                        var Method = this.Method;

                        expect(function() {
                            new Method(that.name, value);
                        }).to.throwError(function(e) {
                            expect(e.message).to.be('Details string required');
                        });
                    });
                }
            );

            _.each(
                {
                    'a number': 1,
                    'an object': {},
                    'a boolean': true,
                    null: null,
                    'an empty string': ''
                },
                function(value, description) {
                    it(`should throw if link is ${description}`, function() {
                        var that = this;
                        var Method = this.Method;

                        expect(function() {
                            new Method(that.name, that.details, value);
                        }).to.throwError(function(e) {
                            expect(e.message).to.be('Link is optional, but should be a string if passed');
                        });
                    });
                }
            );
        });

        describe('compile', function() {
            it('should return an object with name, details and a link', function() {
                expect(new this.Method(this.name, this.details, this.link).compile()).to.eql({
                    name: this.name,
                    details: this.details,
                    link: this.link
                });
            });

            it('should omit a link if it is null', function() {
                expect(new this.Method(this.name, this.details).compile()).to.eql({
                    name: this.name,
                    details: this.details
                });
            });
        });
    });

    describe('Payment Methods Group', function() {
        beforeEach(function() {
            this.type = 'yamoney';
            this.group = new this.Group(this.type);
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
                    it(`should throw if type is ${description}`, function() {
                        var Group = this.Group;

                        expect(function() {
                            new Group(value);
                        }).to.throwError(function(e) {
                            expect(e.message).to.be('Type string required');
                        });
                    });
                }
            );
        });

        describe('getType', function() {
            it('should return the type group was created with', function() {
                expect(this.group.getType()).to.be(this.type);
            });
        });

        describe('addMethod', function() {
            it('should throw if passed object is not a PaymentMethod', function() {
                var group = this.group;

                expect(function() {
                    group.addMethod('whaaa?');
                }).to.throwError(function(e) {
                    expect(e.message).to.be('Method should be an instance of PaymentMethod');
                });
            });

            it('should return the group itself for chaining', function() {
                expect(this.group.addMethod(this.method)).to.be(this.group);
            });

            it('should add the method to methods list', function() {
                expect(this.group.addMethod(this.method).getMethods()).to.eql([this.method]);
            });
        });

        describe('compile', function() {
            it('should return an object with type and empty array of methods for an empty group', function() {
                expect(this.group.compile()).to.eql({
                    type: this.type,
                    methods: []
                });
            });

            it('should put compiled methods into methods array if group has payment methods', function() {
                var compiledMethod = {
                    iama: 'payment method'
                };

                sinon.stub(this.method, 'compile').returns(compiledMethod);
                this.group.addMethod(this.method);

                var compiledGroup = this.group.compile();

                expect(compiledGroup.methods.length).to.be(1);
                expect(compiledGroup.methods[0]).to.be(compiledMethod);
            });
        });
    });

    describe('Payment Methods View', function() {
        beforeEach(function() {
            this.view = new this.Page();
        });

        describe('addGroup', function() {
            it('should throw if the argument passed is not a PaymentGroup', function() {
                var view = this.view;

                expect(function() {
                    view.addGroup('not a PaymentGroup');
                }).to.throwError(function(e) {
                    expect(e.message).to.be('MethodsGroup should be an instance of PaymentMethodsGroup');
                });
            });

            it('should throw if a group of same type already exists', function() {
                var view = this.view;
                var group = this.group;

                view.addGroup(group); //First time should go ok;

                expect(function() {
                    view.addGroup(group);
                }).to.throwError(function(e) {
                    expect(e.message).to.be('Group of this type already exists');
                });
            });

            it('should return the view itself for chaining', function() {
                expect(this.view.addGroup(this.group)).to.be(this.view);
            });

            it('should add a group to groups list', function() {
                expect(this.view.addGroup(this.group).getGroups()).to.eql([this.group]);
            });
        });

        describe('addMethod', function() {
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
                    it(`should throw if method type is ${description}`, function() {
                        var view = this.view;
                        var method = this.method;

                        expect(function() {
                            view.addMethod(method, value);
                        }).to.throwError(function(e) {
                            expect(e.message).to.be('Type string required');
                        });
                    });
                }
            );

            it('should add a method to existing group of a specified type', function() {
                this.view.addGroup(this.group);
                this.view.addMethod(this.method, this.group.getType());
                expect(this.group.getMethods()).to.contain(this.method);
            });

            it('should create a new group if no group exists of a specified type', function() {
                this.view.addMethod(this.method, 'someType');
                var groups = this.view.getGroups();

                expect(groups.length).to.be(1);
                expect(groups[0].getMethods()).to.contain(this.method);
            });

            it('should return the view instance for chaining', function() {
                expect(this.view.addMethod(this.method, this.group.getType())).to.be(this.view);
            });
        });
    });
});
