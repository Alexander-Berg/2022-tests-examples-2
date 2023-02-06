import * as chai from 'chai';
import * as sinon from 'sinon';
import type { CounterOptions } from '@src/utils/counterOptions';
import * as domUtils from '@src/utils/dom';
import type { Queryable } from '@src/utils/dom';
import * as localStorageUtils from '@src/storage/localStorage';
import type { LocalStorage } from '@src/storage/localStorage';
import * as defaultSenderUtils from '@src/sender/default';
import type { DefaultSenderResult } from '@src/sender/default';
import * as transportUtils from '@src/transport';
import type { TransportList } from '@src/transport';
import type { InternalSenderInfo } from '@src/sender/SenderInfo';
import type { TransportOptions } from '@src/transport/types';
import { encodeBase64, encodeUtf8 } from '@src/utils/decoder';
import { Provider } from '@src/providers/index';
import { useWatermarkProviderRaw } from '../watermark';
import * as watermarkUtils from '../watermark';
import { CODE_MATRIX, LOCAL_STORAGE_WATERMARK_KEY } from '../const';

describe('WatermarkProvider', () => {
    const sandbox = sinon.createSandbox();
    let localStorageMap: Record<string, unknown>;
    const localStorageStub: LocalStorage = {
        isBroken: false,
        getVal: <T>(name: string, defVal?: T) =>
            (localStorageMap[name] || defVal) as T,
        setVal<T>(name: string, val: T) {
            localStorageMap[name] = val;
            return this;
        },
        delVal(name: string) {
            delete localStorageMap[name];
            return this;
        },
    };
    let globalLocalStorageStub: sinon.SinonStub<
        [ctx: Window, nameSpace?: string | number, prefix?: string],
        LocalStorage
    >;
    let createStyleStub: sinon.SinonStub<[ctx: Window, uidData: string], void>;
    let drawStub: sinon.SinonStub<
        [ctx: Window, uid: number],
        string | undefined
    >;
    let getTransportListStub: sinon.SinonStub<
        [ctx: Window, provider?: Provider],
        TransportList
    >;
    let useDefaultSenderStub: sinon.SinonStub<
        [ctx: Window, transports: TransportList],
        (
            senderInfo: InternalSenderInfo,
            urls: string[],
            opt?: TransportOptions,
        ) => Promise<DefaultSenderResult>
    >;
    let defaultSenderStub: sinon.SinonStub<
        [
            senderInfo: InternalSenderInfo,
            urls: string[],
            opt?: TransportOptions,
        ],
        Promise<DefaultSenderResult>
    >;

    const win = {} as Window;
    const counterOptions = { id: 123 } as unknown as CounterOptions;
    const dataUrl = 'dataUrl';
    const uid = '1120000000000001';
    const passportResponse: DefaultSenderResult = {
        responseData: { default_uid: uid },
        urlIndex: 0,
    };
    const setPassportResponseUid = (newUid: string) => {
        (passportResponse.responseData as Record<string, unknown>)[
            'default_uid'
        ] = newUid;
    };

    beforeEach(() => {
        localStorageMap = {};
        setPassportResponseUid(uid);
        globalLocalStorageStub = sandbox
            .stub(localStorageUtils, 'globalLocalStorage')
            .returns(localStorageStub);
        createStyleStub = sandbox.stub(watermarkUtils, 'createStyle');
        getTransportListStub = sandbox.stub(transportUtils, 'getTransportList');
        useDefaultSenderStub = sandbox
            .stub(defaultSenderUtils, 'useDefaultSender')
            .returns(() => Promise.resolve(passportResponse));
        defaultSenderStub = sandbox
            .stub<
                [
                    senderInfo: InternalSenderInfo,
                    urls: string[],
                    opt?: TransportOptions,
                ],
                Promise<DefaultSenderResult>
            >()
            .resolves({
                responseData: { default_uid: uid },
                urlIndex: 0,
            });
        drawStub = sandbox.stub(watermarkUtils, 'draw');
    });

    afterEach(() => {
        sandbox.restore();
    });

    it('retrieves dataURL form localStorage and draws', async () => {
        localStorageMap[LOCAL_STORAGE_WATERMARK_KEY] = encodeBase64(
            encodeUtf8(dataUrl),
        );

        await useWatermarkProviderRaw(win, counterOptions);

        sinon.assert.calledOnce(globalLocalStorageStub);
        sinon.assert.calledOnceWithExactly(createStyleStub, win, dataUrl);
        sinon.assert.notCalled(useDefaultSenderStub);
        sinon.assert.notCalled(defaultSenderStub);
    });

    it('for empty localStorage key requests uid from passport', async () => {
        setPassportResponseUid('');

        await useWatermarkProviderRaw(win, counterOptions);

        sinon.assert.calledOnce(globalLocalStorageStub);
        sinon.assert.calledOnce(getTransportListStub);
        sinon.assert.calledOnce(useDefaultSenderStub);
        sinon.assert.notCalled(drawStub);
        sinon.assert.notCalled(createStyleStub);
    });

    it('draws on canvas', async () => {
        await useWatermarkProviderRaw(win, counterOptions);

        sinon.assert.calledOnce(drawStub);
        sinon.assert.notCalled(createStyleStub);
    });

    it('saves valid dataURL to localStorage', async () => {
        drawStub.returns(dataUrl);

        await useWatermarkProviderRaw(win, counterOptions);

        sinon.assert.notCalled(createStyleStub);
        chai.expect(localStorageMap[LOCAL_STORAGE_WATERMARK_KEY]).to.eq(
            encodeBase64(encodeUtf8(dataUrl)),
        );
    });

    describe('does nothing for invalid uid:', () => {
        it('too big', async () => {
            setPassportResponseUid('1130000000000000');
            await useWatermarkProviderRaw(win, counterOptions);
            sinon.assert.notCalled(drawStub);
        });

        it('too small', async () => {
            setPassportResponseUid('112000000000000');
            await useWatermarkProviderRaw(win, counterOptions);
            sinon.assert.notCalled(drawStub);
        });
    });
});

