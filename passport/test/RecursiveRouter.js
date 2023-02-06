var expect = require('expect.js');
var sinon = require('sinon');

var RecursiveRouter = require('../RecursiveRouter');

describe('Recursive Router', function() {
    beforeEach(function() {
        this.router = new RecursiveRouter();
        this.router._match = sinon.stub().returns(new RecursiveRouter.Match());

        this.url =
            'http://passport.yandex.ru/registration/mail/digit?from=mail' +
            '&origin=whatsoever&firstname=vasya&lastname=pupkine';
        this.method = 'GET';
    });
    describe('match', function() {
        it('should throw if url is not a string', function() {
            var router = this.router;
            var method = this.method;

            expect(function() {
                router.match({}, method);
            }).to.throwError(function(e) {
                expect(e.message).to.be('Url should be a string');
            });
        });

        it('should throw if method is not a string, when it is provided', function() {
            var url = this.url;
            var router = this.router;

            expect(function() {
                router.match(url, {});
            }).to.throwError(function(e) {
                expect(e.message).to.be('Method is optional, but should be a string if provided');
            });
        });

        it('should not throw if method is not provided', function() {
            this.router.match(this.url);
        });

        it('should call _match', function() {
            this.router.match(this.url, this.method);
            expect(this.router._match.calledOnce).to.be(true);
            expect(this.router._match.calledWithExactly(this.url, this.method)).to.be(true);
        });

        it('should return the value from _match, if it is not an instance of RecursiveController', function() {
            var result = {whatso: 'ever'};

            this.router._match.returns(new RecursiveRouter.Match(result));
            expect(this.router.match(this.url, this.method)).to.be(result);
        });

        it('should call the result of a match, if it is another RecursiveController', function() {
            var matchedRouter = new RecursiveRouter();

            sinon.stub(matchedRouter, 'match');
            this.router._match.returns(new RecursiveRouter.Match(matchedRouter));

            this.router.match(this.url, this.method);
            expect(matchedRouter.match.calledOnce).to.be(true);
        });

        it(
            'should pass the original url and a matched url to transformUrl, ' + 'if match is another RecoursiveRouter',
            function() {
                var matchedUrl = '/whatso/ever';
                var matchedRouter = new RecursiveRouter();

                sinon.stub(matchedRouter, 'match');

                var match = new RecursiveRouter.Match(matchedRouter, matchedUrl);

                this.router._match.returns(match);

                sinon.stub(this.router, 'transformUrl').returns(match);

                this.router.match(this.url, this.method);
                expect(this.router.transformUrl.calledOnce).to.be(true);
                expect(this.router.transformUrl.calledWithExactly(this.url, matchedUrl)).to.be(true);
            }
        );

        it(
            'should call the result of a match with a result of transformUrl, ' +
                'if it is another RecursiveController',
            function() {
                var matchedRouter = new RecursiveRouter();

                sinon.stub(matchedRouter, 'match');
                this.router._match.returns(new RecursiveRouter.Match(matchedRouter));

                var transformed = {trans: 'formed'};

                sinon.stub(this.router, 'transformUrl').returns(transformed);

                this.router.match(this.url, this.method);
                expect(matchedRouter.match.calledWith(transformed)).to.be(true);
            }
        );

        it('should return the result of a call to the match, if it is another RecursiveController', function() {
            var expectedResult = {whatso: 'ever'};
            var intermediary = new RecursiveRouter();

            sinon.stub(intermediary, 'match').returns(expectedResult);
            this.router._match.returns(new RecursiveRouter.Match(intermediary));

            expect(this.router.match(this.url, this.method)).to.be(expectedResult);
        });
    });
});
