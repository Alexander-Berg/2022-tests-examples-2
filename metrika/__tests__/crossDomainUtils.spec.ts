/* eslint-env mocha */
import * as chai from 'chai';
import * as sinon from 'sinon';
import * as browser from '@src/utils/browser';
import { CounterOptions } from '@src/utils/counterOptions';
import { BrowserInfo } from '@src/utils/browserInfo';
import { LocalStorage } from '@src/storage/localStorage';
import { GlobalStorage } from '@src/storage/global';
import * as cdUtils from '../utils';

describe('crossDomain utils', () => {
    const fakeWindow = {} as any as Window;
    const sandbox = sinon.createSandbox();
    let isIOS: any;
    let isSafariWebView: any;
    let isFF: any;
    let getAgent: any;
    let isITP: any;

    beforeEach(() => {
        isIOS = sandbox.stub(browser, 'isIOS');
        sandbox.stub(browser, 'isSafari');
        isSafariWebView = sandbox.stub(browser, 'isSafariWebView');
        isFF = sandbox.stub(browser, 'isFF');
        getAgent = sandbox.stub(browser, 'getAgent');
        isITP = sandbox.stub(browser, 'isITP');
    });

    afterEach(() => {
        sandbox.restore();
    });

    it('getITPYaBroVersion', () => {
        getAgent.returns('It is Yptp/1.52 ');
        chai.expect(
            cdUtils.getITPYaBroVersion({} as any as Window),
            'should parse version from fake user agent',
        ).to.be.equal(52);
        getAgent.returns('It is not valid Yptp browser');
        chai.expect(
            cdUtils.getITPYaBroVersion({} as any as Window),
            'should return 0 for non Yptp',
        ).to.be.equal(0);
    });

    it('isFFVersion', () => {
        isFF.returns(false);
        getAgent.returns('Something');
        chai.expect(
            cdUtils.isFFVersion({} as any as Window, 10),
            'false for something that not looks like Firefox',
        ).to.be.false;
        isFF.returns(true);
        getAgent.returns('Firefox/10');
        chai.expect(
            cdUtils.isFFVersion({} as any as Window, 10),
            'true if Firefox and version >= requested one',
        ).to.be.true;
        getAgent.returns('Firefox/99');
        chai.expect(
            cdUtils.isFFVersion({} as any as Window, 100),
            'false if Firefox and version < requested one',
        ).to.be.false;
    });

    it('checkVersion', () => {
        getAgent.returns('Random agent ');
        isSafariWebView.returns(false);
        isITP.returns(false);
        chai.expect(
            cdUtils.isITPDisabled({} as any as Window),
            'true for a random browser in random OS',
        ).to.be.true;

        getAgent.returns('It is Yptp/1.52 ');
        isSafariWebView.returns(false);
        isITP.returns(false);

        chai.expect(
            cdUtils.isITPDisabled({} as any as Window),
            'false for Yptp >= 50 && <= 99 at random OS',
        ).to.be.false;

        getAgent.returns('Something random');
        isSafariWebView.returns(true);
        isITP.returns(false);
        isIOS.returns(true);

        chai.expect(
            cdUtils.isITPDisabled({} as any as Window),
            'true for anything inside isSafariWebView at random OS',
        ).to.be.true;

        getAgent.returns('Something random');
        isSafariWebView.returns(false);
        isITP.returns(true);

        chai.expect(
            cdUtils.isITPDisabled({} as any as Window),
            'false for ITP Safari',
        ).to.be.false;

        getAgent.returns(
            'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36 Edg/83.0.478.37',
        );
        chai.expect(
            cdUtils.isITPDisabled({} as any as Window),
            'false for edge >= 79',
        ).to.be.false;
    });

    it('getVal without brInfo', () => {
        const counterOptions: CounterOptions = { id: 1, counterType: '0' };
        const storage = {
            getVal: sinon.stub(),
            setVal: sinon.stub(),
        };
        const localStorage = {
            getVal: sinon.stub(),
            setVal: sinon.stub(),
        };
        const init = sinon.stub();

        storage.getVal.returns('Something');
        chai.expect(
            cdUtils.getVal(
                fakeWindow,
                counterOptions,
                storage as any,
                localStorage as any,
                init,
                'valName',
                'default',
            ),
            'should return value from storage.getVal if var is set',
        ).to.be.equal('Something');
        sinon.assert.notCalled(init);
        sinon.assert.notCalled(storage.setVal);

        storage.setVal.resetHistory();
        init.resetHistory();

        storage.getVal.callsFake((_, defVal) => {
            return defVal;
        });
        chai.expect(
            cdUtils.getVal(
                fakeWindow,
                counterOptions,
                storage as any,
                localStorage as any,
                init,
                'valName',
                'default',
            ),
            'should return default if val is undefined',
        ).to.be.equal('default');
        sinon.assert.called(init);
        chai.expect(
            storage.setVal.called,
            'should call storage.setVal function if var is undefined',
        ).to.be.true;
    });
    it('getVal with brInfo', () => {
        const counterOptions: CounterOptions = { id: 1, counterType: '0' };
        const storage = {
            getVal: sinon.stub(),
            setVal: sinon.stub(),
        };
        const localStorage = {
            getVal: sinon.stub(),
            setVal: sinon.stub(),
        };
        const init = sinon.stub();
        const brInfo = {
            setOrNot: sinon.stub(),
        };
        storage.getVal.returns('Something');
        chai.expect(
            cdUtils.getVal(
                fakeWindow,
                counterOptions,
                storage as any,
                localStorage as any,
                init,
                'valName',
                'default',
                brInfo as unknown as BrowserInfo,
            ),
            'should return save value to browserInfo',
        ).to.be.equal('Something');
        chai.expect(
            brInfo.setOrNot.getCall(0).args,
            'should call brInfo.setVal',
        ).to.be.deep.eq(['valName', 'Something']);

        brInfo.setOrNot.resetHistory();
        init.resetHistory();

        storage.getVal.callsFake((_, defVal) => {
            return defVal;
        });
        chai.expect(
            cdUtils.getVal(
                fakeWindow,
                counterOptions,
                storage as unknown as GlobalStorage,
                localStorage as unknown as LocalStorage,
                init,
                'valName',
                'default',
                brInfo as unknown as BrowserInfo,
            ),
            'should store default value if val is undefined',
        ).to.be.equal('default');
        chai.expect(
            brInfo.setOrNot.getCall(0).args,
            'should call brInfo.setVal',
        ).to.be.deep.eq(['valName', 'default']);
    });
});
