var expect = require('expect.js');
var cipher = require('../libs/xor_cipher');

describe('Xor cipher', function() {
    var messageAscii = 'Lorem ipsum';
    var messageUnicode = 'Лорем ипсуп';
    var secretAscii = 'foobar';
    var secretUnicode = 'фубар';
    var b64Table = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=';

    describe('encode', function() {
        it('Should return a base64 string', function() {
            var encMessage = cipher.encode(secretAscii, messageAscii);

            expect(encMessage).to.be.a('string');
            encMessage.split('').forEach(function(c) {
                expect(b64Table.indexOf(c)).to.be.greaterThan(-1);
            });
        });

        it("Should throw if secret or data isn't an ascii string", function() {
            expect(cipher.encode)
                .withArgs(secretUnicode, messageAscii)
                .to.throwException();
            expect(cipher.encode)
                .withArgs(secretAscii, messageUnicode)
                .to.throwException();
            expect(cipher.encode)
                .withArgs(secretAscii, true)
                .to.throwException();
            expect(cipher.encode)
                .withArgs(secretAscii, 123456789)
                .to.throwException();
            expect(cipher.encode)
                .withArgs(true, messageAscii)
                .to.throwException();
            expect(cipher.encode)
                .withArgs(123456789, messageAscii)
                .to.throwException();
        });
    });

    describe('decode', function() {
        it('Should return original string', function() {
            var encMessage = cipher.encode(secretAscii, messageAscii);

            expect(cipher.decode(secretAscii, encMessage)).to.be.equal(messageAscii);
        });

        it("Should throw if secret or data isn't an ascii string", function() {
            expect(cipher.decode)
                .withArgs(secretUnicode, messageAscii)
                .to.throwException();
            expect(cipher.decode)
                .withArgs(secretAscii, messageUnicode)
                .to.throwException();
            expect(cipher.decode)
                .withArgs(secretAscii, true)
                .to.throwException();
            expect(cipher.decode)
                .withArgs(secretAscii, 123456789)
                .to.throwException();
            expect(cipher.decode)
                .withArgs(true, messageAscii)
                .to.throwException();
            expect(cipher.decode)
                .withArgs(123456789, messageAscii)
                .to.throwException();
        });
    });
});
