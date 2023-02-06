import { expect } from 'chai';
import sinon, { assert, match } from 'sinon';
import { mix } from '@src/utils/object';
import { SenderInfo } from '@src/sender/SenderInfo';
import { WATCH_REFERER_PARAM, WATCH_URL_PARAM } from '@src/sender/watch';
import * as locationUtils from '@src/utils/location';
import * as domUtils from '@src/utils/dom';
import * as getCountersUtils from '@src/providers/getCounters';
import * as errorLoggerUtils from '@src/utils/errorLogger';
import * as debugConsoleUtils from '@src/providers/debugConsole';
import * as senderUtils from '@src/sender';
import * as hidUtils from '@src/middleware/watchSyncFlags/brinfoFlags/hid';
import { syncPromise } from '@src/__tests__/utils/syncPromise';
import { CounterOptions } from '@src/utils/counterOptions';
import {
    sendClickLink,
    handleClickEventRaw,
    setShouldTrack,
    useClicksProviderRaw,
    addFileExtensionFn,
} from '../clicks';
import { IS_DONWLOAD_BR_KEY, IS_EXTERNAL_LINK_BR_KEY } from '../const';
import { SendOptions } from '../types';

describe('clicks.ts', () => {
    const { any } = match;
    // todo убрать window?
    const win = window;
    const currentLocationHostname = 'my-site.ru';
    const currentLocationHref = `https://${currentLocationHostname}/path?a=1`;
    const counterOptions: CounterOptions = {
        id: 123,
        counterType: '0',
    };
    const url = 'some-url';
    const title = 'This is title';
    const params = {
        param: 'wop-wop',
    };

    describe('sendClickLink', () => {
        const sandbox = sinon.createSandbox();
        let senderSpy: sinon.SinonSpy;
        let callbackSpy: sinon.SinonSpy;
        let getLoggerFn: sinon.SinonStub;

        beforeEach(() => {
            senderSpy = sinon.fake.returns(syncPromise);
            callbackSpy = sinon.fake();
            getLoggerFn = sandbox.stub(debugConsoleUtils, 'getLoggerFn');

            sandbox.stub(locationUtils, 'getLocation').returns({
                href: currentLocationHref,
                hostname: currentLocationHostname,
            } as any);
        });

        afterEach(() => {
            sandbox.restore();
        });

        it('add file extention list and just string', () => {
            const mut: string[] = [];
            addFileExtensionFn(mut)('a');
            expect(mut).to.be.deep.eq(['a']);
            const mut2: string[] = ['0'];
            addFileExtensionFn(mut2)(['a', 'b']);
            expect(mut2).to.be.deep.eq(['0', 'a', 'b']);
        });

        it('properly sets browserInfo', () => {
            sendClickLink(win, counterOptions, {
                url,
                title,
                params,
                isExternalLink: true,
                isDownload: true,
                sender: senderSpy,
            });

            assert.calledOnce(senderSpy);
            assert.calledWith(
                senderSpy,
                match(
                    ({ brInfo }: any) =>
                        brInfo.getVal(IS_EXTERNAL_LINK_BR_KEY) === '1',
                ),
            );
            assert.calledWith(
                senderSpy,
                match(
                    ({ brInfo }: any) =>
                        brInfo.getVal(IS_DONWLOAD_BR_KEY) === '1',
                ),
            );
        });

        it('properly sets params', () => {
            sendClickLink(win, counterOptions, {
                url,
                title,
                params,
                noIndex: true,
                sender: senderSpy,
            });

            const spyCall = senderSpy.getCall(0);
            const senderOptions: SenderInfo = spyCall.args[0];

            delete senderOptions.brInfo;

            assert.calledOnce(senderSpy);
            expect(senderOptions).to.deep.equal({
                title,
                params,
                noIndex: true,
                urlParams: {
                    [WATCH_URL_PARAM]: url,
                    [WATCH_REFERER_PARAM]: currentLocationHref,
                },
            });
        });

        it('respects forceUrl', () => {
            const forceUrl = 'https://yandex.ru/maps';
            const counterOptionsForce = mix({}, counterOptions, {
                forceUrl,
            });

            sendClickLink(win, counterOptionsForce, {
                url,
                title,
                params,
                noIndex: true,
                sender: senderSpy,
            });

            const spyCall = senderSpy.getCall(0);

            assert.calledWith(
                spyCall,
                match.hasNested(`urlParams.${WATCH_REFERER_PARAM}`, forceUrl),
            );
        });

        it('calls callback', () => {
            sendClickLink(win, counterOptions, {
                url,
                sender: senderSpy,
                callback: callbackSpy,
                ctx: 'hey',
            });

            assert.calledOnce(callbackSpy);
            assert.calledOn(callbackSpy, 'hey');
        });

        describe('calls getLoggerFn with propper message', () => {
            const defaultOptions: Partial<SendOptions> = {
                url,
                isDownload: false,
                isExternalLink: false,
                ctx: 'hey',
            };

            const assertGetLoggerFnCall = (
                message: string,
                options: SendOptions,
            ) => {
                assert.calledOnce(getLoggerFn);
                assert.calledWith(
                    getLoggerFn,
                    win,
                    counterOptions,
                    message,
                    options,
                );
            };

            beforeEach(() => {
                defaultOptions.sender = senderSpy;
                defaultOptions.callback = callbackSpy;
            });

            it('for a local download link', () => {
                const options = {
                    ...defaultOptions,
                    isDownload: true,
                } as SendOptions;
                const message = `File. Counter ${counterOptions.id}. Url: ${options.url}`;

                sendClickLink(win, counterOptions, options);

                assertGetLoggerFnCall(message, options);
            });

            it('for an external download link', () => {
                const options = {
                    ...defaultOptions,
                    isDownload: true,
                    isExternalLink: true,
                } as SendOptions;
                const message = `Ext link - File. Counter ${counterOptions.id}. Url: ${options.url}`;

                sendClickLink(win, counterOptions, options);

                assertGetLoggerFnCall(message, options);
            });

            it('for an external link', () => {
                const options = {
                    ...defaultOptions,
                    isExternalLink: true,
                } as SendOptions;
                const message = `Ext link. Counter ${counterOptions.id}. Url: ${options.url}`;

                sendClickLink(win, counterOptions, options);

                assertGetLoggerFnCall(message, options);
            });
        });
    });

    describe('handleClickEvent', () => {
        const sandbox = sinon.createSandbox();

        let senderSpy: sinon.SinonSpy;
        let globalStorageSpy: Record<string, sinon.SinonStub>;
        let localStorageSpy: Record<string, sinon.SinonStub>;
        let stubs: Record<string, sinon.SinonStub>;

        beforeEach(() => {
            senderSpy = sinon.fake.returns(syncPromise);
            globalStorageSpy = {
                getVal: sandbox.stub(),
                setVal: sandbox.stub(),
            };
            localStorageSpy = {
                getVal: sandbox.stub(),
                setVal: sandbox.stub(),
            };
            stubs = {
                getTargetLink: sandbox.stub(domUtils, 'getTargetLink'),
                isSameDomain: sandbox.stub(locationUtils, 'isSameDomain'),
                textFromLink: sandbox.stub(domUtils, 'textFromLink'),
            };
        });

        afterEach(() => {
            sandbox.restore();
        });

        it('respects ym-disable-tracklink', () => {
            stubs.getTargetLink.returns({
                className: 'link1 ym-disable-tracklink link2',
            });

            handleClickEventRaw(
                {
                    ctx: win,
                    counterOptions,
                    hitId: 123,
                    sender: senderSpy,
                    globalStorage: globalStorageSpy as any,
                    counterLocalStorage: localStorageSpy as any,
                    fileExtensions: [],
                    trackLinksEnabled: () => true,
                },
                {} as any,
            );

            assert.notCalled(senderSpy);
        });

        it('respects ym-external-link', () => {
            stubs.getTargetLink.returns({
                className: 'link1 ym-external-link link2',
                href: currentLocationHref,
                hostname: currentLocationHostname,
            });
            stubs.textFromLink.returns('click me');

            handleClickEventRaw(
                {
                    ctx: win,
                    counterOptions,
                    hitId: 123,
                    sender: senderSpy,
                    globalStorage: globalStorageSpy as any,
                    counterLocalStorage: localStorageSpy as any,
                    fileExtensions: [],
                    trackLinksEnabled: () => true,
                },
                {} as any,
            );

            const spyCall = senderSpy.getCall(0);

            assert.calledOnce(senderSpy);
            assert.calledWith(
                spyCall,
                match(
                    ({ brInfo }: any) =>
                        brInfo.getVal(IS_EXTERNAL_LINK_BR_KEY) === '1',
                ),
            );
            assert.calledWith(
                spyCall,
                match.hasNested(
                    `urlParams.${WATCH_URL_PARAM}`,
                    currentLocationHref,
                ),
            );
            assert.calledWith(spyCall, match.has('title', 'click me'));
        });

        it('saves link text to storage', () => {
            stubs.getTargetLink.returns({
                className: 'link',
                href: currentLocationHref,
                hostname: currentLocationHostname,
                innerHTML: 'click me',
            });
            stubs.textFromLink.returns('click me');
            stubs.isSameDomain.returns(true);

            globalStorageSpy.getVal.returns(() => '');

            handleClickEventRaw(
                {
                    ctx: win,
                    counterOptions,
                    hitId: 123,
                    sender: senderSpy,
                    globalStorage: globalStorageSpy as any,
                    counterLocalStorage: localStorageSpy as any,
                    fileExtensions: [],
                    trackLinksEnabled: () => true,
                },
                {} as any,
            );

            assert.calledWith(localStorageSpy.setVal.lastCall, any, 'click me');
        });

        it('handles internal download link', () => {
            const fileUrl = `https://${currentLocationHostname}/file.mp3`;
            stubs.getTargetLink.returns({
                className: 'link',
                href: fileUrl,
                hostname: currentLocationHostname,
            });
            stubs.isSameDomain.returns(true);

            handleClickEventRaw(
                {
                    ctx: win,
                    counterOptions,
                    hitId: 123,
                    sender: senderSpy,
                    globalStorage: globalStorageSpy as any,
                    counterLocalStorage: localStorageSpy as any,
                    fileExtensions: [],
                    trackLinksEnabled: () => true,
                },
                {} as any,
            );

            const spyCall = senderSpy.lastCall;

            assert.calledOnce(senderSpy);
            assert.calledWith(
                spyCall,
                match.hasNested(`urlParams.${WATCH_URL_PARAM}`, fileUrl),
            );
            assert.calledWith(
                spyCall,
                match(
                    ({ brInfo }: any) =>
                        !brInfo.getVal(IS_EXTERNAL_LINK_BR_KEY) &&
                        brInfo.getVal(IS_DONWLOAD_BR_KEY) === '1',
                ),
            );
        });

        it('handles external download link', () => {
            const fileUrl = `https://example.com/file.mp3`;
            stubs.getTargetLink.returns({
                className: 'link',
                href: fileUrl,
            });
            stubs.isSameDomain.returns(false);

            handleClickEventRaw(
                {
                    ctx: win,
                    counterOptions,
                    hitId: 123,
                    sender: senderSpy,
                    globalStorage: globalStorageSpy as any,
                    counterLocalStorage: localStorageSpy as any,
                    fileExtensions: [],
                    trackLinksEnabled: () => true,
                },
                {} as any,
            );

            const spyCall = senderSpy.lastCall;

            assert.calledOnce(senderSpy);
            assert.calledWith(
                spyCall,
                match.hasNested(`urlParams.${WATCH_URL_PARAM}`, fileUrl),
            );
            assert.calledWith(
                spyCall,
                match(
                    ({ brInfo }: any) =>
                        brInfo.getVal(IS_EXTERNAL_LINK_BR_KEY) === '1' &&
                        brInfo.getVal(IS_DONWLOAD_BR_KEY) === '1',
                ),
            );
        });

        it('ignores bad protocols', () => {
            stubs.getTargetLink.returns({
                className: 'link',
                href: 'data:eee',
            });
            stubs.isSameDomain.returns(false);

            handleClickEventRaw(
                {
                    ctx: win,
                    counterOptions,
                    hitId: 123,
                    sender: senderSpy,
                    globalStorage: globalStorageSpy as any,
                    counterLocalStorage: localStorageSpy as any,
                    fileExtensions: [],
                    trackLinksEnabled: () => true,
                },
                {} as any,
            );

            assert.notCalled(senderSpy);
        });

        it('should do nothing if trackLinks is disabled', () => {
            handleClickEventRaw(
                {
                    ctx: win,
                    counterOptions,
                    hitId: 123,
                    sender: senderSpy,
                    globalStorage: globalStorageSpy as any,
                    counterLocalStorage: localStorageSpy as any,
                    fileExtensions: [],
                    trackLinksEnabled: () => false,
                },
                {} as any,
            );
            expect(stubs.getTargetLink.notCalled).to.be.true;
        });
    });

    describe('trackLinks flag', () => {
        const sandbox = sinon.createSandbox();
        const ctxStub = {} as any;
        let counterStateStub: sinon.SinonStub;
        const verifyCounterStateCall = (
            callIndex: number,
            rawValue: any,
            expectedValue: any,
        ) => {
            const { args } = counterStateStub.getCall(callIndex);
            expect(
                args[0],
                `expected to return ${expectedValue} if the value is ${rawValue}`,
            ).to.deep.eq({
                trackLinks: expectedValue,
            });
            expect(args.length).to.eq(1);
        };

        beforeEach(() => {
            sandbox
                .stub(errorLoggerUtils, 'errorLogger')
                .callsFake(
                    (...args: unknown[]) => args[args.length - 1] as any,
                );
            counterStateStub = sandbox.stub();
            sandbox
                .stub(getCountersUtils, 'counterStateSetter')
                .returns(counterStateStub);
            sandbox.stub(senderUtils, 'getSender').returns((() => {}) as any);
            sandbox.stub(hidUtils, 'getHid').returns(1);
        });

        afterEach(() => {
            sandbox.restore();
        });

        it('should sets counter state correctly', () => {
            [
                [{}, true],
                [null, true],
                ['', true],
                ['dd', true],
                [12, false],
                [true, true],
                [false, false],
                [[], true],
                [() => {}, false],
                [NaN, false],
                [undefined, false],
            ].forEach(([rawParam, expected]: any[], i) => {
                setShouldTrack(counterStateStub as any, rawParam);
                verifyCounterStateCall(i, rawParam, expected);
            });
        });

        it('provider changes counter state based on counterOptions', () => {
            useClicksProviderRaw(ctxStub, {
                trackLinks: {},
            } as any);

            const { trackLinks } = useClicksProviderRaw(ctxStub, {
                trackLinks: false,
            } as any);

            verifyCounterStateCall(0, {}, true);
            expect(counterStateStub.getCalls().length).to.eq(1);

            trackLinks(true);
            verifyCounterStateCall(1, true, true);
            expect(counterStateStub.getCalls().length).to.eq(2);
        });
    });
});
