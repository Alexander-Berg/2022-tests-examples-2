var expect = require('expect.js');
var sinon = require('sinon');

var MappingRouter = require('../Mapping');

describe('Mapping Router', function() {
    beforeEach(function() {
        this.url = 'http://yandex.ru/1/2/3';
        this.router = new MappingRouter();
    });

    describe('map', function() {
        it('should throw if the url is not a string', function() {
            var router = this.router;

            expect(function() {
                router.map({}, 'value');
            }).to.throwError(function(e) {
                expect(e.message).to.be('Url should be a string or a regexp');
            });
        });

        it('should throw if mapped value is undefined', function() {
            var router = this.router;

            expect(function() {
                router.map('/url');
            }).to.throwError(function(e) {
                expect(e.message).to.be('Mapped value should be defined. Perhaps use default?');
            });
        });

        it('should define an object that is mapped to a part of the url', function() {
            var mapped = {definitely: 'mapped'};

            this.router.map('/mapped', mapped);

            expect(this.router.match('/mapped')).to.be(mapped);
        });

        it('should throw if anything is already mapped to the given url', function() {
            var router = this.router;

            router.map('/throw', true);

            expect(function() {
                router.map('/throw', 'nope');
            }).to.throwError(function(e) {
                expect(e.message).to.be('Value already mapped to the given key');
            });
        });

        it('should return the router itself for chaining', function() {
            expect(this.router.map('a', 'b')).to.be(this.router);
        });
    });

    describe('default', function() {
        it('should define an object that is returned when nothing is mapped to the given url', function() {
            var defaultResult = {de: 'fault'};

            this.router.default(defaultResult);

            expect(this.router.match('/unknown')).to.be(defaultResult);
        });

        it('should throw if anything is already defined as default', function() {
            var router = this.router;

            router.default('/donotthrow');

            expect(function() {
                router.default('/throw');
            }).to.throwError(function(e) {
                expect(e.message).to.be('Value already defined as a default');
            });
        });

        it('should throw if value is undefined', function() {
            var router = this.router;

            expect(function() {
                router.default();
            }).to.throwError(function(e) {
                expect(e.message).to.be('Value should be defined');
            });
        });

        it('should return the router itself for chaining', function() {
            expect(this.router.default('a')).to.be(this.router);
        });
    });

    describe('transformUrl', function() {
        it('should cur the matched path from the url', function() {
            expect(this.router.transformUrl('/matched/freaking/long/url', '/matched/freaking')).to.be('/long/url');
        });

        it('should return the same url if cuttin a signle slash', function() {
            expect(this.router.transformUrl('/a', '/')).to.be('/a');
        });

        it('should return a single slash if there is nothing left from the url', function() {
            expect(this.router.transformUrl('/a', '/a')).to.be('/');
        });

        it('should support cutting a path from a full url', function() {
            expect(this.router.transformUrl('http://yandex.ru/a/b/c', '/a/b')).to.be('/c');
        });

        it('should only cut at the beginning of the url', function() {
            expect(this.router.transformUrl('/a/b/a', '/a')).to.be('/b/a');
        });
    });

    describe('match', function() {
        it('should throw if no default is defined and an unknown url is given', function() {
            var router = this.router;

            expect(function() {
                router.match('/unknown');
            }).to.throwError(function(e) {
                expect(e).to.be.an(URIError);
                expect(e.message).to.be('Unknown url given with no default defined');
            });
        });

        it('should return a mapped url instead of default', function() {
            var expectedResult = {expected: 'result'};

            this.router.map('/value', expectedResult);
            this.router.default('nope');
            expect(this.router.match('/value')).to.be(expectedResult);
        });

        it('should tolerate trailing slashes', function() {
            var expectedResult = {expected: 'result'};

            this.router.map('/value', expectedResult);
            expect(this.router.match('/value/')).to.be(expectedResult);
        });

        it('should match the url with get params using pathname', function() {
            this.router.map('/route', 'yep');
            expect(this.router.match('/route?get=param')).to.be('yep');
        });

        it('should match the url ending in slash with get params using pathname', function() {
            this.router.map('/route', 'yep');
            expect(this.router.match('/route/?get=param')).to.be('yep');
        });

        it('should support complex definitions', function() {
            var secondLevelRouter = new MappingRouter();

            secondLevelRouter.map('/b/c', 'one');
            secondLevelRouter.map('/b/d', 'two');
            secondLevelRouter.default('sldefault');

            this.router.map('/a', secondLevelRouter);
            this.router.map('/b', 'firstlevelb');
            this.router.default('fldefault');

            expect(this.router.match('/a/b/c')).to.be('one');
            expect(this.router.match('/a/b/d')).to.be('two');
            expect(this.router.match('/a/unknown')).to.be('sldefault');
            expect(this.router.match('/a')).to.be('sldefault');

            expect(this.router.match('/b')).to.be('firstlevelb');
            expect(this.router.match('/safasdfsdf')).to.be('fldefault');
        });

        it('should return a value mapped to the regexp if url matches', function() {
            this.router.map(/\/whatso.{4}/, 'hey-hey!');
            expect(this.router.match('/whatsoever')).to.be('hey-hey!');
        });

        it('should call nested router with the url sans the matched part', function() {
            var nestedRouter = new MappingRouter();

            sinon.stub(nestedRouter, 'match');

            this.router.map('/whatso/ever', nestedRouter);
            this.router.match('/whatso/ever/whatever/whenever');

            expect(nestedRouter.match.calledOnce).to.be(true);
            expect(nestedRouter.match.calledWith('/whatever/whenever')).to.be(true);
        });

        describe('strict', function() {
            it('should return a default when there is no exact match', function() {
                this.router.map('/a', 'one');
                this.router.default('two');

                expect(this.router.match('/a/b')).to.be('two');
            });

            it('should return a deafult value when an unknown url is given', function() {
                this.router.map('/', 'one');
                this.router.default('two');

                expect(this.router.match('/unknown')).to.be('two');
            });
        });

        describe('lax', function() {
            beforeEach(function() {
                this.router.setLax();
            });

            it('should search for longest possible match', function() {
                this.router.map('/a/b/c', 'one');
                this.router.map('/a', 'two');

                expect(this.router.match('/a/b/c/d')).to.be('one');
            });

            it('should return value mapped to the root when an unknown url is given', function() {
                this.router.map('/', 'one');
                this.router.default('two');

                expect(this.router.match('/unknown')).to.be('one');
            });
        });
    });
});