describe('WatermarkProvider / createStyle', () => {
    const uidData = 'dataURL';
    const { createStyle } = watermarkUtils;

    const styleElement = {} as HTMLStyleElement;
    const win = { document: { head: {} } } as Window;

    const sandbox = sinon.createSandbox();
    let makeElementStub: sinon.SinonStub<
        [
            ctx: Window,
            tag: string,
            parent?: HTMLElement,
            className?: string | undefined,
            attrs?: [string, string | number][] | undefined,
            namespace?: string,
        ],
        HTMLElement
    >;
    let selectOneStub: sinon.SinonStub<
        [selector: string, node: Queryable],
        Element | null
    >;
    let appendChildSpy: sinon.SinonSpy;

    beforeEach(() => {
        makeElementStub = sandbox
            .stub(domUtils, 'makeElement')
            .returns(styleElement);
        selectOneStub = sandbox
            .stub(domUtils, 'selectOne')
            .returns(styleElement);
        appendChildSpy = sandbox.spy();
        win.document.head.appendChild = appendChildSpy;
        styleElement.innerText = 'body { display: block; }';
    });

    afterEach(() => {
        sandbox.restore();
    });

    it('creates a new style element if none found', () => {
        selectOneStub.returns(null);

        createStyle(win, uidData);

        sinon.assert.calledOnceWithExactly(
            makeElementStub,
            win,
            'style',
            win.document.head,
        );
    });

    it('appends innerText of the style element', () => {
        createStyle(win, uidData);

        sinon.assert.notCalled(makeElementStub);
        sinon.assert.notCalled(appendChildSpy);
        chai.expect(styleElement.innerText).to.be.ok;
    });

    it('styles "body::after" for rendering', () => {
        createStyle(win, uidData);

        chai.expect(styleElement.innerText).to.contain(
            `\nbody.mail-Page-Body::after,body.yc-root_theme_light::after,body.b-page::after{content:'';background:url('dataURL');position:fixed;top:0;left:0;width:100%;height:100%;opacity:0.004;pointer-events:none;overflow:hidden;z-index:999999}`,
        );
    });
});

describe('WatermarkProvider / xorBits', () => {
    it('processes a number with XOR', () => {
        const { xorBits } = watermarkUtils;
        const results = [
            100, 500, 1000, 3000, 8000, 14000, 25000, 54000, 123500,
        ].map(xorBits);
        chai.expect(results).to.deep.eq([1, 0, 0, 1, 0, 1, 0, 0, 1]);
    });
});

describe('WatermarkProvider / draw', () => {
    const uid = 123456;
    const dataURL = 'dataURL';
    const canvasContextElement = {} as CanvasRenderingContext2D;
    const canvasElement = {} as HTMLCanvasElement;
    const win = {} as Window;

    const sandbox = sinon.createSandbox();
    let makeElementStub: sinon.SinonStub<
        [
            ctx: Window,
            tag: string,
            parent?: HTMLElement,
            className?: string | undefined,
            attrs?: [string, string | number][] | undefined,
            namespace?: string,
        ],
        HTMLElementTagNameMap[keyof HTMLElementTagNameMap]
    >;
    let getContextStub: sinon.SinonStub<
        Parameters<HTMLCanvasElement['getContext']>,
        ReturnType<HTMLCanvasElement['getContext']>
    >;
    let fillRectSpy: sinon.SinonSpy;
    let toDataURLStub: sinon.SinonStub<
        [type?: string | undefined, quality?: any],
        string
    >;

    const { draw } = watermarkUtils;
    const fillRectCallCount = CODE_MATRIX.length ** 2;

    beforeEach(() => {
        fillRectSpy = sandbox.spy();
        canvasContextElement.fillRect = fillRectSpy;

        getContextStub = sandbox
            .stub<
                Parameters<HTMLCanvasElement['getContext']>,
                ReturnType<HTMLCanvasElement['getContext']>
            >()
            .returns(canvasContextElement);
        toDataURLStub = sandbox
            .stub<[type?: string | undefined, quality?: any], string>()
            .returns(dataURL);
        canvasElement.getContext =
            getContextStub as HTMLCanvasElement['getContext'];
        canvasElement.toDataURL = toDataURLStub;
        makeElementStub = sandbox
            .stub(domUtils, 'makeElement')
            .returns(canvasElement);
    });

    afterEach(() => {
        sandbox.restore();
    });

    it('does nothing if 2D context not found on the created canvas', () => {
        getContextStub.returns(null);

        draw(win, uid);

        sinon.assert.calledOnce(makeElementStub);
        sinon.assert.calledOnce(getContextStub);
        sinon.assert.notCalled(fillRectSpy);
    });

    it('draws on canvas and returns dataUrl', () => {
        const result = draw(win, uid);

        sinon.assert.calledOnce(makeElementStub);
        sinon.assert.calledOnce(getContextStub);
        sinon.assert.callCount(fillRectSpy, fillRectCallCount);
        sinon.assert.calledOnce(toDataURLStub);
        chai.expect(result).to.eq(dataURL);
    });
});
