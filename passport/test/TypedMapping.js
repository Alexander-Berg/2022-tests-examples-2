var expect = require('expect.js');
var inherit = require('inherit');

describe('Typed Mapping routing', function() {
    beforeEach(function() {
        this.Type = inherit({});
        this.TypeSuccessor = inherit(this.Type, {});

        this.typeInstance = new this.Type();

        this.Router = require('../TypedMapping');
        this.router = new this.Router(this.Type);
    });

    describe('Constructor', function() {
        it('should throw if called with anything but a function', function() {
            var Router = this.Router;

            expect(function() {
                new Router(123);
            }).to.throwError(function(e) {
                expect(e.message).to.be('Type should be a constructor');
            });
        });
    });

    describe('map', function() {
        it(
            'should throw when called with anything but type successor, type instance or an ' +
                'instance of another Router',
            function() {
                var that = this;

                expect(function() {
                    that.router.map('key', 'throw me!');
                }).to.throwError(function(e) {
                    expect(e.message).to.be(
                        'Routing result is a given type successor or TypedMappingRouter with the same type'
                    );
                });
            }
        );

        it('should not throw when called with type instance', function() {
            var that = this;

            expect(function() {
                that.router.map('key', that.typeInstance);
            }).to.not.throwError();
        });

        it('should not throw when called with type successor', function() {
            var that = this;

            expect(function() {
                that.router.map('key', that.TypeSuccessor);
            }).to.not.throwError();
        });

        it('should throw when called with an instance of TypedMappingRouter of different type', function() {
            var that = this;
            var differentTypedRouter = new this.Router(inherit({}));

            expect(function() {
                that.router.map('key', differentTypedRouter);
            }).to.throwError(function(e) {
                expect(e.message).to.be(
                    'Routing result is a given type successor or TypedMappingRouter with the same type'
                );
            });
        });

        it('should not throw when called with an instance of TypedMappingRouter of the same type', function() {
            var that = this;

            expect(function() {
                that.router.map('key', that.router);
            }).to.not.throwError();
        });
    });

    describe('default', function() {
        it('should throw when called with anything but given type successor or instance', function() {
            var that = this;

            expect(function() {
                that.router.default('asfsdfd');
            }).to.throwError(function(e) {
                expect(e.message).to.be('Default route should be a given type successor or a type instance');
            });
        });

        it('should throw when called with another TypedMappingRouter', function() {
            var that = this;

            expect(function() {
                that.router.default(that.router);
            }).to.throwError(function(e) {
                expect(e.message).to.be('Default route should be a given type successor or a type instance');
            });
        });

        it('should not throw when called with given type successor', function() {
            var that = this;

            expect(function() {
                that.router.default(that.TypeSuccessor);
            }).to.not.throwError();
        });

        it('should not throw when called with given type instance', function() {
            var that = this;

            expect(function() {
                that.router.default(that.typeInstance);
            }).to.not.throwError();
        });
    });
});
