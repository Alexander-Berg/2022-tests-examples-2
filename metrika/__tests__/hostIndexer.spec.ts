import { expect } from 'chai';
import * as sinon from 'sinon';
import * as cookieModule from '@src/storage/cookie';
import * as config from '@src/config';
import * as tldModule from '@src/providers/searchTLD';
import {
    COOKIE_NAME,
    COOKIE_TIME,
    getHostIndexer,
    getUrls,
    onSuccess,
    readHostStatus,
    writeHostStatus,
} from '../hostIndexer';

describe('hostIndexer', () => {
    const sandbox = sinon.createSandbox();
    const getCookieStub = sandbox.stub();
    const setCookieStub = sandbox.stub();
    const cookie = {
        getVal: getCookieStub,
        setVal: setCookieStub,
    } as any;
    let configStub: sinon.SinonStub<any, any>;
    let baseDomainStub: sinon.SinonStub<any, any>;
    let hostStub: sinon.SinonStub<any, any>;
    let cookieStub: sinon.SinonStub<any, any>;
    let tldStub: sinon.SinonStub<any, any>;
    const testPtotocol = 'proto:';
    const testDomain = 'testDomain';
    const testTld = 'test';
    const testHost = `${testDomain}.${testTld}`;

    beforeEach(() => {
        baseDomainStub = sandbox.stub(config, 'BASE_DOMAIN');
        baseDomainStub.value(testDomain);
        hostStub = sandbox.stub(config, 'host');
        hostStub.value(testHost);
        tldStub = sandbox.stub(tldModule, 'getDomainAndTLD');
        configStub = sandbox.stub(config, 'config');
        configStub.value({
            cProtocol: testPtotocol,
        });
        cookieStub = sandbox.stub(cookieModule, 'globalCookieStorage');
    });
    afterEach(() => {
        setCookieStub.reset();
        getCookieStub.reset();
        sandbox.restore();
    });
    it('reads host state from cookie if it empty', () => {
        getCookieStub.returns(null);
        const result = readHostStatus(cookie, ['a', 'b']);
        sinon.assert.calledWith(getCookieStub, COOKIE_NAME);
        expect(result).to.be.deep.eq([0, 0]);
    });
    it('reads host state from cookie if it exist', () => {
        getCookieStub.returns('a-2,b-4');
        const result = readHostStatus(cookie, ['a', 'b']);
        sinon.assert.calledWith(getCookieStub, COOKIE_NAME);
        expect(result).to.be.deep.eq([2, 4]);
    });
    it('write host state to cooke', () => {
        writeHostStatus([3, 9], { cookie } as any);
        sinon.assert.calledWith(
            setCookieStub,
            COOKIE_NAME,
            '0-3,1-9',
            COOKIE_TIME,
        );
    });
    it('provide full urls list when empty state', () => {
        const resourse = 'test';
        const result = getUrls(resourse)({
            cookie,
            HOST_LIST: ['a', 'b'],
            hostStatus: [0, 0],
            currentIndex: 0,
        } as any);
        expect(result).to.be.deep.eq([
            `${testPtotocol}//a/${resourse}`,
            `${testPtotocol}//b/${resourse}`,
        ]);
    });
    it('provide full urls list when state exist', () => {
        const resourse = 'test';
        const state = {
            cookie,
            HOST_LIST: ['a', 'b'],
            hostStatus: [0, 2],
            currentIndex: 0,
        };
        const result = getUrls(resourse)(state as any);
        expect(result).to.be.deep.eq([
            `${testPtotocol}//b/${resourse}`,
            `${testPtotocol}//a/${resourse}`,
        ]);
        expect(state.currentIndex).to.be.eq(1);
    });
    it('doesnt save change if current doman is succeed', () => {
        const state = {
            cookie,
            HOST_LIST: ['a', 'b'],
            hostStatus: [0, 2],
            currentIndex: 0,
        };
        onSuccess(1)(state);
        sinon.assert.notCalled(setCookieStub);
        expect(state.currentIndex).to.be.eq(1);
    });
    it('save change if not current doman is succeed', () => {
        getCookieStub.returns('0-0,1-1');
        const state = {
            cookie,
            HOST_LIST: ['a', 'b'],
            hostStatus: [0, 1],
            currentIndex: 0,
        };
        onSuccess(1)(state);
        sinon.assert.calledWith(
            setCookieStub,
            COOKIE_NAME,
            '0-0,1-2',
            COOKIE_TIME,
        );
        expect(state.currentIndex).to.be.eq(0);
    });
    it('creates single state for all calls', () => {
        cookieStub.returns(cookie);
        tldStub.returns('b');
        const win = {} as any;
        const indexerC = getHostIndexer(win);
        const indexerC2 = getHostIndexer(win);
        const indexer = indexerC((a: any) => a);
        const indexer2 = indexerC2((a: any) => a);
        expect(indexer).to.be.eq(indexer2);
        expect(indexer.HOST_LIST).to.include('b');
    });
});
