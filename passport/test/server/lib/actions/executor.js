var expect = require('expect.js');
var sinon = require('sinon');
var when = require('when');
var _ = require('lodash');

var Executor = require('../../../../lib/actions/executor');
var Action = require('../../../../lib/actions/action');

describe('Action Executor', function() {
    beforeEach(function() {
        this.sampleAction = new Action();

        this.executeDeferred = when.defer();
        sinon.stub(this.sampleAction, 'execute').returns(this.executeDeferred.promise);

        this.executor = new Executor([this.sampleAction]);
    });

    describe('Constructor', function() {
        _.each(
            {
                'is a string': 'abc',
                'is a number': 123,
                'is an object': {},
                'is a boolean': true,
                'contains anything but Actions': ['nope']
            },
            function(value, description) {
                it(`should throw if argument ${description}`, function() {
                    expect(function() {
                        new Executor(value);
                    }).to.throwError(function(e) {
                        expect(e.message).to.be('Executor should be instantiated with an array of Actions');
                    });
                });
            }
        );
    });

    describe('run', function() {
        it('should return a promise', function() {
            expect(when.isPromiseLike(this.executor.run())).to.be(true);
        });

        it('should call next action when the promise of a previous action resolves', function(done) {
            var secondAction = new Action();

            sinon.stub(secondAction, 'execute');

            var executer = new Executor([this.sampleAction, secondAction]);
            var promise = executer.run();

            expect(secondAction.execute.called).to.be(false);
            this.executeDeferred.resolve();

            promise
                .then(function() {
                    expect(secondAction.execute.calledOnce).to.be(true);
                    done();
                })
                .then(null, done);
        });

        it('should call every action with the arguments run was called with', function(done) {
            var arg1 = {};
            var arg2 = {};

            var sampleAction = this.sampleAction;

            this.executor
                .run(arg1, arg2)
                .then(function() {
                    expect(sampleAction.execute.calledWithExactly(arg1, arg2)).to.be(true);
                    done();
                })
                .then(null, done);

            this.executeDeferred.resolve();
        });

        it('should resolve the returned promise when all the action promises are resolved', function(done) {
            var promise = this.executor.run();

            promise
                .then(function() {
                    done();
                })
                .then(null, asyncFail(done, 'Expected the promise to resolve'));

            expect(promise.inspect().state).to.be('pending');
            this.executeDeferred.resolve();
        });

        it('should reject the returned promise if any action promise was rejected', function(done) {
            var promise = this.executor.run();

            promise.then(asyncFail(done, 'Expected the promise to resolve'), function() {
                done();
            });
            expect(promise.inspect().state).to.be('pending');
            this.executeDeferred.reject();
        });

        it('should support actions that do not return a promise', function(done) {
            var action = new Action();

            sinon.stub(action, 'execute');
            var executer = new Executor([action]);

            var promise = executer.run();

            promise
                .then(function() {
                    done();
                })
                .then(null, asyncFail(done, 'Expected the promise to resolve'));
        });

        it("should call action's execute with the context of an action", function(done) {
            var action = this.sampleAction;

            this.executor
                .run()
                .then(function() {
                    expect(action.execute.calledOn(action)).to.be(true);
                    done();
                })
                .then(null, done);
            this.executeDeferred.resolve();
        });
    });
});
