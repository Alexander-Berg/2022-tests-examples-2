import * as chai from 'chai';
import { decodeUtf8, decodeBase64, encodeUtf8, encodeBase64 } from '../decoder';

describe('decoder / utils', () => {
    it('utf8 decode null character', () => {
        const encoded = '\0';
        const decoded = '\u0000';
        chai.expect(decodeUtf8(encoded)).to.be.equal(decoded);
    });

    it('utf8 decode  charcode', () => {
        const encoded = '\xC2\x80';
        const decoded = '\u0080';
        chai.expect(decodeUtf8(encoded)).to.be.equal(decoded);
    });

    it('utf8 decode charcodes', () => {
        const encoded = '\xF4\x8F\xBF\xBF';
        const decoded = '\u43FF\uF000';
        chai.expect(decodeUtf8(encoded)).to.be.equal(decoded);
    });

    it('base64: decode not full string', () => {
        const encoded = 'YR';
        const decoded = 'a';
        chai.expect(decodeBase64(encoded)).to.be.equal(decoded);
    });

    it('base64: decode full string', () => {
        const encoded = 'YQ==';
        const decoded = 'a';
        chai.expect(decodeBase64(encoded)).to.be.equal(decoded);
    });

    it('base64: decode long string', () => {
        const encoded = 'Zm9vIGJhciBiYXo=';
        const decoded = 'foo bar baz';
        chai.expect(decodeBase64(encoded)).to.be.equal(decoded);
    });

    it('base64: decode wrong string, return empty string', () => {
        const encoded = 'ab\\tcd';
        const decoded = '';
        chai.expect(decodeBase64(encoded)).to.be.equal(decoded);
    });

    it('decode urlsafe', () => {
        const encoded =
            'bWFya2V0LnlhbmRleC5ydTvQn9C70LDRgtGM0LUg0KHRg9C70YLQsNC90L3QsCDQpNGA0LDQvdGG0YPQt9C-0LLQsCDRgdCy0L7QsdC-0LTQvdC-0LUg0YEg0LrQsNGA0LzQsNC90LDQvNC4O3pfOU9OcjFyaEltWjZYdktpZXB5S0E7';
        const decoded =
            'market.yandex.ru;Платье Султанна Французпва свобпднпе с карманами;z_9ONr1rhImZ6XvKiepyKA;';
        chai.expect(decodeUtf8(decodeBase64(encoded, true) || '')).to.be.equal(
            decoded,
        );
    });

    it('utf8: encode empty', () => {
        const decoded = '';
        chai.expect(encodeUtf8(decoded)).to.be.empty;
    });

    it('utf8: encode', () => {
        const decoded = `safari п${String.fromCharCode(2048)}`;
        const encoded = [
            0x73, 0x61, 0x66, 0x61, 0x72, 0x69, 0x20, 0xd0, 0xbf, 0xe0, 0xa0,
            0x80,
        ];
        chai.expect(encodeUtf8(decoded)).to.deep.equal(encoded);
    });

    it('base64: encode full string', () => {
        const decoded = [0x73, 0x61, 0x66, 0x61, 0x72, 0x69];
        const encoded = 'c2FmYXJp';
        chai.expect(encodeBase64(decoded)).to.equal(encoded);
    });

    it('base64: encode full string', () => {
        const decoded = [0x63, 0x68, 0x72, 0x6f, 0x6d, 0x65];
        const encoded = 'Y2hyb21l';
        chai.expect(encodeBase64(decoded)).to.equal(encoded);
    });

    it('base64: encode byte code to base64 string (with safe flag)', () => {
        const initialString = 'Hello World';
        // В этом байт-коде зашифровано "Hello World"
        const decoded = [72, 101, 108, 108, 111, 32, 87, 111, 114, 108, 100];
        const encodedSafe = 'SGVsbG8gV29ybGQ_';
        chai.expect(encodeBase64(decoded, true)).to.equal(encodedSafe);
        chai.expect(decodeBase64(encodedSafe, true)).to.equal(initialString);
    });

    it('base64: encode and then decode full string (with safe flag)', () => {
        const initialString = 'Hello World';
        const encoded = encodeBase64(encodeUtf8(initialString), true);
        const decoded = decodeBase64(encoded, true);
        chai.expect(initialString).to.equal(decoded);
    });
});
