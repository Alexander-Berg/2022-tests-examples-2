import {setWid, getOrigin} from '../src/utils';
import {expect} from 'chai';

describe('utils', function () {
    function testMiddleware(func, req, res) {
        return new Promise((resolve, reject) => {
            func(req, res, e => {
                if (e) {
                    reject(e);
                } else {
                    resolve();
                }
            });
        });
    }
    describe('setWid', () => {
        it('парсит строку wauth', async () => {
            const req = {
                query: {
                    wauth: '1..6903IZ.576-1.1596489730144518.2766269.2766269..27792493.1406.70d0a0d3ecc4b1a269341b9dbe82b54c'
                },
                wid: undefined
            };
            await testMiddleware(setWid, req, {});
            expect(req.wid).to.equal('576');
        });

        it('устанавливает 000 при проблеме', async () => {
            const req = {
                query: {
                    wauth: '1..6903IZ.2766269.2766269..27792493.1406.70d0a0d3ecc4b1a269341b9dbe82b54c'
                },
                wid: undefined
            };
            await testMiddleware(setWid, req, {});
            expect(req.wid).to.equal('000');
        });

        it('устанавливает 000 при отсутствии wauth', async () => {
            const req = {
                query: {},
                wid: undefined
            };
            await testMiddleware(setWid, req, {});
            expect(req.wid).to.equal('000');
        });
    });

    describe('getOrigin', () => {
        it('обычные урлы', () => {
            expect(getOrigin('https://some.site')).to.equal('https://some.site');
            expect(getOrigin('https://some.site/')).to.equal('https://some.site');
            expect(getOrigin('http://some.site')).to.equal('http://some.site');
            expect(getOrigin('http://some.site:4444')).to.equal('http://some.site:4444');
            expect(getOrigin('http://some.site/he/he?arg=45#hash=/qq')).to.equal('http://some.site');
        });
        it('урлы без схемы', () => {
            expect(getOrigin('//some.site#https://evil.com')).to.equal('http://some.site');
            expect(getOrigin('//some.site/he/he?arg=45#hash=/qq')).to.equal('http://some.site');
        });
        it('не урлы', () => {
            expect(getOrigin('')).to.equal('');
            expect(getOrigin()).to.equal('');
        });
        it('урлы без хоста', () => {
            expect(getOrigin('/he/he?arg=qwe#https://evil.com')).to.equal('');
        });
    });
});
