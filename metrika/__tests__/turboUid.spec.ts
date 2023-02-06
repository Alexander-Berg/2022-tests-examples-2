import * as chai from 'chai';
import * as store from '@src/storage/cookie';
import * as loc from '@src/utils/location';
import * as sinon from 'sinon';
import { CounterOptions } from '@src/utils/counterOptions';
import { getTurboUid, COOKIE_NAME } from '../turboUid';

describe('turboUid', () => {
    const sandbox = sinon.createSandbox();
    const getWin = () => ({} as any as Window);
    const getOpt = () =>
        ({
            noCookie: false,
            id: 1,
            counterType: '0',
        } as CounterOptions);
    let win: Window;
    let locationStub: sinon.SinonStub<any, any>;
    let cookieStub: sinon.SinonStub<any, any>;
    beforeEach(() => {
        win = getWin();
        locationStub = sandbox.stub(loc, 'getLocation');
        cookieStub = sandbox.stub(store, 'globalCookieStorage');
    });
    afterEach(() => {
        sandbox.restore();
    });
    it('doesnt set cookie if it desabled', () => {
        const opt = getOpt();
        opt.noCookie = true;
        const testUid = '1test';
        locationStub.withArgs(win).returns({
            search: `asdf&turbo_uid=${testUid}&12`,
        });
        const getValStub = sinon.stub();
        const setValStub = sinon.stub().named('setVal');
        cookieStub.withArgs(win).returns({
            getVal: getValStub.returns(''),
            setVal: setValStub,
        });
        const result = getTurboUid(win, opt);
        chai.expect(result).to.be.eq(testUid);
        sinon.assert.notCalled(setValStub);
    });
    it('returns empty string if there are no location and cookie info', () => {
        locationStub.withArgs(win).returns({
            search: '',
        });
        const getValStub = sinon.stub();
        cookieStub.withArgs(win).returns({
            getVal: getValStub.returns(''),
        });
        const result = getTurboUid(win, getOpt());
        chai.expect(result).to.be.eq('');
    });
    it('get uid from url', () => {
        const testUid = '1test';
        locationStub.withArgs(win).returns({
            search: `asdf&turbo_uid=${testUid}&12`,
        });
        const getValStub = sinon.stub();
        const setValStub = sinon.stub().named('setVal');
        cookieStub.withArgs(win).returns({
            getVal: getValStub.returns(''),
            setVal: setValStub,
        });
        const result = getTurboUid(win, getOpt());
        chai.expect(result).to.be.eq(testUid);
        sinon.assert.calledWith(setValStub, COOKIE_NAME, testUid);
    });
    it('get uid from cookie', () => {
        const testUid = '1test';
        locationStub.withArgs(win).returns({
            search: ``,
        });
        const getValStub = sinon.stub();
        cookieStub.withArgs(win).returns({
            getVal: getValStub.returns(testUid),
        });
        const result = getTurboUid(win, getOpt());
        chai.expect(result).to.be.eq(testUid);
        sinon.assert.calledWith(getValStub, COOKIE_NAME);
    });
});
