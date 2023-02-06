var expect = require('expect.js');
var sinon = require('sinon');
var when = require('when');

var CompositeView = require('../CompositeView');
var View = require('../View');

describe('Composite View', function() {
    beforeEach(function() {
        var CompositeSuccessor = require('inherit')(CompositeView, {
            name: 'TstCompositeView'
        });

        this.composite = new CompositeSuccessor();
    });

    describe('append', function() {
        beforeEach(function() {
            var ViewSuccessor = require('inherit')(View, {
                name: 'TstView'
            });

            this.subView = new ViewSuccessor();
        });

        it('should return the composite for chaining', function() {
            expect(this.composite.append(this.subView)).to.be(this.composite);
        });

        it('should add a view to an array of nested views', function() {
            expect(this.composite.append(this.subView).getSubviews()).to.contain(this.subView);
        });

        it('should throw if a view being appended is not an instance of View', function() {
            var composite = this.composite;

            expect(function() {
                composite.append('nope');
            }).to.throwError(function(e) {
                expect(e.message).to.be('Appended subview should be an instance of View');
            });
        });
    });

    describe('compile', function() {
        beforeEach(function() {
            var TmpView = require('inherit')(View, {
                __constructor: function() {
                    this.comDef = when.defer();
                    this.compile = sinon.stub().returns(this.comDef.promise);
                }
            });

            this.subviews = [new TmpView(), new TmpView()];

            var composite = this.composite;

            this.subviews.forEach(function(view) {
                composite.append(view);
            });
        });

        it('should call compile on all the subviews', function() {
            this.composite.compile();
            this.subviews.forEach(function(view) {
                expect(view.compile.calledOnce).to.be(true);
            });
        });

        it('should merge results of subviews compilation into a single object', function(done) {
            this.subviews[0].comDef.resolve({a: 'bc'});
            this.subviews[1].comDef.resolve({d: {e: 'fg'}});

            this.composite
                .compile()
                .then(function(compiled) {
                    expect(compiled).to.eql({
                        a: 'bc',
                        d: {e: 'fg'}
                    });
                    done();
                })
                .then(null, done);
        });

        it("should pass the arguments to subviews' compile methods", function() {
            var arg1 = {};
            var arg2 = {};

            this.composite.compile(arg1, arg2);
            this.subviews.forEach(function(view) {
                expect(view.compile.calledWithExactly(arg1, arg2)).to.be(true);
            });
        });
    });
});
