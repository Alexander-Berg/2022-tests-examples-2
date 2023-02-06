var expect = require('expect.js');
var sinon = require('sinon');

var Collection = require('../../../OAuth/models/ScopesCollection');
var Scope = require('../../../OAuth/models/Scope');

describe('Scopes collection', function() {
    beforeEach(function() {
        this.scope1 = new Scope('one', {
            title: 'Scope One',
            requires_approval: false,
            ttl: null,
            is_ttl_refreshable: false
        });
        this.scope2 = new Scope('two', {
            title: 'Scope Two',
            requires_approval: false,
            ttl: null,
            is_ttl_refreshable: false
        });

        this.collection = new Collection(this.scope1, this.scope2);
    });

    describe('Constructor', function() {
        it('should throw if any argument is not a scope (or an array of scopes)', function() {
            expect(function() {
                new Collection('nope');
            }).to.throwError(function(err) {
                expect(err.message).to.be('Scope should be a Scope Model');
            });
        });
    });

    describe('length', function() {
        it('should be 0 for an empty collection', function() {
            expect(new Collection().length).to.be(0);
        });

        it('should return the number of scopes in a collection', function() {
            expect(this.collection.length).to.be(2);
        });
    });

    describe('contains', function() {
        it('should return true if collection contains the given scope', function() {
            expect(this.collection.contains(this.scope1)).to.be(true);
        });

        it('should return true if collection contains the scope of the same id', function() {
            var scope = new Scope('one', {
                title: 'Nobody cares for this title',
                requires_approval: false,
                ttl: null,
                is_ttl_refreshable: false
            });

            expect(this.collection.contains(scope)).to.be(true);
        });

        it('should return false if collection does not contains the scope', function() {
            var scope = new Scope('three', {
                title: 'Nobody cares for this title either',
                requires_approval: false,
                ttl: null,
                is_ttl_refreshable: false
            });

            expect(this.collection.contains(scope)).to.be(false);
        });
    });

    describe('getTtl', function() {
        it('should return NOT_DEFINED if there are no scopes in this collection', function() {
            expect(new Collection().getTtl()).to.be(Scope.TTL_NOT_DEFINED);
        });

        it('should return INFINITE if every scope in the collection has infinite ttl', function() {
            sinon.stub(this.scope1, 'isTtlInfinite').returns(true);
            sinon.stub(this.scope2, 'isTtlInfinite').returns(true);

            expect(this.collection.getTtl()).to.be(Scope.TTL_INFINITE);
        });

        it('should return a numeric ttl if any scope has non-infinite one', function() {
            var numericTTL = 13213;

            sinon.stub(this.scope1, 'getTtl').returns(Scope.TTL_INFINITE);
            sinon.stub(this.scope2, 'getTtl').returns(numericTTL);

            expect(this.collection.getTtl()).to.be(numericTTL);
        });

        it('should return lowest ttl among the non-infinite scopes', function() {
            var lowest = Math.ceil(Math.PI * Math.E);

            sinon.stub(this.scope1, 'getTtl').returns(lowest);
            sinon.stub(this.scope2, 'getTtl').returns(42);

            expect(this.collection.getTtl()).to.be(lowest);
        });

        it('should return INFINITE if all the scopes have (somehow) infinite ttls', function() {
            sinon.stub(this.scope1, 'getTtl').returns(Infinity);
            sinon.stub(this.scope2, 'getTtl').returns(Infinity);

            expect(this.collection.getTtl()).to.be(Scope.TTL_INFINITE);
        });
    });

    describe('isTtlRefreshable', function() {
        it('should return false for an empty collection', function() {
            expect(new Collection().isTtlRefreshable()).to.be(false);
        });

        it('should return false if collection ttl is infinite', function() {
            sinon.stub(this.collection, 'getTtl').returns(Scope.TTL_INFINITE);
            expect(this.collection.isTtlRefreshable()).to.be(false);
        });

        it('should return true if every scope has a refreshable ttl', function() {
            sinon.stub(this.collection, 'getTtl').returns(555);
            sinon.stub(this.scope1, 'isTtlRefreshable').returns(true);
            sinon.stub(this.scope2, 'isTtlRefreshable').returns(true);
            expect(this.collection.isTtlRefreshable()).to.be(true);
        });

        it('should return false if any scope has a non-refreshable ttl', function() {
            sinon.stub(this.collection, 'getTtl').returns(666);
            sinon.stub(this.scope1, 'isTtlRefreshable').returns(true);
            sinon.stub(this.scope2, 'isTtlRefreshable').returns(false);
            expect(this.collection.isTtlRefreshable()).to.be(false);
        });
    });
});
