var expect = require('expect.js');

describe('Interface', function() {
    beforeEach(function() {
        this.method1 = 'method1';
        this.method2 = 'method2';

        this.methodWithArity1 = 'setSomething';
        this.methodWithArity1definition = 'setSomething:1';
        this.methodWithArity2 = 'setAnotherThing';
        this.methodWithArity2definition = 'setAnotherThing:2';

        this.Interface = require('../../../lib/Interface');
    });

    describe('implementedBy', function() {
        it('should return false if the argument is not an object', function() {
            expect(new this.Interface().implementedBy(null)).to.be(false);
            expect(new this.Interface().implementedBy(undefined)).to.be(false);
            expect(new this.Interface().implementedBy(1)).to.be(false);
            expect(new this.Interface().implementedBy('whatever')).to.be(false);
        });

        it('should return true if an object contains all the methods required by the interface', function() {
            var implementation = {};

            implementation[this.method1] = function() {};
            implementation[this.method2] = function() {};

            expect(new this.Interface(this.method1, this.method2).implementedBy(implementation)).to.be(true);
        });

        it('should return false if an object does not contains any required method', function() {
            var implementation = {};

            implementation[this.method1] = function() {};

            expect(new this.Interface(this.method1, this.method2).implementedBy(implementation)).to.be(false);
        });

        it('should return false if an object has a property named as a requried method', function() {
            var implementation = {};

            implementation[this.method1] = function() {};
            implementation[this.method2] = 'vasya';

            expect(new this.Interface(this.method1, this.method2).implementedBy(implementation)).to.be(false);
        });

        it('should return false if an object contains the methods but they have wrong arity', function() {
            var implementation = {};

            implementation[this.methodWithArity1] = function() {};
            implementation[this.methodWithArity2] = function() {};

            expect(
                new this.Interface(this.methodWithArity1definition, this.methodWithArity2definition).implementedBy(
                    implementation
                )
            ).to.be(false);
        });

        it('should return true if an object contains the methods with matching arity', function() {
            var implementation = {};

            // eslint-disable-next-line no-unused-vars
            implementation[this.methodWithArity1] = function(arg) {};
            // eslint-disable-next-line no-unused-vars
            implementation[this.methodWithArity2] = function(arg, anotherArg) {};

            expect(
                new this.Interface(this.methodWithArity1definition, this.methodWithArity2definition).implementedBy(
                    implementation
                )
            ).to.be(true);
        });
    });
});
