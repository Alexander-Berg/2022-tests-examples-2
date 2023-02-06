var expect = require('expect.js');
var Scope = require('../../../OAuth/models/Scope');

describe('Scope model', function() {
    beforeEach(function() {
        this.scopeId = 'bar:baz';
        this.scopeDefinition = {
            title: 'Foo',
            requires_approval: false,
            ttl: null,
            is_ttl_refreshable: false
        };

        this.scopeTitle = 'Foo';

        this.scope = new Scope(this.scopeId, this.scopeDefinition);
    });

    describe('constructor', function() {
        it('should not throw if called without scope definition (only with id)', function() {
            var that = this;

            expect(function() {
                new Scope(that.scopeId);
            }).to.not.throwError();
        });
    });

    describe('setSectionTitle', function() {
        it('should set section title (obviously)', function() {
            var title = 'How much wood would a woodchuck chuck?';

            expect(this.scope.setSectionTitle(title).getSectionTitle()).to.be(title);
        });
    });

    describe('getTtl', function() {
        it('should return INFINITE if ttl is null', function() {
            expect(this.scope.getTtl()).to.be(Scope.TTL_INFINITE);
        });

        it('should return ttl if it is defined', function() {
            this.scopeDefinition.ttl = 123;
            var scope = new Scope(this.scopeId, this.scopeDefinition);

            expect(scope.getTtl()).to.be(this.scopeDefinition.ttl);
        });
    });

    describe('isSame', function() {
        it('should throw if the argument is not a scope', function() {
            var scope = this.scope;

            expect(function() {
                scope.isSame('definitely not a scope');
            }).to.throwError(function(err) {
                expect(err.message).to.be('Scope should be a Scope Model');
            });
        });

        it('should return true if compared to the scope itself', function() {
            expect(this.scope.isSame(this.scope)).to.be(true);
        });

        it('should return true if compared to a scope with same id', function() {
            var scope = new Scope(this.scopeId, this.scopeDefinition);

            expect(this.scope.isSame(scope)).to.be(true);
        });

        it('should return false if compared scope has different id', function() {
            var scope = new Scope('Think different', this.scopeDefinition);

            expect(this.scope.isSame(scope)).to.be(false);
        });
    });
});
