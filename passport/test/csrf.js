var expect = require('expect.js');

var csrf = require('../libs/csrf');

describe('csrf', function() {
    beforeEach(function() {
        this.uid = '123123123';
        this.yandexuid = '890972394898734234';
    });

    it('should throw if the salt is not defined', function() {
        var that = this;

        expect(function() {
            csrf(that.uid, that.yandexuid);
        }).to.throwError(function(e) {
            expect(e.message).to.be('Salt should be defined with csrf.setSalt()');
        });
    });

    it('should generate different hashes with different salts', function() {
        csrf.setSalt('one');
        var one = csrf(this.uid, this.yandexuid);

        csrf.setSalt('two');
        var two = csrf(this.uid, this.yandexuid);

        expect(one).to.not.eql(two);
    });

    describe('setSalt', function() {
        it('should throw if salt is not a string', function() {
            expect(function() {
                csrf.setSalt(['n', 'o', 'p', 'e']);
            }).to.throwError(function(err) {
                expect(err.message).to.be('Salt should be a string');
            });
        });
    });
});
