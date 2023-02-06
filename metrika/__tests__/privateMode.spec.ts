import * as chai from 'chai';
import * as sinon from 'sinon';
import * as browser from '@src/utils/browser';
import * as privateMode from '../private';

const { isPrivate, QUOTA_LIMIT } = privateMode;

describe('private mode provider', () => {
    const state = {
        pri: undefined as any,
    };
    const detectPrivateMode = privateMode.isPrivateMode;

    let getBrowserStateStub: any;
    let isAndroidWebViewStub: any;
    let isPrivateStub: any;

    beforeEach(() => {
        state.pri = undefined;
        getBrowserStateStub = sinon
            .stub(privateMode, 'getState')
            .returns(state);
        isAndroidWebViewStub = sinon
            .stub(browser, 'isAndroidWebView')
            .returns(false);
        isPrivateStub = sinon.stub(privateMode, 'isPrivate');
    });
    afterEach(() => {
        getBrowserStateStub.restore();
        isAndroidWebViewStub.restore();
        isPrivateStub.restore();
    });
    it('do nothing if Android WebView', () => {
        isAndroidWebViewStub.returns(true);
        detectPrivateMode({} as any);
        chai.expect(isPrivateStub.called).to.be.not.ok;
    });
    it('do nothing if already set', () => {
        state.pri = true;
        detectPrivateMode({} as any);
        chai.expect(isPrivateStub.called).to.be.not.ok;
    });
    it('set value', () => {
        const value = true;
        isPrivateStub.returns(Promise.resolve(value));
        detectPrivateMode({} as any);
        return isPrivateStub().then(() => {
            chai.expect(state.pri).to.eq(value);
        });
    });
});

describe('private mode Utils', () => {
    const oldChromeWin = (isPrivateMode: boolean) =>
        ({
            webkitRequestFileSystem: (
                type: any,
                size: any,
                successCallback: () => {},
                errorCallback: () => {},
            ) => {
                isPrivateMode ? errorCallback() : successCallback();
            },
        } as any);
    const newChromeWin = (isPrivateMode: boolean) =>
        ({
            navigator: {
                userAgent: 'chrome',
                storage: {
                    estimate: () =>
                        Promise.resolve({
                            quota: QUOTA_LIMIT + (isPrivateMode ? -1 : 1),
                        }),
                },
            },
            webkitRequestFileSystem: (
                type: any,
                size: any,
                successCallback: () => {},
            ) => {
                successCallback();
            },
        } as any);
    const ffWin = (isPrivateMode = false) =>
        ({
            navigator: {
                serviceWorker: !isPrivateMode || undefined,
            },
        } as any);
    const safariWin = (isPrivateMode = false) =>
        ({
            openDatabase: () => {
                if (isPrivateMode) {
                    throw new Error();
                }
            },
        } as any);
    const ieWin = (isPrivateMode = false) =>
        ({
            indexedDB: !isPrivateMode || undefined,
            PointerEvent: true,
            MSPointerEvent: true,
        } as any);

    let isAndroidStub: any;
    let isFFStub: any;
    let isSafariStub: any;
    beforeEach(() => {
        isAndroidStub = sinon.stub(browser, 'isAndroid').returns(false);
    });
    afterEach(() => {
        isAndroidStub.restore();
        isFFStub && isFFStub.restore();
        isSafariStub && isSafariStub.restore();
    });
    const createPrivateTest = (
        title: string,
        winConstruct: (isPrivateValue: boolean) => any,
        before: () => void = () => {},
    ) =>
        it(title, () => {
            before();
            return Promise.all([
                isPrivate(winConstruct(false)).then((result) => {
                    chai.expect(result).to.be.false;
                }),
                isPrivate(winConstruct(true)).then((result) => {
                    chai.expect(result).to.be.true;
                }),
            ]);
        });
    createPrivateTest(
        'should detect incognito mode in chrome < 74',
        oldChromeWin,
    );
    createPrivateTest(
        'should detect incognito mode in chrome >=74',
        newChromeWin,
    );
    createPrivateTest('should detect incognito mode in ff', ffWin, () => {
        isFFStub = sinon.stub(browser, 'isFF').returns(true);
    });
    createPrivateTest(
        'should detect incognito mode in safari',
        safariWin,
        () => {
            isSafariStub = sinon.stub(browser, 'isSafari').returns(true);
        },
    );
    createPrivateTest('should detect incognito mode in ie10+ & edge', ieWin);
});
